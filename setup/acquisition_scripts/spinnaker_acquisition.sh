#!/bin/sh
# 
# Wrapper that runs the Acquisition.py script provided by Spinnaker.
#
# Creates a new directory where the images captured by the script are stored.
#
# Author: Imran Matin
# Email: imatin@ucsd.edu
#

conda_env=spinnaker_py37

printf "This script will run the Spinnaker example python script to acquire images from the camera.\n"

# create the directory to store the images
rm -rf test_images
mkdir test_images
cd test_images

# activate the conda environment
. ~/anaconda3/etc/profile.d/conda.sh
conda activate ${conda_env}

# Run python script to acquire images
python ../Acquisition.py

printf "\nIf the camera could not start acquisition with error [-1010], run this command..."
printf "\n$ sudo sh -c 'echo 1000 > /sys/module/usbcore/parameters/usbfs_memory_mb'"
printf "\nYou must be in the conda environment to acquire images..."
printf "\nThe images have been acquired and can be found out test_images/. Thank you, goodbye.\n"
