"""Camera helpers shared by the camera packages.

This package normally exposes :class:`VideoCapture` from the ``EasyPySpin``
module which depends on the FLIR ``PySpin`` bindings.  Those bindings are not
available in the lightweight test environment used for this kata.  Attempting to
import ``VideoCapture`` unconditionally therefore results in an import error
when the tests are collected.  To keep the public API stable while avoiding
failures when ``PySpin`` is missing we try to import ``VideoCapture`` and fall
back to a small stub which simply raises an informative ``ImportError`` when
instantiated.
"""

try:  # pragma: no cover - exercised implicitly during import
    from .EasyPySpin import VideoCapture  # type: ignore
except Exception:  # ModuleNotFoundError if PySpin is absent
    class VideoCapture:  # pragma: no cover - only used when PySpin isn't present
        """Fallback stub used when ``PySpin``/``EasyPySpin`` is unavailable."""

        def __init__(self, *_, **__):
            raise ImportError(
                "EasyPySpin/PySpin is required for VideoCapture but is not installed"
            )

# Expose ``EasyPySpin`` as a top-level module so ``import EasyPySpin`` works
# without requiring callers to know the package location.  This mirrors the
# behaviour of the real library which is typically installed as ``EasyPySpin``.
import sys as _sys
_sys.modules.setdefault("EasyPySpin", _sys.modules[__name__ + ".EasyPySpin"])

