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

##Usage

The basic setting for the Cinema Player are set in the config/config.cfg file. The server section holds the information about the host (normaly 'localhost') and the port for the web access. The api sections defines the name for the http path for api calls (normaly 'api'), the subdirectories for the html files and the start directory the file manager starts at.

In the html subdirectory the index.html contains a standard player gui to access and play videos.

##Installation

Extract the cinema_player file to a directory. Make the cinema_player and start.sh files executable.

Edit the server section of the config/server.cfg file to select the host name and port for the webservice.

Edit the screens section of the config/player.cfg file to set the playing screen. Multiple entries make it possible to play parts of a video to multiple screens.
Edit the player section to define the master screen in multiple screen settings. If only one screen is defined, the master screen is equal with the defined screen.

###Dependencies

The Python library psutil has to be installed.
For hiding the cursor the program unclutter is used, which is found in the repository.

###Start

The Cinema Player can be started by calling the cinema_player file in the root directory. To activate the automatic mouse hiding, use the start.sh script instead. For automatic start add a startup entry calling the cinema_player file in the root directory.

