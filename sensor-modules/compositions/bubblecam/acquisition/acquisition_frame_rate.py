import PySpin
import os
import time
import subprocess

# Directory to save the images
output_dir = './'

# Run the Bash script
output = subprocess.check_output(['./usb_drives.sh'], universal_newlines=True)

# Process the output
usb_drives = {}
for line in output.splitlines():
    device, mount_point = line.split(':')
    usb_drives[device] = mount_point

# Print the USB drives and their mount points
for device, mount_point in usb_drives.items():
    print(f"Found USB Drive: {device}, Mount Point: {mount_point}")
    output_dir = mount_point + '/images'

# Create a system object
system = PySpin.System.GetInstance()

# Get the camera list
cam_list = system.GetCameras()

if cam_list.GetSize() == 0:
    print("No FLIR cameras found!")
    system.ReleaseInstance()
    exit()

# Get the first camera
cam = cam_list[0]

# Initialize the camera
cam.Init()

# Set the acquisition mode to continuous
cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)

# Set the desired frame rate (in Hz)
frame_rate = 10

# Set the frame rate
cam.AcquisitionFrameRateEnable.SetValue(True)
cam.AcquisitionFrameRate.SetValue(frame_rate)

# Start the acquisition
cam.BeginAcquisition()

# Create the directory to save the images
os.makedirs(output_dir, exist_ok=True)

# Capture images continuously
try:
    start_time = time.time()
    
    while True:
        if time.time() - start_time > 1/frame_rate:
            # Retrieve the next available image
            image_result = cam.GetNextImage()

            # Convert the image result to a numpy array for saving
            image_array = image_result.GetNDArray()

            # Generate a unique filename based on the current timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}.png"

            # Save the image
            image_path = os.path.join(output_dir, filename)
            PySpin.ImageResult.Save(image_result, image_path)

            # Release the image
            image_result.Release()

            # Reset the start time
            start_time = time.time()

        time.sleep(0.001)

except KeyboardInterrupt:
    # Stop the acquisition
    cam.EndAcquisition()

    # Deinitialize the camera
    cam.DeInit()

    # Release the camera
    del cam

    # Release the camera list
    cam_list.Clear()

    # Release the system instance
    system.ReleaseInstance()

    print("Stopped Acquisition")