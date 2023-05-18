#!/bin/bash

# List all block devices
lsblk --nodeps --output NAME,TYPE,MOUNTPOINT | grep 'disk$' | awk '{print "/dev/"$1,$NF}' | while read -r device mount_point; do
  # Check if the block device is a USB drive
  if udevadm info --query=property --name="$device" | grep -q 'ID_BUS=usb'; then
    echo "$device:$mount_point"
  fi
done
