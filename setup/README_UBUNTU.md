# Ubuntu Desktop 18.04.4 LTS Installation on LattePanda

This is a guide to installing Ubuntu Desktop 18.04.4 LTS onto your LattePanda. Note that in this guide, local computer refers to the computer that you use regularly and LattePanda will refer to your actual LattePanda.

### Prerequisites
* Have 16GB+ of free space on your local computer.
* Have a USB with 8GB+ space.
* USB Keyboard and USB Mouse.
* HDMI Cord.
* Ethernet cable
* Ethernet network connection.
* USB Wall Adapter with up to 2A Output and MicroUSB power cord.

## Section 1: Installing Ubuntu 18.04.4 LTS

### Section 1.1: Perform these steps on your local computer.
1. Download Ubuntu Desktop 18.04.4 LTS iso from Microsoft OneDrive.

2. Install BalenaEtcher for your local computer OS from this [link](https://www.balena.io/etcher/). It will be used to burn the Ubuntu .iso image onto the USB.

3. Insert your USB into your local computer. 

4. Open BalenaEtcher. Ignore the popup that occurs by pressing ignore if it shows up. Press *Select image* and locate the Ubuntu .iso that you downloaded in Step 1. Press *Select target* and locate the USB drive that you have inserted (It may be /dev/disk2 or the name of the disk, but confirm the size of the disk matches to make sure). Then select *Flash*.

    *  NOTE: If the USB does not show up when you select *Select Target*, you must erase and reformat the USB to FAT32 first. Once this is done, repeat Step 4.

    * NOTE: Once BalenaEtcher finishes with USB, an error about the USB may come up saying *"The disk you inserted was not readable by this computer."* Go ahead and ignore it by pressing ignore.

5. Remove the USB from your local computer.

### Section 1.2: Perform these steps on your LattePanda.
1. Insert your keyboard into the USB 2.0 port (black) and mouse into the USB 3.0 port (blue).

2. Insert the USB with Ubuntu into the USB 2.0 port (black).

3. Plug in your HDMI cord.

4. Plug in your Ethernet cable. 

5. Plug in the microUSB power cord. When plugged in, you should see the red LED indicator light up on the underside of the board. This means that the LattePanda is initializing. Wait patiently for a few seconds until the LED light goes out.

6. When the LED indicator turns off then begin this step. First press the power button once (top white button farther from the corner of the board) to turn on the LattePanda. You should see the LED indicator light up again.

7. Continually tap ESC upon boot up until you enter the BIOS. If you miss the BIOS screen and go into the current OS, shut down the computer by unplugging the power cord and repeat Steps 5 to 7.

8. Navigate to the *Boot* tab in the BIOS screen using your keyboard.

9. Navigate to the *Machine Status AC/Battery In* setting to disable the power buttons and allow for the LattePanda to boot automatically when provided power. Press enter and select the *Power On* option.

10. Navigate to the *Save & Exit* tab and select *Save Changes and Reset*. When the computer begins to restart continually tap ESC upon boot up until you enter the BIOS.

11. Navigate to the *Save & Exit* tab. Navigate to the *Boot Override* section below on the same tab, and select the name of your USB device (Example: UEFI: SanDisk Partition 1) to boot from the USB drive you inserted.

12. Select *Install Ubuntu*.
    * NOTE: Your mouse may be jittery or leave multiple copies on the screen. Currently, there is no solution for this.

13. Only the orange Ubuntu Desktop with the Beaver in the background will be displayed. This is because the LattePanda has an internal display. If you drag your mouse past the top left side of the monitor, the mouse will disappear. You must try to grab the installation window from the internal display and drag it onto your main monitor. Think of a virtual screen that contains the installation window and you need that window on your monitor.

14. Follow the On-Screen Instructions.
    * Welcome Page: Select English.
    * Keyboard Layout Page: Select English (US) for both.
    * Wireless Page: Select I don't want to connect to a network right now. (This page may or may not show up. If it does, then your ethernet may not be connected.)
    * Updates and Other Software Page: Select Normal Installation and Download updates.
    * Installation Type Page: Select Erase disk and install Ubuntu.
    * Write the changes to disks? Popup: Select Continue.
    * Where are you? Page: Enter Los Angeles.
    * Who are you? Page: Enter these credentials.
        * Your name: imt
        * Your computer's name: lattepanda
        * Pick a username: imt
        * Choose a password: Use the IMT Lab password
        * Confirm your password: Use the IMT Lab password
        * Select Log in automatically

15. When the installation is complete popup displays, select *Restart Now*. Remove the USB after you have clicked the button.

16. Please skip this step if the orange Ubuntu Desktop with the Beaver in the background is displayed.
    * If you did not select "login automatically", then either the current time on an orange background or a purple screen will appear. 
    * If the current time on an orange background appears, press the space bar once and that will bring up a purple screen. 
    * When the purple screen is displayed, you need to enter your password even though it may not show the prompt. Once the password is entered, the Desktop with an orange background and beaver will appear.

17. Press "CTRL-ALT-T" to open a terminal. If this does not open a terminal on your screen, then right click on the screen and select "Open Terminal".

18. Disable the second LattePanda output "DSI-1" by executing the following command in your terminal.
    ```
    xrandr --output DSI-1 --off
    ```

20. Close all pop ups that show up on the screen. For the popup that says next, just click next until it goes away.

21. Set up Ubuntu to automatically disable the LattePanda internal display upon startup. Begin by opening a terminal and running the following commands.
    ```
    # Install necessary Linux commands
    sudo apt install git curl vim -y
    # Move to the Desktop directory
    cd Desktop/
    # Clone this repo
    git clone <repo>
    ```
* Click the grid icon on the bottom left corner of the screen. Search for *Startup Applications* and open it. Select *Add* and enter the following:
    * Name: Startup Script
    * Command: Select Browse and select the file `~/Desktop/[repo_name]/installation_scripts/startup.sh`
    * Comment: Disables LattePanda internal display upon startup.
* Complete the step by pressing *Add*. Now whenever you reboot, the LattePanda internal display will be disabled automatically. You can now close the window.

22. In the terminal, and execute the following commands to update and upgrade the system. If it fails, that means the system is running other apt update processes. Please wait until those complete it may take around 5 minutes, so continue trying the command every minute.
    ```
    sudo apt update -y && sudo apt upgrade -y
    ```

23. In the terminal, and execute the following commands to enable SSH.
    ```
    sudo apt install openssh-server -y
    sudo systemctl enable ssh
    sudo systemctl status ssh # If you see `active (running)` then it is SSH is working. Press `q` to exit.
    sudo ufw allow ssh
    ```

24. Install TeamViewer by running the following commands below in the terminal.
    ```
    wget https://download.teamviewer.com/download/linux/teamviewer_amd64.deb
    sudo apt install ./teamviewer_amd64.deb -y
    ```

25. Reboot the computer to allow any other updates to take effect.
    ```
    sudo reboot
    ```

26. You have now completed the installation of Ubuntu!


## Extra Notes
* Follow links below to download Ubuntu Desktop 18.04.4 LTS installation files independently. Note, these links may lead to newer releases of the software and may cause issues during installation.
    * Download Ubuntu Desktop 18.04.4 LTS from this [link](https://releases.ubuntu.com/18.04.4/).
* How to reformat a USB on MacOS
    ```
    # list all disk partitions
    diskutil list

    # Usage
    diskutil eraseDisk <FILE_SYSTEM> <DISK_NAME> <DISK_IDENTIFIER>

    # Example
    diskutil eraseDisk FAT32 SANDISK_USB /dev/disk2
    ```
* Set up a static IP address for LattePanda. Follow [this guide](https://linuxize.com/post/how-to-configure-static-ip-address-on-ubuntu-18-04/). Please follow the section that says "Configuring Static IP address on Ubuntu Desktop" on the lower part of the page. Make sure to open the SETTINGS application and not the SYSTEM SETTINGS application.
    * Change the X in all of the IP addresses 192.168.X.Y to the value that is currently there for your IP Address (ip address can be found using `ip address`)
    * Change the Y in all of the IP addresses 192.168.X.Y to what you would like for this system
    * Below are what need to be customized when setting up you systems static IP if you are confused.
    ```
    IPv4 Method: Manual
    Address: 192.168.X.Y
    Netmask: 24
    Gateway: 192.168.X.1
    DNS: 8.8.8.8,1.1.1.1
    ```
* Other Notes
    * Explain BalenaEtcher USB Initialization error message, Section 1.1: Step 4
    * USB Drive name in BalenaEtcher is unclear Section 1.1: Step 4
    * LattePanda boot up process (buttons/timing), Section 1.2: Step 5-6
    * Changing Machine Status AC/Battery In to disable power buttons, Section 1.2: Step 9
    * USB Drive name in the BIOS is unclear Section 1.2: Step 11
    * Purple Login Screen, Section 1.2: Step 16
    * DSI-1 Second Display Section 1.2: Step 13, 16-18
    * Jittery Mouse, Section 1.2: Step 12