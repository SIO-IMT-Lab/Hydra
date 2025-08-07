import time
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
COMMON_DIR = CURRENT_DIR.parent / "common"
sys.path.append(str(CURRENT_DIR))
sys.path.append(str(COMMON_DIR))

from whitecapcam import WhiteCapCam
from state import State
import config


class StateMonitor:
    """Placeholder state monitor returning the current glider state."""

    def get_state(self) -> State:
        # In real deployment, this would query an external system
        return State.STORM


if __name__ == "__main__":
    cam = WhiteCapCam()
    monitor = StateMonitor()
    last_capture = 0.0

    while True:
        state = monitor.get_state()
        if state in (State.STORM, State.WAVEBREAK):
            elapsed = time.time() - last_capture
            if elapsed >= config.CAPTURE_INTERVAL:
                cam.capture()
                last_capture = time.time()
            time.sleep(1)
        else:
            cam.power_off()
            break
