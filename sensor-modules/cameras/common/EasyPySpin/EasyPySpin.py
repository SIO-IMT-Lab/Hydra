import cv2
import PySpin
from typing import Optional

# ---------- Global singletons ----------
_SPIN_SYSTEM = PySpin.System.GetInstance()
_SPIN_CAM_LIST = _SPIN_SYSTEM.GetCameras()

def spin_cleanup():
    """Call once at program exit (after all cameras are released)."""
    _SPIN_CAM_LIST.Clear()
    _SPIN_SYSTEM.ReleaseInstance()

def list_cameras():
    """Return [{index, serial, user_id}] for discovery."""
    out = []
    for i in range(_SPIN_CAM_LIST.GetSize()):
        cam = _SPIN_CAM_LIST.GetByIndex(i)
        cam.Init()
        serial = cam.DeviceSerialNumber.ToString() if cam.DeviceSerialNumber.IsReadable() else ""
        user_id = cam.DeviceUserID.ToString() if cam.DeviceUserID.IsReadable() else ""
        out.append({"index": i, "serial": serial, "user_id": user_id})
        cam.DeInit()
    return out

def _get_by_user_id(user_id: str):
    for i in range(_SPIN_CAM_LIST.GetSize()):
        cam = _SPIN_CAM_LIST.GetByIndex(i)
        cam.Init()
        uid = cam.DeviceUserID.ToString() if cam.DeviceUserID.IsReadable() else ""
        cam.DeInit()
        if uid == user_id:
            return _SPIN_CAM_LIST.GetByIndex(i)
    raise RuntimeError(f"Camera with DeviceUserID='{user_id}' not found")

# ---------- Capture class ----------
class VideoCapture:
    """
    Open a FLIR camera for video capturing (safe for multiple concurrent instances).
    Open by: serial (str), user_id (str, with by='user_id'), or index (int).
    """

    def __init__(self, device, by: str = "serial"):
        """
        device: str (serial or user_id) or int (index)
        by:     'serial' | 'user_id' | 'index'
        """
        self._system = _SPIN_SYSTEM
        self._cam_list = _SPIN_CAM_LIST
        self.cam: Optional[PySpin.CameraPtr] = None
        self._streaming = False

        # Resolve camera handle
        try:
            if isinstance(device, int) or by == "index":
                self.cam = self._cam_list.GetByIndex(int(device))
            elif by == "user_id":
                self.cam = _get_by_user_id(str(device))
            else:  # default: serial
                self.cam = self._cam_list.GetBySerial(str(device))
        except Exception as e:
            raise RuntimeError(f"Failed to get camera handle: {e}")

        # Init + basic node setup
        try:
            self.cam.Init()
            # Continuous
            self.cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
            # Stream buffer policy: NewestOnly
            s_node_map = self.cam.GetTLStreamNodeMap()
            handling_mode = PySpin.CEnumerationPtr(s_node_map.GetNode("StreamBufferHandlingMode"))
            handling_mode_entry = handling_mode.GetEntryByName("NewestOnly")
            handling_mode.SetIntValue(handling_mode_entry.GetValue())
        except Exception as e:
            # Ensure clean state if init failed
            try:
                self.cam.DeInit()
            except:
                pass
            raise RuntimeError(f"Camera initialization failed: {e}")

    # --- lifecycle ---
    def start(self):
        if not self._streaming:
            self.cam.BeginAcquisition()
            self._streaming = True

    def stop(self):
        if self._streaming and self.cam.IsStreaming():
            self.cam.EndAcquisition()
        self._streaming = False

    def release(self):
        """Stop and deinit this camera (does NOT release the global system)."""
        try:
            self.stop()
            if self.cam:
                self.cam.DeInit()
        except:
            pass
        finally:
            self.cam = None

    def __del__(self):
        # Best effort; do NOT touch global system here
        try:
            self.release()
        except:
            pass

    def isOpened(self) -> bool:
        try:
            return self.cam is not None and self.cam.IsValid()
        except:
            return False

    # --- IO ---
    def read(self, timeout_ms: int = 1000):
        """
        Returns (ok, frame). Add a timeout to avoid hangs when shutting down.
        """
        if not self._streaming:
            self.start()

        try:
            image = self.cam.GetNextImage(timeout_ms)
        except PySpin.SpinnakerException:
            return False, None

        if image.IsIncomplete():
            image.Release()
            return False, None

        frame = image.GetNDArray()
        image.Release()
        return True, frame

    # --- (optional) example setters you can extend ---
    def set_exposure_us(self, value: float):
        if value < 0:
            self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)
        else:
            self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
            mn, mx = self.cam.ExposureTime.GetMin(), self.cam.ExposureTime.GetMax()
            self.cam.ExposureTime.SetValue(max(mn, min(mx, value)))

    def set_gain_db(self, value: float):
        if value < 0:
            self.cam.GainAuto.SetValue(PySpin.GainAuto_Continuous)
        else:
            self.cam.GainAuto.SetValue(PySpin.GainAuto_Off)
            mn, mx = self.cam.Gain.GetMin(), self.cam.Gain.GetMax()
            self.cam.Gain.SetValue(max(mn, min(mx, value)))
