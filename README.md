# IMT-Hydra

This repository contains software for the Scripps Institution of Oceanography IMT Lab's Hydra project. The platform integrates multiple sensors and cameras running on single board computers (SBCs).

## Repository structure

- `sensor-modules/` – all sensor and camera code
- `experiment/` – prototype scripts exploring threading and pub/sub patterns
- `system-outline/` – architectural notes and diagrams

## Sensor-modules

- Inheritance implementation => ~/sensor-modules/cameras
- Composition implementation => ~/sensor-modules/compositions
- Tests for inheritance and composition => ~/sensor-modules/tests
- Implementation and testing docs => ~/sensor-modules/docs

## Remote SSH

1. Download Cisco AnyConnect
2. Connect to vpn.ucsd.edu and log in with your UCSD credentials
3. Use VSCode ssh or terminal ssh into appropriate sensors and passwords