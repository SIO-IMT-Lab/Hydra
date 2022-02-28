# IMT-Hydra
Repository for the Scripps Institute of Oceanography IMT Lab's Hydra project. 

**WIP - Repo structure is not finalized**

Repository Structure:
- setup-scripts
- sensor-modules
- environment-validation
- to-dos

# ROADMAP
- [X] Adapt Imran's Test Suite to utilize OOP-BubbleCam Implementation
- [ ] Use Bubble Cam Implementation to Capture/Save Images
  - [ ] Determine byte threshold for "interesting" Bubble Cam images
  - [ ] Determine i/o speed for a completely full buffer
- [ ] Revise Bubble Cam Implementation Method Names/Inheritance Hierarchy
  - [ ] Determine list of all sensors that we can actually power on/off
- [ ] Implement Foam Cam
- [ ] Implement Whitecap Cam
  - [ ] Change event trigger to a timer
- [ ] Determine byte threshold for "interesting" images on Foam/Whitecap Cam
- [X] Create Class Hierarchy Diagram
- [X] Create State Transition Flowchart
- [X] Create Flowchart for sensors and add pseudocode
- [ ] Implement Sensor Module/Submodules
- [ ] Implement Comms Module
- [ ] Implement Power Module
  - Note: Include bidrectional comms support
- [ ] Implement Logging Module
