# physics_games
Repo for testing small, physics based games, with education in mind. Written in python 3, using the pyglet library.
First attempt is asteroid_rage (working title)

# Installation
The simplest way to get the game running is to install the packages in requirements.txt.
NOTE: It is recommended to install these packages inside a virtual environment.

For example, using virtualenv, create a virtual environment called game_environment using the command:

virtualenv game_environment

then start your virtual environment using

source game_environment/bin/activate

To install packages easily, run

pip3 install -r requirements.txt

preferably inside your virtual environment. You are now ready to test the game.

# Usage
python3 asteroid_rage

This runs the game at 1920x1080 resolution.

# Controls
w - boost,
space - consume planet/star if in range,
a - rotate counterclockwise,  
d - rotate clockwise,
up/down - zoom out/in,
, (comma) - lower simulation time step,
. (period) - increase simulation time step.
