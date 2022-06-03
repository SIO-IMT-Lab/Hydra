# IMT-Hydra

Repository for the Scripps Institute of Oceanography IMT Lab's Hydra project.

**WIP - Repo structure is not finalized**

Repository Structure:

- setup-scripts (TODO)
- sensor-modules
- experiment

### Expected Launch: February 2023

# Spring Quarter

## Week 2

Questions for meeting

- What times work best for undergrad meeting? _TBD_
- Can we just use the GPS to set system time of the SBCs? _Do we need 1pps and if so how would we use it? Log 1pps pulse with measurement logs and sync them up later. Find out how to connect GPS with Latte Pandas._
- What logging convention should we use (for cams, for SITA/MET1)? _Low data rate. Human readable. Serves as activity log for cameras._
- Recruiting: _Job posting. Share with student-orgs: ACM, Triton Robotics (tritonrobotics@ucsd.edu)._

- [x] GPS time logging for RPi
- [x] Implement cam Module (composition)

## Week 3

- [x] Implement logger module (concurrent to bubblecam)
- [x] Implement bubblecam module (compisition)

## Week 4

Questions for meeting

- What lockout time are we expecting? (currently averaging 3.3 seconds for 150-image write -- slow at the start) _30 seconds_
- For the buffer, is there a rate of capture that we want, or do we want every single frame (according to the cam fps)? _10fps for bubblecam/foamcam, 1 frame white cap cam_
- What size buffer do we want? (seconds into frames) _5 seconds back and 5 seconds forward, 100 frames total_
- What format do we want to write data in? (currently png) _no compression_
- Data validation to get rid of less interesting images

- [x] Test logger module
- [x] Test reimplementation of bubblecam (current functionality + data quality check)

## Week 5

Questions for meeting

- When camera is locked out, do we still want to capture images in the buffer?
- Will I be able to come into the lab next week?

- [x] Make fixes to bubblecam and test again
- [x] Devise more tests for edge cases

## Week 6

Points for meeting

- Bubblecam cannot ssh
- Other tests to consider
- Behrad software

## Week 10
- [ ] Finalize bubblecam
  - [x] Finish thread testing
  - [X] Refine logging format
  - [X] Refine pre-post wavebreak capture window
  - [ ] Capture real images
- [X] Reimplement foam and white cap cam
- [ ] Test reimplementation of foam and white cap cam

## Beyond
- [ ] Implement pub/sub for state between RPi (supervisor) and cams (Latte Pandas)
- [ ] GPS time logging for Latte Pandas
- [ ] Get MET1 feather working with the supervisor
- [ ] Test SITA and MET1
- [ ] Implement Power Module

## Other
- [ ] Onboard Behrad to software
- [ ] Job description for software
