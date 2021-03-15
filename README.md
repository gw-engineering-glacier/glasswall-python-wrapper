# Glasswall Python Wrapper
A high level Python wrapper for interfacing with Glasswall libraries.



## Getting Started
Install via pip:
```
pip install glasswall
```



## Prerequisites
* [Python >= 3.6](https://www.python.org/downloads/)



## Examples

<details open>
<summary>Loading a Glasswall Library</summary>

Currently the following libraries are supported:

* ArchiveManager
* Editor
* Rebuild
* SecurityTagging
* WordSearch

```py
import glasswall


editor = glasswall.Editor(library_path=r"C:\azure\sdk.editor\2.173")
```
```
>>> 2021-03-15 12:27:42.337 glasswall INFO     __init__                  Loaded Glasswall Editor version 2.173 from C:\azure\sdk.editor\2.173\windows-drop-no-kill-switch\glasswall_core2.dll
```

`library_path` can be a path to a directory or a path to a file. When a directory is specified all subdirectories are recursively searched for the library file with the latest creation time.
</details>

<details>
<summary>Logging</summary>

Logs are saved in the OS-specific temp directory and are also output to console with a default logging level of INFO. You can view the file path of the temp directory or the log file:
```py
import glasswall


print(glasswall._TEMPDIR)
print(glasswall.config.logging.log_file_path)
```
```
>>> C:\Users\ANGUSR~1\AppData\Local\Temp\glasswall
>>> C:\Users\ANGUSR~1\AppData\Local\Temp\glasswall\logs\2021-03-15 122826.txt
```

The logging level can be modified, for a list of levels see: https://docs.python.org/3/library/logging.html#logging-levels
```py
import logging

import glasswall

# Modify logging level for logs to the console
glasswall.config.logging.console.setLevel(logging.DEBUG)

# Modify logging level for logs to file
glasswall.config.logging.log.setLevel(logging.DEBUG)
```
</details>

<details>
<summary>Protecting a directory</summary>

If no content management policy is provided then the default `sanitise` all policy is used.
```py
import glasswall


editor = glasswall.Editor(library_path=r"C:\azure\sdk.editor\2.173")
editor.protect_directory(
    input_directory=r"C:\test_files",
    output_directory=r"C:\test_files_sanitised"
)
```

</details>


<details>
<summary>Protecting a directory with a customised content management policy</summary>

Using `glasswall.content_management.policies.Editor`:
```py
import glasswall


editor = glasswall.Editor(library_path=r"C:\azure\sdk.editor\2.173")
editor.protect_directory(
    input_directory=r"C:\test_files",
    output_directory=r"C:\test_files_sanitised",
    content_management_policy=glasswall.content_management.policies.Editor(
        config={
            "pptConfig": {
                "internal_hyperlinks": "allow",
                "macros": "disallow",
            },
            "wordConfig": {
                "internal_hyperlinks": "allow",
                "macros": "disallow",
            }
        }
    )
)
```

Using a custom `.xml` file:
```py
import glasswall


editor = glasswall.Editor(library_path=r"C:\azure\sdk.editor\2.173")
editor.protect_directory(
    input_directory=r"C:\test_files",
    output_directory=r"C:\test_files_sanitised",
    content_management_policy=r"C:\configs\config.xml"
)
```

</details>


## Built With
* [Python 3.6.8 64-bit](https://www.python.org/downloads/release/python-368/)