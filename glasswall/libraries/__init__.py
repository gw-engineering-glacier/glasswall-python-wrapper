

# Note, `dependencies` refers to the dependencies required to call
# ctypes.cdll.LoadLibrary on CentOS7 / Windows 10 and may not be indicative
# of the full dependencies for all functionality within a library.

os_info = {
    "Linux": {
        "archive_manager": {
            "file_name": "libglasswall.archive.manager.so",
            "dependencies": [],
        },
        "editor": {
            "file_name": "libglasswall_core2.so",
            "dependencies": [
                "libquazip.so.1",
            ],
        },
        "gwqtcli": {
            "file_name": "GWQtCLI",
            "dependencies": [],
        },
        "rebuild": {
            "file_name": "libglasswall.classic.so",
            "dependencies": [],
        },
        "security_tagging": {
            "file_name": "libgw_securtag.so",
            "dependencies": [
                "libicudata.so.56",
                "libicui18n.so.56",
                "libicuuc.so.56",
                "libQt5Core.so.5",
                "libQt5Multimedia.so.5",
                "libQt5XmlPatterns.so.5",
                "libquazip.so.1"
            ],
        },
        "word_search": {
            "file_name": "libglasswall.word.search.so",
            "dependencies": [],  # loading dependencies through ctypes doesn't help for word search, use LD_LIBRARY_PATH
        },
    },

    "Windows": {
        "archive_manager": {
            "file_name": "glasswall.archive.manager.dll",
            "dependencies": [],
        },
        "editor": {
            "file_name": "glasswall_core2.dll",
            "dependencies": [
                "Qt5Core.dll",
                "Qt5Xml.dll",
                "quazip.dll",
            ],
        },
        "gwqtcli": {
            "file_name": "GWQtCLI.exe",
            "dependencies": [],
        },
        "rebuild": {
            "file_name": "glasswall.classic.dll",
            "dependencies": [],
        },
        "security_tagging": {
            "file_name": "gw_securtag.dll",
            "dependencies": [
                "Qt5Core.dll",
                "Qt5Gui.dll",
                "Qt5Xml.dll",
                "Qt5XmlPatterns.dll",
                "Qt5Network.dll",
                "quazip.dll"
            ],
        },
        "word_search": {
            "file_name": "glasswall.word.search.dll",
            "dependencies": [],
        },
    },
}
