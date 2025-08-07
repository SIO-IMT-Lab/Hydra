from unittest.mock import MagicMock
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
import whitecapcam.whitecapcam as whitecapcam


def test_capture_resets_and_retries(monkeypatch, tmp_path):
    """WhiteCapCam should reset and retry when a capture fails."""

    class DummyCam:
        def __init__(self, *args, **kwargs):
            # First call fails, second succeeds
            self.capture_image = MagicMock(side_effect=[(False, None), (True, "frame")])
            self.reset = MagicMock()
            self.power_off = MagicMock()

    # Replace the real Cam with our dummy implementation
    monkeypatch.setattr(whitecapcam, "Cam", DummyCam)

    # Stub out cv2.imwrite so no files are actually written
    monkeypatch.setattr(whitecapcam.cv2, "imwrite", MagicMock())

    cam = whitecapcam.WhiteCapCam()
    cam.config.IMG_DIR = tmp_path

    cam.capture()

    assert cam.cam.capture_image.call_count == 2
    assert cam.cam.reset.call_count == 1
    whitecapcam.cv2.imwrite.assert_called_once()

