![](https://github.com/filetrust/glasswall-python/actions/workflows/python-package.yml/badge.svg)

![](https://github.com/filetrust/glasswall-python/actions/workflows/python-publish.yml/badge.svg)

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

<details>
<summary>Loading a Glasswall library</summary>

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

### Archive Manager

<details>
<summary>Supported archive formats</summary>

```py

import glasswall

# Load the Glasswall Archive Manager library
am = glasswall.ArchiveManager(r"C:\path\to\your\library\sdk.archive.manager")

print(am.supported_archives)

>>> ['7z', 'rar', 'tar', 'zip']
```

</details>

<details>
<summary>Extraction - Unpacking an archive</summary>

```py
import glasswall

# Load the Glasswall Archive Manager library
am = glasswall.ArchiveManager(r"C:\path\to\your\library\sdk.archive.manager")

# Unpack the Nested_4_layers.zip archive to a new directory
am.unpack(
    input_file=r"C:\Users\AngusRoberts\Desktop\archives\nested\Nested_4_layers.zip",
    output_directory=r"C:\Users\AngusRoberts\Desktop\unpacked_archives\nested"
)
```
A new directory is created: `C:\Users\AngusRoberts\Desktop\unpacked_archives\nested\Nested_4_layers` containing the unpacked contents of the `Nested_4_layers` zip archive. Nested archives are recursively unpacked while maintaining the same directory structure. To disable recursive unpacking use the `recursive` arg:

```py
import glasswall

# Load the Glasswall Archive Manager library
am = glasswall.ArchiveManager(r"C:\path\to\your\library\sdk.archive.manager")

# Unpack the Nested_4_layers.zip archive to a new directory without recursing the archive.
am.unpack(
    input_file=r"C:\Users\AngusRoberts\Desktop\archives\nested\Nested_4_layers.zip",
    output_directory=r"C:\Users\AngusRoberts\Desktop\unpacked_archives\nested",
    recursive=False
)
```
Other useful arguments:
* `file_type` default None (use archive extension), force Glasswall to try to process archives as this format. 
* `include_file_type` default False, keep the archive format in the directory name when unpacking. e.g. when True `Nested_4_layers.zip` will be unpacked to a directory `Nested_4_layers.zip` instead of `Nested_4_layers`. This can be necessary when unpacking multiple same-named archives that have different archive formats.
* `raise_unsupported` default True, raise an error if the Glasswall library encounters an error.
* `delete_origin` default False, delete the `input_file` after it has been unpacked to `output_directory`.

</details>

<details>
<summary>Extraction - Unpacking a directory of archives</summary>

```py
import glasswall

# Load the Glasswall Archive Manager library
am = glasswall.ArchiveManager(r"C:\path\to\your\library\sdk.archive.manager")

# Recursively unpack all archives found in the `archives` directory
am.unpack_directory(
    input_directory=r"C:\Users\AngusRoberts\Desktop\archives",
    output_directory=r"C:\Users\AngusRoberts\Desktop\unpacked_archives"
)
```
The `unpack_directory` method shares the same optional arguments as `unpack`. See also: `Extraction - Unpacking an archive`


</details>

<details>
<summary>Compression - Packing a directory into an archive</summary>

```py
import glasswall

# Load the Glasswall Archive Manager library
am = glasswall.ArchiveManager(r"C:\path\to\your\library\sdk.archive.manager")

# Pack the `assorted_files` directory as zip to `assorted_files.zip`
am.pack_directory(
    input_directory=r"C:\Users\AngusRoberts\Desktop\assorted_files",
    output_directory=r"C:\Users\AngusRoberts\Desktop",
    file_type="zip",
)
```
Pack to multiple formats with ease:
```py
import glasswall

# Load the Glasswall Archive Manager library
am = glasswall.ArchiveManager(r"C:\path\to\your\library\sdk.archive.manager")

# Pack the `assorted_files` directory in each supported file format
for file_type in am.supported_archives:
    am.pack_directory(
        input_directory=r"C:\Users\AngusRoberts\Desktop\assorted_files",
        output_directory=fr"C:\Users\AngusRoberts\Desktop",
        file_type=file_type,
    )
```

</details>

## Built With
* [Python 3.6.8 64-bit](https://www.python.org/downloads/release/python-368/)