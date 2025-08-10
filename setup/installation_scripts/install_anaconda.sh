#!/bin/sh
# 
# Installation script for Anaconda.
#
# Author: Imran Matin
# Email: imatin@ucsd.edu
#

# Version of anaconda to install
anaconda_script=Anaconda3-2019.10-Linux-x86_64.sh

# URL to current anaconda install file, check if updated version released
anaconda_url=https://repo.anaconda.com/archive/${anaconda_script}

printf "This script will download and install Anaconda.\n"

printf "\nDownloading the installer script...\n"
cd /tmp
curl -O ${anaconda_url}

printf "\nConfirming integrity of installer...\n"
sha256sum ${anaconda_script}

printf "\nRunning installation script, accept all questions...\n"
sh ${anaconda_script}

printf "\nAnaconda is installed. Thank you, goodbye.\n"