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

- [Python >= 3.6](https://www.python.org/downloads/)

## Examples

<details>
<summary>Loading a Glasswall library</summary>

Each library is a subclass of the `glasswall.libraries.library.Library` class and can be accessed from the top level of the `glasswall` module. The following subclasses are available:

- ArchiveManager
- Editor
- Rebuild
- SecurityTagging
- WordSearch

Libraries are loaded on initialisation and have one required argument: `library_path` which can be the path to a file or a directory. If a directory is specified it is recursively searched and the library with the latest change time will be loaded.

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\azure\sdk.editor\2.173")
```

```
>>> 2021-03-15 12:27:42.337 glasswall INFO     __init__                  Loaded Glasswall Editor version 2.173 from C:\azure\sdk.editor\2.173\windows-drop-no-kill-switch\glasswall_core2.dll
```

</details>

<details>
<summary>Logging</summary>

Logs are saved to the temp directory and are also output to console with a default logging level of INFO. You can view the file path of the temp directory or the log file:

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
<summary>Content management policies</summary>

Subclasses of the `glasswall.content_management.policies.Policy` class can be used to easily create content management policies of varying complexity by passing the `default` and `config` keyword arguments. Subclasses include:

- ArchiveManager
- Editor
- Rebuild
- WordSearch

Some examples of content management policies are below.

<details>
<summary>Default sanitise all Editor policy</summary>

```xml
<?xml version="1.0" encoding="utf-8"?>
<config>
    <pdfConfig>
        <acroform>sanitise</acroform>
        <actions_all>sanitise</actions_all>
        <digital_signatures>sanitise</digital_signatures>
        <embedded_files>sanitise</embedded_files>
        <embedded_images>sanitise</embedded_images>
        <external_hyperlinks>sanitise</external_hyperlinks>
        <internal_hyperlinks>sanitise</internal_hyperlinks>
        <javascript>sanitise</javascript>
        <metadata>sanitise</metadata>
    </pdfConfig>
    <pptConfig>
        <embedded_files>sanitise</embedded_files>
        <embedded_images>sanitise</embedded_images>
        <external_hyperlinks>sanitise</external_hyperlinks>
        <internal_hyperlinks>sanitise</internal_hyperlinks>
        <javascript>sanitise</javascript>
        <macros>sanitise</macros>
        <metadata>sanitise</metadata>
        <review_comments>sanitise</review_comments>
    </pptConfig>
    <sysConfig>
        <interchange_pretty>false</interchange_pretty>
        <interchange_type>sisl</interchange_type>
    </sysConfig>
    <tiffConfig>
        <geotiff>sanitise</geotiff>
    </tiffConfig>
    <wordConfig>
        <dynamic_data_exchange>sanitise</dynamic_data_exchange>
        <embedded_files>sanitise</embedded_files>
        <embedded_images>sanitise</embedded_images>
        <external_hyperlinks>sanitise</external_hyperlinks>
        <internal_hyperlinks>sanitise</internal_hyperlinks>
        <macros>sanitise</macros>
        <metadata>sanitise</metadata>
        <review_comments>sanitise</review_comments>
    </wordConfig>
    <xlsConfig>
        <dynamic_data_exchange>sanitise</dynamic_data_exchange>
        <embedded_files>sanitise</embedded_files>
        <embedded_images>sanitise</embedded_images>
        <external_hyperlinks>sanitise</external_hyperlinks>
        <internal_hyperlinks>sanitise</internal_hyperlinks>
        <macros>sanitise</macros>
        <metadata>sanitise</metadata>
        <review_comments>sanitise</review_comments>
    </xlsConfig>
</config>
```

</details>

```py
import glasswall

# Print the default Editor content management policy
print(glasswall.content_management.policies.Editor())
```

<details>
<summary>Custom Rebuild policy</summary>

```xml
<?xml version="1.0" encoding="utf-8"?>
<config>
    <pdfConfig>
        <acroform>allow</acroform>
        <actions_all>allow</actions_all>
        <digital_signatures>allow</digital_signatures>
        <embedded_files>allow</embedded_files>
        <embedded_images>allow</embedded_images>
        <external_hyperlinks>allow</external_hyperlinks>
        <internal_hyperlinks>allow</internal_hyperlinks>
        <javascript>allow</javascript>
        <metadata>allow</metadata>
    </pdfConfig>
    <pptConfig>
        <embedded_files>allow</embedded_files>
        <embedded_images>allow</embedded_images>
        <external_hyperlinks>allow</external_hyperlinks>
        <internal_hyperlinks>allow</internal_hyperlinks>
        <javascript>allow</javascript>
        <macros>allow</macros>
        <metadata>allow</metadata>
        <review_comments>allow</review_comments>
    </pptConfig>
    <sysConfig>
        <default>allow</default>
        <interchange_pretty>false</interchange_pretty>
        <interchange_type>sisl</interchange_type>
    </sysConfig>
    <tiffConfig>
        <geotiff>allow</geotiff>
    </tiffConfig>
    <wordConfig>
        <dynamic_data_exchange>allow</dynamic_data_exchange>
        <embedded_files>allow</embedded_files>
        <embedded_images>allow</embedded_images>
        <external_hyperlinks>allow</external_hyperlinks>
        <internal_hyperlinks>allow</internal_hyperlinks>
        <macros>sanitise</macros>
        <metadata>allow</metadata>
        <review_comments>allow</review_comments>
    </wordConfig>
    <xlsConfig>
        <dynamic_data_exchange>allow</dynamic_data_exchange>
        <embedded_files>sanitise</embedded_files>
        <embedded_images>sanitise</embedded_images>
        <external_hyperlinks>allow</external_hyperlinks>
        <internal_hyperlinks>allow</internal_hyperlinks>
        <macros>allow</macros>
        <metadata>allow</metadata>
        <review_comments>allow</review_comments>
    </xlsConfig>
</config>
```

</details>

```py
import glasswall

# Print a custom Rebuild content management policy with a default of allow
# that only sanitises macros in wordConfig, and embedded images and files in
# xlsConfig
print(glasswall.content_management.policies.Rebuild(
    default="allow",
    config={
        "wordConfig": {
            "macros": "sanitise",
        },
        "xlsConfig": {
            "embedded_files": "sanitise",
            "embedded_images": "sanitise",
        },
    }
))
```

Any functionality that requires a content management policy will use its default content management policy if one has not been specified with the keyword argument `content_management_policy`.

</details>

### Editor

<details>
<summary>Protecting a file</summary>

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\azure\sdk.editor\2.173")

# Use the default sanitise all policy to sanitise a file, writing the sanitised
# file to a new directory
editor.protect_file(
    input_file=r"C:\test_files\InternalHyp_Review.doc",
    output_file=r"C:\test_files_sanitised\InternalHyp_Review.doc"
)
```

</details>

<details>
<summary>Protecting all files in a directory</summary>

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\azure\sdk.editor\2.173")

# Use the default sanitise all policy to protect a directory of files, writing
# the sanitised files to a new directory.
# NOTE: Passing `raise_unsupported=False` can be useful when working with a
# directory containing a mixture of supported and unsupported file types. By
# default this value is True, and an error will be raised on the first failure.
editor.protect_directory(
    input_directory=r"C:\test_files",
    output_directory=r"C:\test_files_sanitised"
)
```

</details>

<details>
<summary>Protecting all files in a directory using a custom content management policy</summary>

Using `glasswall.content_management.policies.Editor`:

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\azure\sdk.editor\2.173")

# Use a custom Editor policy to sanitise all files in the test_files directory
# and write them to the test_files_sanitised directory. Internal hyperlinks in
# ppt and word files will not be sanitised, and if macros are present then
# withhold the file
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


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\azure\sdk.editor\2.173")

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
am = glasswall.ArchiveManager(r"C:\azure\sdk.archive.manager")

print(am.supported_archives)

>>> ['7z', 'rar', 'tar', 'zip']
```

</details>

<details>
<summary>Protecting an archive</summary>

```py

import glasswall

# Load the Glasswall Archive Manager library
am = glasswall.ArchiveManager(r"C:\azure\sdk.archive.manager")

# Use the default Archive Manager policy: sanitise all, process all, writing
# the sanitised archive and the analysis report to different directories.
am.protect_archive(
    input_file=r"C:\archives\7Zip\0000192.doc.7z",
    output_file=r"C:\archives_sanitised\7Zip\0000192.doc.7z",
    output_report=r"C:\archives_reports\7Zip\0000192.doc.7z.xml"
)
```

</details>

<details>
<summary>Protecting all archives in a directory using a custom content management policy</summary>

```py

import glasswall

# Load the Glasswall Archive Manager library
am = glasswall.ArchiveManager(r"C:\azure\sdk.archive.manager")

# Use a custom Archive Manager policy: sanitise all, process all, but discard
# mp3 and mp4 files. Write the sanitised archives and the analysis reports to
# different directories
am.protect_directory(
    input_directory=r"C:\archives\7Zip",
    output_directory=r"C:\archives_sanitised\7Zip",
    output_report_directory=r"C:\archives_analysis_reports\7Zip",
    content_management_policy=glasswall.content_management.policies.ArchiveManager(
        default="sanitise",
        default_archive_manager="process",
        config={
            "archiveConfig": {
                "mp3": "discard",
                "mp4": "discard"
            }
        }
    ),
    raise_unsupported=False
)
```

</details>

<details>
<summary>Extraction - Unpacking an archive</summary>

```py
import glasswall

# Load the Glasswall Archive Manager library
am = glasswall.ArchiveManager(r"C:\azure\sdk.archive.manager")

# Unpack the Nested_4_layers.zip archive to a new directory
am.unpack(
    input_file=r"C:\archives\nested\Nested_4_layers.zip",
    output_directory=r"C:\unpacked_archives\nested"
)
```

A new directory is created: `C:\unpacked_archives\nested\Nested_4_layers` containing the unpacked contents of the `Nested_4_layers` zip archive. Nested archives are recursively unpacked while maintaining the same directory structure. To disable recursive unpacking use the `recursive` arg:

```py
import glasswall

# Load the Glasswall Archive Manager library
am = glasswall.ArchiveManager(r"C:\azure\sdk.archive.manager")

# Unpack the Nested_4_layers.zip archive to a new directory without recursing the archive.
am.unpack(
    input_file=r"C:\archives\nested\Nested_4_layers.zip",
    output_directory=r"C:\unpacked_archives\nested",
    recursive=False
)
```

Other useful arguments:

- `file_type` default None (use archive extension), force Glasswall to try to process archives as this format.
- `include_file_type` default False, keep the archive format in the directory name when unpacking. e.g. when True `Nested_4_layers.zip` will be unpacked to a directory `Nested_4_layers.zip` instead of `Nested_4_layers`. This can be necessary when unpacking multiple same-named archives that have different archive formats.
- `raise_unsupported` default True, raise an error if the Glasswall library encounters an error.
- `delete_origin` default False, delete the `input_file` after it has been unpacked to `output_directory`.

</details>

<details>
<summary>Extraction - Unpacking a directory of archives</summary>

```py
import glasswall

# Load the Glasswall Archive Manager library
am = glasswall.ArchiveManager(r"C:\azure\sdk.archive.manager")

# Recursively unpack all archives found in the `archives` directory
am.unpack_directory(
    input_directory=r"C:\archives",
    output_directory=r"C:\unpacked_archives"
)
```

The `unpack_directory` method shares the same optional arguments as `unpack`. See also: `Extraction - Unpacking an archive`

</details>

<details>
<summary>Compression - Packing a directory into an archive</summary>

```py
import glasswall

# Load the Glasswall Archive Manager library
am = glasswall.ArchiveManager(r"C:\azure\sdk.archive.manager")

# Pack the `assorted_files` directory as zip to `assorted_files.zip`
am.pack_directory(
    input_directory=r"C:\test_files\assorted_files",
    output_directory=r"C:\test_files",
    file_type="zip",
)
```

Pack to multiple formats with ease by iterating the `supported_archives` attribute:

```py
import glasswall

# Load the Glasswall Archive Manager library
am = glasswall.ArchiveManager(r"C:\azure\sdk.archive.manager")

# Pack the `assorted_files` directory in each supported file format
for file_type in am.supported_archives:
    am.pack_directory(
        input_directory=r"C:\test_files\assorted_files",
        output_directory=fr"C:\test_files",
        file_type=file_type,
    )
```

</details>

## Documentation

https://gw-engineering.github.io/glasswall-python-wrapper/

## Built With

- [Python 3.6.8 64-bit](https://www.python.org/downloads/release/python-368/)
