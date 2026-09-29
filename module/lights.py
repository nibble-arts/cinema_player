# ****************************************************
# * House lights for the Cinema Player.
# *
# * Sends DMX512 to an Enttec DMX USB Pro compatible
# * interface, or Art-Net (DMX over UDP) to a node.
# *
# * GNU GENERAL PUBLIC LICENSE Version 3
# *
# * @author    Thomas Winkler <thomas.winkler__at__iggmp.net>
# * @copyright 2018
# ****************************************************

import atexit
import os
import socket
import struct
import termios
import threading
import time


DMX_CHANNELS = 512
ARTNET_PORT = 6454
ENTTEC_BAUD = 57600
# Enttec Pro frames are ~520 bytes at 57600 baud (~90 ms). Stay under that.
ENTTEC_INTERVAL = 0.12
ARTNET_INTERVAL = 1.0 / 30.0


def parse_scene(text):
	"""Parse '1:255, 2:0' into a list of (channel, value). Channels are 1-based."""

	scene = []

	if text is None:
		return scene

	text = str(text).strip()

	if not text:
		return scene

	for part in text.split(","):

		part = part.strip()

		if not part:
			continue

		if ":" not in part:
			raise ValueError("DMX scene entry '%s' must be channel:value" % part)

		channel_text, value_text = part.split(":", 1)
		channel = int(channel_text.strip())
		value = int(value_text.strip())

		if channel < 1 or channel > DMX_CHANNELS:
			raise ValueError("DMX channel %s is outside 1-%s" % (channel, DMX_CHANNELS))

		if value < 0 or value > 255:
			raise ValueError("DMX value %s is outside 0-255" % value)

		scene.append((channel, value))

	return scene


def _as_bytes(values):
	return bytes(bytearray(values))


def _level(value):

	if value <= 0:
		return 0

	if value >= 255:
		return 255

	return int(value + 0.5)


def build_artdmx(universe, values, sequence):
	"""Art-Net ArtDMX packet (OpCode 0x5000) for one universe."""

	if len(values) != DMX_CHANNELS:
		raise ValueError("Art-Net frame must contain %s channels" % DMX_CHANNELS)

	data = _as_bytes([_level(v) for v in values])
	length = len(data)

	# Art-Net length is even and big-endian. 512 is already even.
	header = struct.pack(
		"<8sHBBBBH",
		b"Art-Net\x00",
		0x5000,
		0,
		14,
		sequence & 0xFF,
		0,
		universe & 0x7FFF,
	)

	return header + struct.pack(">H", length) + data


def build_enttec(values):
	"""Enttec DMX USB Pro 'Output Only Send DMX Packet' (label 6)."""

	if len(values) != DMX_CHANNELS:
		raise ValueError("DMX frame must contain %s channels" % DMX_CHANNELS)

	# Start code 0x00 followed by the 512 channel slots.
	payload = b"\x00" + _as_bytes([_level(v) for v in values])
	return struct.pack("<BBH", 0x7E, 0x06, len(payload)) + payload + b"\xE7"


class NullOutput(object):

	name = "null"
	connected = False
	interval = ARTNET_INTERVAL

	def send(self, values):
		pass

	def close(self):
		pass


class ArtNetOutput(object):

	name = "artnet"
	interval = ARTNET_INTERVAL

	def __init__(self, host, port, universe):

		self.host = host
		self.port = int(port)
		self.universe = int(universe) & 0x7FFF
		self.sequence = 0
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		self.connected = True

	def send(self, values):

		self.sequence = (self.sequence % 255) + 1
		packet = build_artdmx(self.universe, values, self.sequence)
		self._sock.sendto(packet, (self.host, self.port))

	def close(self):

		self.connected = False

		try:
			self._sock.close()
		except Exception:
			pass


