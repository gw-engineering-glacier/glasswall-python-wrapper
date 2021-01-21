

import ctypes
import logging
import os
import platform
from datetime import datetime

from glasswall import config, content_management
from glasswall.common import gw_utils
from glasswall.libraries.archive_manager.archive_manager import ArchiveManager
from glasswall.libraries.editor.editor import Editor
from glasswall.libraries.rebuild.rebuild import Rebuild
from glasswall.libraries.security_tagging.security_tagging import SecurityTagging
from glasswall.libraries.word_search.word_search import WordSearch

__version__ = "0.10.0"
_PYTHON_VERSION = platform.python_version()
_OPERATING_SYSTEM = platform.system()
_ROOT = os.path.dirname(__file__)

fmt = "%(asctime)s.%(msecs)03d %(name)-9s %(levelname)-8s %(funcName)-25s %(message)s"
# datefmt "2020-06-25 15:04:59"
datefmt = "%Y-%m-%d %H:%M:%S"
# log_filename "2020-06-25 150459.txt"
log_filename = os.path.join(os.path.dirname(__file__), "logs", f'{datetime.now().strftime("%Y-%m-%d %H%M%S")}.txt')
# Create log directory
os.makedirs(os.path.dirname(log_filename), exist_ok=True)

# Logging to file
logging.basicConfig(
    level=logging.DEBUG,
    format=fmt,
    datefmt=datefmt,
    filename=log_filename,
    filemode="w",
)
log = logging.getLogger("glasswall")

# Logging to console
console = logging.StreamHandler()
console.setLevel(logging.ERROR)
console.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
logging.getLogger("").addHandler(console)

# Don't display the Windows GPF dialog if the invoked program dies.
# https://stackoverflow.com/a/24131590
# Use by setting kwarg "creationflags" as int in subprocess.call(..., creationflags=int(os.environ["creationflags"])
if _OPERATING_SYSTEM == "Windows":
    SEM_NOGPFAULTERRORBOX = 0x0002  # From MSDN
    ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX)
    CREATE_NO_WINDOW = 0x08000000  # From Windows API
    os.environ["creationflags"] = str(CREATE_NO_WINDOW)
else:
    os.environ["creationflags"] = str(0)


class GwReturnObj:
    """ A Glasswall return object. """

    def __init__(self, **kwargs):
        [setattr(self, k, v) for k, v in kwargs.items()]
