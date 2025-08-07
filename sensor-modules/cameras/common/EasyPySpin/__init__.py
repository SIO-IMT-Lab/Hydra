"""Export a ``VideoCapture`` class backed by FLIR's PySpin library.

The real implementation requires the proprietary ``PySpin`` package which is
not available in all environments.  Importing this package directly would raise
``ModuleNotFoundError`` during test collection.  To keep imports from this
module working we attempt to pull in the real implementation but fall back to a
stub that simply raises ``ImportError`` when used.
"""

try:  # pragma: no cover - exercised implicitly during import
    from .EasyPySpin import VideoCapture  # type: ignore
except Exception:  # pragma: no cover - PySpin not installed
    class VideoCapture:
        """Stub used when PySpin is unavailable."""

        def __init__(self, *_, **__):
            raise ImportError("PySpin is required for EasyPySpin.VideoCapture")

