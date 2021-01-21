

import ctypes
import os

import glasswall

# Don't display the Windows GPF dialog if the invoked program dies.
# https://stackoverflow.com/a/24131590
# Use by setting kwarg "creationflags" as int in subprocess.call(..., creationflags=int(os.environ["creationflags"])
if glasswall._OPERATING_SYSTEM == "Windows":
    SEM_NOGPFAULTERRORBOX = 0x0002  # From MSDN
    ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX)
    CREATE_NO_WINDOW = 0x08000000  # From Windows API
    os.environ["creationflags"] = str(CREATE_NO_WINDOW)
else:
    os.environ["creationflags"] = str(0)
