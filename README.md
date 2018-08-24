Cinema Player
==================

###This is a Python 2.7 library to offer a movie player for cinema style projections

It is based on the mplayer_control Python script from
Musikhin Andrey <melomansegfault __at__ gmail.com> 
using the [MPlayer](http://www.mplayerhq.hu/) control.

The library was tested in Linux Mint. The mplayer_control is tested on Ubuntu and Windows.

##Cinema Player

The Cinema Player is designed as a standalone video player with no on screen display.
It is controlled by a simple webinterface. For playback the mplayer is used, whitch is
based on the ffmpeg library and therefore can playback a vast variety of video formats.

The web control site is provided by the Python script, the html index.html File and JavaScript code
can be found in the html directory.

## Usage

The basic setting for the Cinema Player are set in the config/config.cfg file. The server section holds the information about the host (normaly 'localhost') and the port for the web access. The api sections defines the name for the http path for api calls (normaly 'api'), the subdirectories for the html files and the start directory the file manager starts at.

In the html subdirectory the index.html contains a standard player gui to access and play videos.