class EnttecOutput(object):

	name = "enttec"
	interval = ENTTEC_INTERVAL

	def __init__(self, device):

		self.device = device
		self.fd = None
		self.connected = False
		self.fd = os.open(device, os.O_RDWR | os.O_NOCTTY)
		attrs = termios.tcgetattr(self.fd)
		attrs[0] = 0
		attrs[1] = 0
		attrs[2] = termios.CS8 | termios.CREAD | termios.CLOCAL
		attrs[3] = 0
		attrs[4] = termios.B57600
		attrs[5] = termios.B57600
		attrs[6][termios.VMIN] = 0
		attrs[6][termios.VTIME] = 0
		termios.tcsetattr(self.fd, termios.TCSANOW, attrs)
		self.connected = True

	def send(self, values):

		packet = build_enttec(values)
		offset = 0

		while offset < len(packet):
			written = os.write(self.fd, packet[offset:])
			if written <= 0:
				raise IOError("short write on %s" % self.device)
			offset += written

	def close(self):

		self.connected = False

		if self.fd is None:
			return

		try:
			os.close(self.fd)
		except Exception:
			pass

		self.fd = None


def _open_output(output_name, host, port, universe, device):

	name = (output_name or "enttec").strip().lower()

	# "dmx" is the physical Enttec Pro link.
	if name == "dmx":
		name = "enttec"

	if name == "artnet":
		return ArtNetOutput(host, port, universe)

	if name == "enttec":

		try:
			return EnttecOutput(device)
		except Exception as exc:
			print("DMX interface %s not available: %s" % (device, exc))
			output = NullOutput()
			output.name = "enttec"
			return output

	raise ValueError("unknown DMX output '%s'" % output_name)


