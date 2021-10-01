

import os
import platform
import tempfile

__version__ = "0.2.9"

_OPERATING_SYSTEM = platform.system()
_PYTHON_VERSION = platform.python_version()
_ROOT = os.path.dirname(__file__)
_TEMPDIR = os.path.join(os.environ.get("AGENT_TEMPDIRECTORY", tempfile.gettempdir()), "glasswall")

from glasswall import config, content_management, determine_file_type, utils
from glasswall.libraries.archive_manager.archive_manager import ArchiveManager
from glasswall.libraries.editor.editor import Editor
from glasswall.libraries.rebuild.rebuild import Rebuild
from glasswall.libraries.security_tagging.security_tagging import SecurityTagging
from glasswall.libraries.word_search.word_search import WordSearch


class GwReturnObj:
    """ An object intended mostly for internal use that has different
    attributes depending on which library and functionality utilises it, such
    as `status`, `buffer`, and `buffer_bytes`
    """

    def __init__(self, **kwargs):
        [setattr(self, k, v) for k, v in kwargs.items()]
