"""Initialize supply chain platform src package with Windows DLL resolution."""
import os
import sys

_dll_cookie = None
if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
    torch_lib = os.path.join(sys.prefix, "Lib", "site-packages", "torch", "lib")
    if os.path.exists(torch_lib):
        try:
            _dll_cookie = os.add_dll_directory(torch_lib)
        except Exception:
            pass

# Import torch before pandas/numpy to avoid Windows OpenBLAS DLL initialization conflict
try:
    import torch
except Exception:
    pass
