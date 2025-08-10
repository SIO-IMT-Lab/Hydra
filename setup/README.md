# Setup Documentation

This document provides instructions for setting up the LattePanda and configuring remote access.

## Ubuntu Desktop 18.04.4 LTS and Spinnaker 2.0.0.146 SDK Installation on LattePanda Steps

This is a guide to installing Ubuntu Desktop 18.04.4 LTS and Spinnaker 2.0.0.146 SDK onto your LattePanda. Note that in this guide, local computer refers to the computer that you use regularly and LattePanda will refer to your actual LattePanda.

NOTE: The LattePanda will not boot without an HDMI connection.

1. Please follow the guide [README_UBUNTU.md](README_UBUNTU.md) for instructions on how to install Ubuntu.

2. Please follow the guide [README_SPINNAKER.md](README_SPINNAKER.md) for instructions on how to install Spinnaker.

## Setting up Remote Access to LattePanda

Make sure the following software is installed before attempting remote access:

- RealVNC viewer

1. Press Win+R and type `cmd` in the box if `cmd` is not already there
2. Press Enter
3. In the terminal window, type `ssh -L 5901:localhost:5901 grant@192.168.100.1`
4. Press Enter
5. Enter the remote password (which should be the IMT lab password)
6. Press Enter
7. Repeat steps 1-6

By this point, you should have two terminal windows open (I'll call them Terminal A and Terminal B), with each saying `(spinnaker_py37) grant@IMTHydra01:~$`

8. In Terminal A, type `startx`
9. Press Enter
10. In Terminal B, type `x11vnc -auth guess -display :0 -forever -loop -noxdamage -repeat -rfbauth ~/.vnc/passwd`
11. Press Enter
12. Open RealVNC Viewer

**NOTE: Steps 12a and 12b only apply if you do not see an icon labeled `LattePanda_BubbleCam` on the home screen of RealVNC Viewer. Otherwise, skip to step 13**

12a. At the top of RealVNC Viewer, there is a box saying `Enter VNC address or search`. Click this box and type `192.168.100.1:5900`
12b. Press Enter

**NOTE: Step 13 is required regardless of whether you did steps 12a and 12b**
13. Double-click on the icon labeled `LattePanda_BubbleCam`