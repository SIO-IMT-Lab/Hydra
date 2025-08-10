#!/bin/sh
# 
# Disables display upon startup, increases Linux USB memory, activates the conda environment, and runs the cSBC.py file
#
# Author: Imran Matin
# Email: imatin@ucsd.edu
#

# Turn of DSI-1 LP internal display
xrandr --output DSI-1 --off

# Increase memory for spinnaker camera
# sudo sh -c 'echo 1000 > /sys/module/usbcore/parameters/usbfs_memory_mb'

# activate conda environment
# . ~/anaconda3/etc/profile.d/conda.sh
# conda activate spinnaker_py37

# Run the camera acquisition
# NOTE: CHANGE REPO NAME BELOW
# cd /home/$USER/Desktop/[REPO]
# python cSBC.py