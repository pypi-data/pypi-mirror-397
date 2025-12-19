import os, sys
from .agent import CartaAgent
from .config import CartaConfig
from .profile import Profile

# try:
#     from .ui import (
#         CartaLogin as CartaLoginUI,
#         CartaProfile as CartaProfileUI,
#         CartaWebLogin,
#     )
# except ImportError:
#     from warnings import warn
#     msg = "You appear to be running in a headless environment, e.g. Lambda, so " \
#           "UI components could not be imported. Any attempt to create a GUI " \
#           "will raise an Error. "
#     warn(msg)
#     class CartaLoginUI:
#         def __new__(cls, *args, **kwargs):
#             raise ImportError(msg)
    
#     class CartaProfileUI:
#         def __new__(cls, *args, **kwargs):
#             raise ImportError(msg)
        
#     class CartaWebLogin:
#         def __new__(cls, *args, **kwargs):
#             raise ImportError(msg)

def is_headless() -> bool:
    """Check if the current environment is headless."""
    # On Unix-like systems, DISPLAY must be set for GUI applications
    if sys.platform in ("linux", "linux2", "darwin"):  # Linux or macOS
        if not os.environ.get("DISPLAY"):
            return True

    # On Windows, we can check if a desktop session is available
    if sys.platform in ("win32", "cygwin"):
        try:
            import ctypes
            if not getattr(ctypes, "windll").user32.GetDesktopWindow():
                return True
        except Exception:
            return True

    return False

if is_headless():
    class HeadlessEnvironmentError(ImportError, RuntimeError):
        def __init__(self, msg: str | None=None):
            msg_ = msg or "You appear to be running in a headless environment, e.g. Lambda, so " \
                "UI components could not be imported. Any attempt to create a GUI " \
                "or other interactive element will raise an HeadlessEnvironmentError."
            super().__init__(msg_)

    class InvalidUI:
        def __new__(cls, *args, **kwargs):
            raise HeadlessEnvironmentError()
        
        @classmethod
        def login(cls, *args, **kwargs):
            raise HeadlessEnvironmentError()
    
    class CartaLoginUI(InvalidUI):
        pass
    
    class CartaProfileUI(InvalidUI):
        pass
        
    class CartaWebLogin(InvalidUI):
        pass
else:
    from .ui import (
        CartaLogin as CartaLoginUI, # type: ignore
        CartaProfile as CartaProfileUI, # type: ignore
        CartaWebLogin, # type: ignore
    )
