#!/bin/sh
# 
# Installation script for creating the conda environment for Spinnaker with Python 3.7.
#
# Author: Imran Matin
# Email: imatin@ucsd.edu
#

# Environment name
env_name=spinnaker_py37

printf "This script will create a Python 3.7 environment for Spinnaker.\n"

# Allow for conda to be run
printf "\nActivate and test installation...\n"
. ~/.bashrc
conda list

# Update conda and Anaconda
printf "Update conda utility and Anaconda distribution...\n"
conda update conda -y && conda update anaconda -y

printf "\nCreate Python3.7 environment with the name ${env_name}...\n"
conda create --name ${env_name} python=3.7 -y

printf "\nView all available environments...\n"
conda info --envs

printf "\nConfirm Python3.7 is installed...\n"
python --version

printf "\nPlease activate new Python3.7 environment for Spinnaker...\n"
printf "\nYour new environment is created. Thank you, goodbye.\n"