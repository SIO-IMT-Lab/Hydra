import json
from typing import Dict, List

import cv2

try:
    import PySpin
except Exception as exc:  # pragma: no cover - PySpin not installed
    raise SystemExit(f"PySpin library is required: {exc}")

try:
    from EasyPySpin import VideoCapture
except Exception as exc:  # pragma: no cover - EasyPySpin not available
    raise SystemExit(f"EasyPySpin library is required: {exc}")


def enumerate_cameras() -> List[str]:
    """Return a list of serial numbers for connected cameras."""
    system = PySpin.System.GetInstance()
    cam_list = system.GetCameras()
    serials: List[str] = []
    for i in range(cam_list.GetSize()):
        cam = cam_list.GetByIndex(i)
        serial = cam.TLDevice.DeviceSerialNumber.GetValue()
        serials.append(serial)
    cam_list.Clear()
    system.ReleaseInstance()
    return serials


def preview_camera(serial: str) -> None:
    """Show a preview window for the camera with ``serial``.

    Press the ``q`` key to close the preview and continue.
    """
    cap = VideoCapture(serial)
    if not cap or not cap.isOpened():
        print(f"Unable to open camera with serial {serial}")
        return
    window = f"Camera {serial}"
    print("Press 'q' to close the preview window.")
    while True:
        success, frame = cap.read()
        if not success:
            continue
        cv2.imshow(window, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyWindow(window)


def main() -> None:
    serials = enumerate_cameras()
    if not serials:
        print("No cameras detected.")
        return
    name_map: Dict[str, str] = {}
    for serial in serials:
        preview_camera(serial)
        name = input(f"Enter a name for camera {serial}: ")
        name_map[name] = serial
    print("\nCamera mapping:")
    for name, serial in name_map.items():
        print(f"{name}: {serial}")
    with open('camera_ids.json', 'w', encoding='utf-8') as file:
        json.dump(name_map, file, indent=2)
        print("Mapping written to camera_ids.json")


if __name__ == "__main__":
    main()
