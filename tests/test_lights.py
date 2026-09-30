# ****************************************************
# * Tests for the DMX house-light controller.
# *
# * GNU GENERAL PUBLIC LICENSE Version 3
# ****************************************************

import os
import socket
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "module"))

import lights


class RecordingOutput(object):

	name = "artnet"
	connected = True
	interval = 0.01

	def __init__(self):
		self.frames = []
		self.closed = False

	def send(self, values):
		self.frames.append(list(values))

	def close(self):
		self.closed = True
		self.connected = False


class PacketTests(unittest.TestCase):

	def test_parse_scene(self):

		self.assertEqual(lights.parse_scene("1:255, 2:0"), [(1, 255), (2, 0)])
		self.assertEqual(lights.parse_scene(""), [])
		self.assertEqual(lights.parse_scene(None), [])

	def test_parse_scene_rejects_bad_values(self):

		self.assertRaises(ValueError, lights.parse_scene, "0:10")
		self.assertRaises(ValueError, lights.parse_scene, "1:256")
		self.assertRaises(ValueError, lights.parse_scene, "nope")

	def test_artdmx_header(self):

		values = [0] * 512
		values[0] = 200
		values[255] = 7
		packet = lights.build_artdmx(0, values, sequence=1)

		self.assertEqual(packet[:8], b"Art-Net\x00")
		self.assertEqual(packet[8], 0x00)
		self.assertEqual(packet[9], 0x50)
		self.assertEqual(packet[11], 14)
		self.assertEqual(packet[12], 1)
		self.assertEqual(packet[14], 0)
		self.assertEqual(packet[15], 0)
		self.assertEqual(packet[16], 0x02)
		self.assertEqual(packet[17], 0x00)
		self.assertEqual(packet[18], 200)
		self.assertEqual(packet[18 + 255], 7)
		self.assertEqual(len(packet), 18 + 512)

	def test_artdmx_universe_is_split_into_subuni_and_net(self):

		packet = lights.build_artdmx(256, [0] * 512, sequence=1)
		self.assertEqual(packet[14], 0)
		self.assertEqual(packet[15], 1)

	def test_enttec_frame(self):

		values = [0] * 512
		values[0] = 10
		values[1] = 20
		packet = lights.build_enttec(values)

		self.assertEqual(packet[0], 0x7E)
		self.assertEqual(packet[1], 0x06)
		self.assertEqual(packet[2], 513 & 0xFF)
		self.assertEqual(packet[3], (513 >> 8) & 0xFF)
		self.assertEqual(packet[4], 0x00)
		self.assertEqual(packet[5], 10)
		self.assertEqual(packet[6], 20)
		self.assertEqual(packet[-1], 0xE7)
		self.assertEqual(len(packet), 4 + 513 + 1)


class FadeTests(unittest.TestCase):

	def test_stop_scene_is_applied_immediately_on_startup(self):

		output = RecordingOutput()
		controller = lights.Lights(
			enabled=True,
			play_scene=[(1, 0)],
			stop_scene=[(1, 255)],
			fade=2,
			output=output,
			start_thread=False,
		)

		frame = controller._step(0)
		self.assertEqual(frame[0], 255)
		self.assertEqual(controller.status()["scene"], "stop")
		controller.close()

	def test_play_fades_to_dark_and_idle_returns(self):

		controller = lights.Lights(
			enabled=True,
			play_scene=[(1, 0), (2, 10)],
			stop_scene=[(1, 255), (2, 200)],
			fade=1,
			output=RecordingOutput(),
			start_thread=False,
		)

		controller.play()
		mid = controller._step(0.5)
		self.assertEqual(mid[0], 128)
		self.assertEqual(mid[1], 105)

		done = controller._step(0.5)
		self.assertEqual(done[0], 0)
		self.assertEqual(done[1], 10)
		self.assertEqual(controller.status()["scene"], "play")

		controller.idle()
		back = controller._step(1)
		self.assertEqual(back[0], 255)
		self.assertEqual(back[1], 200)
		controller.close()

	def test_missing_enttec_device_does_not_raise(self):

		controller = lights.Lights(
			enabled=True,
			output_name="enttec",
			device="/tmp/no-such-dmx-device",
			play_scene=[(1, 0)],
			stop_scene=[(1, 255)],
			start_thread=True,
		)

		self.assertFalse(controller.connected())
		controller.play()
		controller.idle()
		controller.close()

	def test_disabled_controller_ignores_scenes(self):

		controller = lights.Lights(enabled=False, start_thread=False)
		controller.play()
		self.assertEqual(controller.status()["scene"], "stop")
		self.assertFalse(controller.status()["enabled"])
		controller.close()


class ArtNetSendTests(unittest.TestCase):

	def test_play_reaches_the_socket(self):

		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.bind(("127.0.0.1", 0))
		sock.settimeout(2)
		port = sock.getsockname()[1]

		controller = lights.Lights(
			enabled=True,
			output_name="artnet",
			host="127.0.0.1",
			port=port,
			universe=0,
			fade=0,
			play_scene=[(1, 0)],
			stop_scene=[(1, 255)],
			start_thread=True,
		)

		try:
			first = self._wait_for_channel(sock, 255)
			self.assertEqual(first[:8], b"Art-Net\x00")
			controller.play()
			self._wait_for_channel(sock, 0)
			self.assertEqual(controller.status()["scene"], "play")
		finally:
			controller.close()
			sock.close()

	def _wait_for_channel(self, sock, expected):

		deadline = time.time() + 2

		while time.time() < deadline:
			packet = sock.recvfrom(1024)[0]
			if packet[18] == expected:
				return packet

		self.fail("no Art-Net frame with channel 1 = %s" % expected)


class ConfigTests(unittest.TestCase):

	def test_from_config_reads_player_style_section(self):

		try:
			import configparser
			parser = configparser.ConfigParser()
		except ImportError:
			import ConfigParser
			parser = ConfigParser.ConfigParser()

		handle, path = tempfile.mkstemp(suffix=".cfg")
		os.close(handle)

		try:
			with open(path, "w") as cfg:
				cfg.write(
					"[lights]\n"
					"enabled = False\n"
					"output = artnet\n"
					"play = 1:0, 4:12\n"
					"stop = 1:255, 4:80\n"
					"fade = 1.5\n"
				)

			parser.read(path)
			controller = lights.Lights.from_config(parser)
			self.assertFalse(controller.enabled)
			self.assertEqual(controller.play_scene, [(1, 0), (4, 12)])
			self.assertEqual(controller.stop_scene, [(1, 255), (4, 80)])
			self.assertEqual(controller.fade, 1.5)
			controller.close()
		finally:
			os.remove(path)


if __name__ == "__main__":
	unittest.main()