class Lights(object):
	"""Fade house lights between the play scene and the stop scene."""

	def __init__(self, enabled=False, output_name="enttec", host="255.255.255.255",
				 port=ARTNET_PORT, universe=0, device="/dev/ttyUSB0", fade=2.0,
				 play_scene=None, stop_scene=None, output=None, start_thread=True):

		self.enabled = bool(enabled)
		self.output_name = output_name or "enttec"
		self.fade = float(fade)
		self.play_scene = list(play_scene or [])
		self.stop_scene = list(stop_scene or [])
		self.scene = "stop"
		self.current = [0.0] * DMX_CHANNELS
		self.target = [0] * DMX_CHANNELS
		self._fade_from = [0.0] * DMX_CHANNELS
		self._fade_to = [0.0] * DMX_CHANNELS
		self._fade_pos = 1.0
		self._lock = threading.Lock()
		self._stop = threading.Event()
		self._thread = None
		self._error = False
		self._closed = False
		self.output = None

		if not self.enabled:
			self.output = NullOutput()
			return

		if output is not None:
			self.output = output
		else:

			try:
				self.output = _open_output(self.output_name, host, port, universe, device)
			except ValueError as exc:
				print("DMX configuration error: %s" % exc)
				self.enabled = False
				self.output = NullOutput()
				return

		self.output_name = self.output.name
		self._assign(self.stop_scene)
		self._begin_fade(snap=True)

		# Fade even when the interface could not be opened, so the
		# reported level still follows the scene.
		if start_thread:
			self._start()
			atexit.register(self.close)

	@classmethod
	def from_config(cls, config):

		if config is None or not config.has_section("lights"):
			return cls(enabled=False)

		def option(key, default):

			if config.has_option("lights", key):
				return config.get("lights", key)

			return default

		enabled = False

		if config.has_option("lights", "enabled"):
			enabled = config.getboolean("lights", "enabled")

		try:
			play_scene = parse_scene(option("play", "1:0"))
			stop_scene = parse_scene(option("stop", "1:255"))
			fade = float(option("fade", "2"))
			port = int(option("port", str(ARTNET_PORT)))
			universe = int(option("universe", "0"))
		except ValueError as exc:
			print("DMX configuration error: %s" % exc)
			return cls(enabled=False)

		return cls(
			enabled=enabled,
			output_name=option("output", "enttec"),
			host=option("host", "255.255.255.255"),
			port=port,
			universe=universe,
			device=option("device", "/dev/ttyUSB0"),
			fade=fade,
			play_scene=play_scene,
			stop_scene=stop_scene,
		)

	def connected(self):
		return bool(self.output and self.output.connected)

	def play(self):
		"""Film is running: fade to the play scene (typically dark)."""

		self._go(self.play_scene, "play")

	def idle(self):
		"""Playback stopped: fade to the stop scene (typically house lights on)."""

		self._go(self.stop_scene, "stop")

	def set_channel(self, channel, value):

		channel = int(channel)
		value = int(value)

		if channel < 1 or channel > DMX_CHANNELS:
			raise ValueError("DMX channel %s is outside 1-%s" % (channel, DMX_CHANNELS))

		if value < 0 or value > 255:
			raise ValueError("DMX value %s is outside 0-255" % value)

		with self._lock:
			self.target[channel - 1] = value
			self.scene = "custom"
			self._begin_fade(snap=(self.fade <= 0))

	def status(self):

		with self._lock:
			channels = {}

			for channel, _value in self.play_scene + self.stop_scene:
				channels[str(channel)] = _level(self.current[channel - 1])

			for index, value in enumerate(self.target):

				if value and str(index + 1) not in channels:
					channels[str(index + 1)] = _level(self.current[index])

			return {
				"enabled": self.enabled,
				"output": self.output_name,
				"connected": self.connected(),
				"scene": self.scene,
				"channels": channels,
			}

	def close(self):
		"""Bring the house lights back up and stop sending."""

		if self._closed:
			return

		self._closed = True
		self._stop.set()

		if self._thread is not None and self._thread is not threading.current_thread():
			self._thread.join(timeout=2)

		if not self.enabled or self.output is None:
			return

		with self._lock:
			self._assign(self.stop_scene)
			self.scene = "stop"
			self._begin_fade(snap=True)
			frame = [_level(v) for v in self.current]

		try:
			self.output.send(frame)
		except Exception as exc:
			print("DMX send failed: %s" % exc)

		self.output.close()

	def _go(self, scene, name):

		if not self.enabled:
			return

		with self._lock:
			self._assign(scene)
			self.scene = name
			self._begin_fade(snap=(self.fade <= 0))

	def _assign(self, scene):

		for channel, value in scene:
			self.target[channel - 1] = value

	def _begin_fade(self, snap=False):

		self._fade_to = [float(v) for v in self.target]

		if snap or self.fade <= 0:
			self.current = list(self._fade_to)
			self._fade_from = list(self._fade_to)
			self._fade_pos = 1.0
		else:
			self._fade_from = list(self.current)
			self._fade_pos = 0.0

	def _step(self, dt):
		"""Advance the fade by dt seconds and return the frame to send."""

		with self._lock:

			if self._fade_pos < 1.0 and self.fade > 0:
				self._fade_pos += float(dt) / self.fade

				if self._fade_pos >= 1.0:
					self._fade_pos = 1.0

			for index in range(DMX_CHANNELS):
				start = self._fade_from[index]
				end = self._fade_to[index]
				self.current[index] = start + (end - start) * self._fade_pos

			return [_level(v) for v in self.current]

	def _start(self):

		self._thread = threading.Thread(target=self._loop)
		self._thread.daemon = True
		self._thread.start()

	def _loop(self):

		last = time.time()

		while not self._stop.is_set():

			now = time.time()
			frame = self._step(now - last)
			last = now

			try:
				self.output.send(frame)
				self._error = False
			except Exception as exc:

				if not self._error:
					print("DMX send failed: %s" % exc)
					self._error = True

			elapsed = time.time() - now
			remain = self.output.interval - elapsed

			if remain > 0 and self._stop.wait(remain):
				break

