# Sensor Modules

All code for interacting with the Hydra sensors lives here. Each subdirectory corresponds to a category of devices or supporting documentation.

- `cameras/` — camera driver implementations
- `c-sensors/` — "c" sensor modules (GPS, MET1, SITA, etc.)
- `compositions/` — higher level modules that combine sensors together
- `tests/` — test suites for the sensor code

## Documentation

Here are notes and tasks related to the sensor modules.

### Checking data before storage

When the bubble cam captures images, some images may not provide any
insightful information. Imagine there were no bubbles or foam. As the
Hydra has limited hard-disk storage, we only want to store relevant
data. During the data capturing process, we will implement a data
checking mechanism to ensure we don't waste any storage space on
non-meaningful data.

We can do so in a few ways

- Use ML/AI image detection
- Check filesize if above threshold

The latter option is likely more feasible and efficient.

Tasks:

- [ ] Capture many black images and look at average filesize
- [ ] Capture non-meaningful images in the wtaer and look at average
  filesize

### Remote SSH guide

Make sure you're connected to UCSD wifi. You can use Cisco AnyConnect.

#### Endpoints

- imtlab@hydratopsidecam.ucsd.edu (Latte Panda) - topside is foam/whitecap cam
- grant@hydrabubblecam.ucsd.edu (Latte Panda)
- pi@hydrapowercontrol.ucsd.edu (RPi) - for toggling power to SBCs remotely (I don't really use this one anymore)
- pi@hydrasupervisor.ucsd.edu (RPi)

#### Sample ssh for bubblecam

```
ssh -L 59000:localhost:5901 -C -N -l grant hydrabubblecam.ucsd.edu
```

Steps

- ssh into one a Latte Panda or Raspi
- Start vnc server in the SBC using `vncserver -localhost`
- In another terminal, use the ssh pattern described above
- Connect to localhost:5901 using a remote desktop ("screen sharing" for mac)

### Storing sensor data on Raspi (non cams)

- Store only essential information (time, measurement, ?)
- Compress files (lossless) after a certain size. When that gets full we'll move the glider state into LOW POWER and conclude the mission.
- Project how long it takes to fill up Raspi storage

Tasks:

- [ ] Napkin mask to see how much Raspi can hold
- [ ] Explore lossless compression techniques

### Sync system time using GPS

~GPS Dongle https://photobyte.org/raspberry-pi-stretch-gps-dongle-as-a-time-source-with-chrony-timedatectl/~

Tasks:

- ~[ ] Sync GPS with supervisor~
- ~[ ] Sync supervisor with Latte Pandas~
- ~[ ] Measure sync delay if below threshold of 1 second~
- [ ] Write SITA and MET1 logs with GPS 1pps
- [ ] Connect GPS to LattePandas and do the same with logs
