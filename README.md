![](https://github.com/filetrust/glasswall-python/actions/workflows/python-package.yml/badge.svg)

![](https://github.com/filetrust/glasswall-python/actions/workflows/python-publish.yml/badge.svg)

<!-- omit in toc -->
# Glasswall Python Wrapper

A high level Python wrapper for interfacing with Glasswall libraries.

<!-- omit in toc -->
## Installation

Install or upgrade to the latest version via pip:

<!-- omit in toc -->
### Online installation

```
pip install --upgrade glasswall
```

<!-- omit in toc -->
### Offline installation

Run the following commands within the directory containing the offline installation files.

```
pip install --upgrade --no-index --find-links=. glasswall
```
>**Note:** The wheels available for offline installation include all necessary dependencies for their respective packages and have been tested on amazonlinux.2023, rockylinux.8.9, and ubuntu.22.04 environments.

<!-- omit in toc -->
## Prerequisites

- [Python >= 3.6](https://www.python.org/downloads/)

<!-- omit in toc -->
## Auto-generated Documentation

https://gw-engineering.github.io/glasswall-python-wrapper/

<!-- omit in toc -->
## Examples

- [Loading a Glasswall library](#loading-a-glasswall-library)
- [Logging](#logging)
- [Content management policies](#content-management-policies)
- [Multiprocessing timeouts and memory limits](#multiprocessing-timeouts-and-memory-limits)
- [Editor](#editor)
  - [Protect](#protect)
    - [Protect from file path to file path](#protect-from-file-path-to-file-path)
    - [Protect from file path to memory](#protect-from-file-path-to-memory)
    - [Protect from memory](#protect-from-memory)
    - [Protect files in a directory](#protect-files-in-a-directory)
    - [Protect files in a directory that may contain unsupported file types](#protect-files-in-a-directory-that-may-contain-unsupported-file-types)
    - [Protect files in a directory using a custom content management policy](#protect-files-in-a-directory-using-a-custom-content-management-policy)
    - [Protect files in a directory conditionally based on file format](#protect-files-in-a-directory-conditionally-based-on-file-format)
  - [Analysis](#analysis)
    - [Analyse from file path to file path](#analyse-from-file-path-to-file-path)
    - [Analyse from file path to memory](#analyse-from-file-path-to-memory)
    - [Analyse from memory](#analyse-from-memory)
    - [Analyse files in a directory](#analyse-files-in-a-directory)
    - [Analyse files in a directory that may contain unsupported file types](#analyse-files-in-a-directory-that-may-contain-unsupported-file-types)
    - [Analyse files in a directory using a custom content management policy](#analyse-files-in-a-directory-using-a-custom-content-management-policy)
    - [Analyse files in a directory conditionally based on file format](#analyse-files-in-a-directory-conditionally-based-on-file-format)
  - [Export](#export)
    - [Export from file path to file path](#export-from-file-path-to-file-path)
    - [Export from file path to memory](#export-from-file-path-to-memory)
    - [Export from memory](#export-from-memory)
    - [Export files in a directory](#export-files-in-a-directory)
    - [Export files in a directory that may contain unsupported file types](#export-files-in-a-directory-that-may-contain-unsupported-file-types)
    - [Export files in a directory using a custom content management policy](#export-files-in-a-directory-using-a-custom-content-management-policy)
    - [Export files in a directory conditionally based on file format](#export-files-in-a-directory-conditionally-based-on-file-format)
  - [Import](#import)
    - [Import from file path to file path](#import-from-file-path-to-file-path)
    - [Import from file path to memory](#import-from-file-path-to-memory)
    - [Import from memory](#import-from-memory)
    - [Import files in a directory](#import-files-in-a-directory)
    - [Import files in a directory that may contain unsupported file types](#import-files-in-a-directory-that-may-contain-unsupported-file-types)
    - [Import files in a directory using a custom content management policy](#import-files-in-a-directory-using-a-custom-content-management-policy)
    - [Import files in a directory conditionally based on file format](#import-files-in-a-directory-conditionally-based-on-file-format)
- [Rebuild](#rebuild)
- [Archive Manager](#archive-manager)
    - [Protect an archive](#protect-an-archive)
    - [Protect all archives in a directory using a custom content management policy](#protect-all-archives-in-a-directory-using-a-custom-content-management-policy)
  - [Extraction - Unpacking an archive](#extraction---unpacking-an-archive)
    - [Other useful arguments when unpacking](#other-useful-arguments-when-unpacking)
  - [Extraction - Unpacking a directory of archives](#extraction---unpacking-a-directory-of-archives)
  - [Compression - Packing a directory into an archive](#compression---packing-a-directory-into-an-archive)
- [WordSearch](#wordsearch)
  - [Redact](#redact)
    - [Redact from file path to file path](#redact-from-file-path-to-file-path)
    - [Redact from file path to memory](#redact-from-file-path-to-memory)
    - [Redact from memory](#redact-from-memory)
    - [Redact files in a directory](#redact-files-in-a-directory)
    - [Redact files in a directory that may contain unsupported file types](#redact-files-in-a-directory-that-may-contain-unsupported-file-types)
    - [Redact files in a directory conditionally based on file format](#redact-files-in-a-directory-conditionally-based-on-file-format)

### Loading a Glasswall library

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
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")
```

```
>>> 2021-03-15 12:27:42.337 glasswall INFO     __init__                  Loaded Glasswall Editor version 2.173 from C:\gwpw\libraries\sdk.editor\windows-drop-no-kill-switch\glasswall_core2.dll
```

---

### Logging

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

---

### Content management policies

Documentation about content management policies can be found on the [Policy Management](https://docs.glasswall.com/docs/embedded-engine-policy-management) page.

Subclasses of the `glasswall.content_management.policies.Policy` class can be used to easily create content management policies of varying complexity by passing the `default` and `config` keyword arguments. Subclasses include:

- ArchiveManager
- Editor
- Rebuild
- WordSearch

Some examples of content management policies are below. Note that if a content management policy is required but has not been specified with the keyword argument `content_management_policy` then the default content management policy will be used.


Content management policies can be specified using subclasses of the `Policy` class:

<details>
    <summary>Expand setting an Editor policy</summary>

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

editor.protect_directory(
    input_directory=r"C:\gwpw\input",
    output_directory=r"C:\input_sanitised",
    content_management_policy=glasswall.content_management.policies.Editor(default="sanitise")
)
```

</details>

...or loaded from a file path:

<details>
    <summary>Expand setting an Editor policy from file path</summary>

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

editor.protect_directory(
    input_directory=r"C:\gwpw\input",
    output_directory=r"C:\input_sanitised",
    content_management_policy=r"C:\gwpw\configs\config.xml"
)
```

</details>

Some examples of policies and how to create them using the Policy subclasses are shown below.

<details>
    <summary>Expand Editor default sanitise all policy</summary>

```py
import glasswall

# Print the default Editor content management policy
print(glasswall.content_management.policies.Editor(default="sanitise"))
```

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


<details>
    <summary>Expand Rebuild custom allow all policy</summary>

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

Elements within a content management policy may have attributes. Attributes can be set by prefixing a key with the `@` character. In the below example the `recursionDepth` attribute is set with a value of `"30"`.

<details>
    <summary>Expand Archive Manager custom recursionDepth policy</summary>

```py
import glasswall

# Print a custom Archive Manager content management policy with a default of
# sanitise and an archive default of process. Set the recursionDepth attribute
# to 30. Discard any bmp files in the archive.
print(glasswall.content_management.policies.ArchiveManager(
    default="sanitise",
    default_archive_manager="process",
    config={
        "archiveConfig": {
            "@recursionDepth": "30",
            "bmp": "discard",
        }
    }
))
```

```xml
<?xml version="1.0" encoding="utf-8"?>
<config>
    <archiveConfig defaultCompression="zip" libVersion="core2" recursionDepth="30">
        <bmp>discard</bmp>
        <doc>process</doc>
        <docx>process</docx>
        <elf>process</elf>
        <emf>process</emf>
        <gif>process</gif>
        <jpeg>process</jpeg>
        <mp3>process</mp3>
        <mp4>process</mp4>
        <mpg>process</mpg>
        <o>process</o>
        <pdf>process</pdf>
        <pe>process</pe>
        <png>process</png>
        <ppt>process</ppt>
        <pptx>process</pptx>
        <tiff>process</tiff>
        <txt>process</txt>
        <wav>process</wav>
        <wmf>process</wmf>
        <xls>process</xls>
        <xlsx>process</xlsx>
    </archiveConfig>
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
        <export_embedded_images>true</export_embedded_images>
        <interchange_best_compression>false</interchange_best_compression>
        <interchange_pretty>false</interchange_pretty>
        <interchange_type>sisl</interchange_type>
        <run_mode>enablerebuild</run_mode>
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


<details>
    <summary>Expand Word Search custom policy</summary>

```py
import glasswall

# Print a custom Word Search content management policy with a default of
# allow. Redact instances of the string "lorem" by replacing each character
# with an asterisk, and redact instances of the string "ipsum" by replacing
# each character with the letter "X".
print(glasswall.content_management.policies.WordSearch(
    default="allow",
    config={
        "textSearchConfig": {
            "textList": [
                {"name": "textItem", "switches": [
                    {"name": "text", "value": "lorem"},
                    {"name": "textSetting", "@replacementChar": "*", "value": "redact"},
                ]},
                {"name": "textItem", "switches": [
                    {"name": "text", "value": "ipsum"},
                    {"name": "textSetting", "@replacementChar": "X", "value": "redact"},
                ]},
            ]
        }
    }
))
```

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
        <export_embedded_images>true</export_embedded_images>
        <interchange_best_compression>false</interchange_best_compression>
        <interchange_pretty>false</interchange_pretty>
        <interchange_type>xml</interchange_type>
        <run_mode>enablerebuild</run_mode>
    </sysConfig>
    <textSearchConfig libVersion="core2">
        <textList>
            <textItem>
                <text>lorem</text>
                <textSetting replacementChar="*">redact</textSetting>
            </textItem>
            <textItem>
                <text>ipsum</text>
                <textSetting replacementChar="X">redact</textSetting>
            </textItem>
        </textList>
    </textSearchConfig>
    <tiffConfig>
        <geotiff>allow</geotiff>
    </tiffConfig>
    <wordConfig>
        <dynamic_data_exchange>allow</dynamic_data_exchange>
        <embedded_files>allow</embedded_files>
        <embedded_images>allow</embedded_images>
        <external_hyperlinks>allow</external_hyperlinks>
        <internal_hyperlinks>allow</internal_hyperlinks>
        <macros>allow</macros>
        <metadata>allow</metadata>
        <review_comments>allow</review_comments>
    </wordConfig>
    <xlsConfig>
        <dynamic_data_exchange>allow</dynamic_data_exchange>
        <embedded_files>allow</embedded_files>
        <embedded_images>allow</embedded_images>
        <external_hyperlinks>allow</external_hyperlinks>
        <internal_hyperlinks>allow</internal_hyperlinks>
        <macros>allow</macros>
        <metadata>allow</metadata>
        <review_comments>allow</review_comments>
    </xlsConfig>
</config>
```

</details>

---

### Multiprocessing timeouts and memory limits

The `GlasswallProcessManager` class is designed to manage multiprocessing with a designated timeout and memory limit for each file being processed by the Glasswall engine.

The `GlasswallProcessManager` consumes `Task` objects which must be created and added to the queue. A `Task` object consists of a function that will be called, and arguments and keyword arguments that will be passed to that function.

The `GlasswallProcessManager` produces either a list of `TaskResult` objects once processing has completed, or yields individual `TaskResult` objects as they are completed. A `TaskResult` object contains attributes related to the processing of the file.

<details>
    <summary>Expand TaskResult attributes</summary>

```python
task: Task
success: bool  # True if function did not raise an exception
result: Any  # function return value
exception: Union[Exception, None],  # the exception raised by the function
exit_code: Union[int, None],  # multiprocessing.Process.exitcode, 0 = success
timeout_seconds: Optional[float]  # time limit for each process
memory_limit_in_gib: Optional[float]  # memory limit for each process, 1 gibibyte = 1024 ** 3 bytes
start_time: float  # uses time.time(), current time in seconds since the Epoch
end_time: float  # uses time.time(), current time in seconds since the Epoch
elapsed_time: float  # end_time - start_time
timed_out: bool  # terminated for exceeding the time limit: 'timeout_seconds'
max_memory_used_in_gib: float  # the highest recorded memory usage of the process
out_of_memory: bool  # terminated for exceeding the memory limit: 'memory_limit_in_gib'
```

</details

<br>

<details>
    <summary>Expand Example: Producing a list of `TaskResult` objects once processing has completed</summary>

<br>

In this example tasks are queued and processed in parallel up to the maximum number of workers, which by default is equal to the number of logical CPUs in the system. 

After all tasks are queued, processing begins automatically when exiting the `GlasswallProcessManager` context. Once all tasks are completed, the `process_manager.task_results` list attribute is populated with `TaskResult` objects that show the processing results.

Once all tasks are completed, this example iterates `process_manager.task_results` in a for loop and prints each `TaskResult` object.

```py
import os
import time

import glasswall
from glasswall.multiprocessing import GlasswallProcessManager, Task


INPUT_DIRECTORY = r"C:\gwpw\input"
OUTPUT_DIRECTORY = r"C:\gwpw\output\editor\multiprocessing"
LIBRARY_DIRECTORY = r"C:\gwpw\libraries\10.0"

glasswall.config.logging.console.setLevel("CRITICAL")
EDITOR = glasswall.Editor(LIBRARY_DIRECTORY)
gw_policy = glasswall.content_management.policies.Editor(default="sanitise")


def worker_function(*args, **kwargs):
    EDITOR.export_file(*args, **kwargs)


def main():
    start_time = time.time()
    input_files = glasswall.utils.list_file_paths(INPUT_DIRECTORY)
    with GlasswallProcessManager(max_workers=None, worker_timeout_seconds=5, memory_limit_in_gib=4) as process_manager:
        for input_file in input_files:
            relative_path = os.path.relpath(input_file, INPUT_DIRECTORY)
            output_file = os.path.join(OUTPUT_DIRECTORY, relative_path) + ".zip"

            task = Task(
                func=worker_function,
                args=tuple(),
                kwargs=dict(
                    input_file=input_file,
                    output_file=output_file,
                    content_management_policy=gw_policy,
                ),
            )
            process_manager.queue_task(task)

    for task_result in process_manager.task_results:
        print(task_result)

    print(f"Elapsed: {time.time() - start_time} seconds")


if __name__ == "__main__":
    main()
```

```
TaskResult(task=Task(func=worker_function, args=(), kwargs=(input_file='C:\\gwpw\\input\\TestFile_11.doc', outp..., success=True, result=None, exception=None, exit_code=0, timeout_seconds=5, memory_limit_in_gib=4, start_time=1710507465.3883162, end_time=1710507466.5565898, elapsed_time=1.168273687362671, timed_out=False, max_memory_used_in_gib=0.06385421752929688, out_of_memory=False)
TaskResult(task=Task(func=worker_function, args=(), kwargs=(input_file='C:\\gwpw\\input\\TestFile_9.doc', outpu..., success=True, result=None, exception=None, exit_code=0, timeout_seconds=5, memory_limit_in_gib=4, start_time=1710507466.299694, end_time=1710507467.366209, elapsed_time=1.0665149688720703, timed_out=False, max_memory_used_in_gib=0.06365966796875, out_of_memory=False)
TaskResult(task=Task(func=worker_function, args=(), kwargs=(input_file='C:\\gwpw\\input\\PDFWithGifAndJpeg.pdf'..., success=True, result=None, exception=None, exit_code=0, timeout_seconds=5, memory_limit_in_gib=4, start_time=1710507465.3763025, end_time=1710507467.7441902, elapsed_time=2.3678877353668213, timed_out=False, max_memory_used_in_gib=0.1662139892578125, out_of_memory=False)
Elapsed: 6.226853370666504 seconds
```

</details>

<details>
    <summary>Expand Example: Yielding individual `TaskResult` objects as they are completed</summary>

<br>

This example uses the external library [tqdm](https://pypi.org/project/tqdm/) to visualise progress during processing.

Tasks are queued and processed in parallel up to the maximum number of workers, which by default is equal to the number of logical CPUs in the system.

After all tasks are queued, processing begins within the `GlasswallProcessManager` context by invoking the `process_manager.as_completed()` generator method. Once any task is completed, its corresponding `TaskResult` object is yielded. This allows results to be accessed as they become available, rather than waiting for the completion of all tasks. The `process_manager.task_results` list attribute will not be populated.

As each task is completed, this example prints the yielded `TaskResult` object.

```py
import os
import time

from tqdm import tqdm

import glasswall
from glasswall.multiprocessing import GlasswallProcessManager, Task


INPUT_DIRECTORY = r"C:\gwpw\input"
OUTPUT_DIRECTORY = r"C:\gwpw\output\editor\multiprocessing"
LIBRARY_DIRECTORY = r"C:\gwpw\libraries\10.0"

glasswall.config.logging.console.setLevel("CRITICAL")
EDITOR = glasswall.Editor(LIBRARY_DIRECTORY)
gw_policy = glasswall.content_management.policies.Editor(default="sanitise")


def worker_function(*args, **kwargs):
    EDITOR.export_file(*args, **kwargs)


def main():
    start_time = time.time()
    input_files = glasswall.utils.list_file_paths(INPUT_DIRECTORY)
    with GlasswallProcessManager(max_workers=None, worker_timeout_seconds=5, memory_limit_in_gib=4) as process_manager:
        for input_file in tqdm(input_files, desc="Queueing files", miniters=len(input_files) // 10):
            relative_path = os.path.relpath(input_file, INPUT_DIRECTORY)
            output_file = os.path.join(OUTPUT_DIRECTORY, relative_path) + ".zip"

            task = Task(
                func=worker_function,
                args=tuple(),
                kwargs=dict(
                    input_file=input_file,
                    output_file=output_file,
                    content_management_policy=gw_policy,
                ),
            )
            process_manager.queue_task(task)

        for task_result in tqdm(process_manager.as_completed(), total=len(input_files), desc="Processing tasks", miniters=len(input_files) // 100):
            print(task_result)

    print(f"Elapsed: {time.time() - start_time} seconds")


if __name__ == "__main__":
    main()
```

```
Queueing files: 100%|███████████████████████████████████████████████████████████| 3/3 [00:00<00:00, 2993.79it/s]
Processing tasks:   0%|                                                                   | 0/3 [00:00<?, ?it/s]
TaskResult(task=Task(func=worker_function, args=(), kwargs=(input_file='C:\\gwpw\\input\\TestFile_11.doc', outp..., success=True, result=None, exception=None, exit_code=0, timeout_seconds=5, memory_limit_in_gib=4, start_time=1710507493.8832896, end_time=1710507496.1666203, elapsed_time=2.2833306789398193, timed_out=False, max_memory_used_in_gib=0.072662353515625, out_of_memory=False)
Processing tasks:  33%|███████████████████▋                                       | 1/3 [00:04<00:08,  4.08s/it]
TaskResult(task=Task(func=worker_function, args=(), kwargs=(input_file='C:\\gwpw\\input\\TestFile_9.doc', outpu..., success=True, result=None, exception=None, exit_code=0, timeout_seconds=5, memory_limit_in_gib=4, start_time=1710507495.4604173, end_time=1710507497.5040953, elapsed_time=2.043678045272827, timed_out=False, max_memory_used_in_gib=0.06534576416015625, out_of_memory=False)
Processing tasks:  67%|███████████████████████████████████████▎                   | 2/3 [00:05<00:02,  2.46s/it]
TaskResult(task=Task(func=worker_function, args=(), kwargs=(input_file='C:\\gwpw\\input\\PDFWithGifAndJpeg.pdf'..., success=True, result=None, exception=None, exit_code=0, timeout_seconds=5, memory_limit_in_gib=4, start_time=1710507495.3951488, end_time=1710507498.389851, elapsed_time=2.9947023391723633, timed_out=False, max_memory_used_in_gib=0.1673431396484375, out_of_memory=False)
Processing tasks: 100%|███████████████████████████████████████████████████████████| 3/3 [00:06<00:00,  2.11s/it] 
Elapsed: 6.356592416763306 seconds
```

</details>

> Note that while the `GlasswallProcessManager` can handle large returns of data from the worker_function, holding this data in memory can quickly fill up the available RAM. When possible, it is advised not to return from the worker_function, and instead to rely on file to file processing.
> If processing files to disk is undesirable or returning the file bytes from the worker function is required, we recommend the following steps:
> - Limit `max_workers` to allow for at least 4 GiB of memory available for each process.
> - Use the `as_completed` generator.
> - Ensure file bytes are not retained after being yielded from `as_completed` so that the Python garbage collector will free up memory after the file bytes are no longer referenced.

<details>
    <summary>Expand Example: Yielding file bytes in file to memory mode and limiting max_workers</summary>

<br>

This example uses the external library [tqdm](https://pypi.org/project/tqdm/) to visualise progress during processing.

The worker_function has been modified to return the result of `EDITOR.export_file`, which will be either the export zip file's bytes, or None.

The max_workers is limited based on the logical CPUs and RAM available.

Tasks are queued and processed in parallel up to the specified number of workers.

After all tasks are queued, processing begins within the `GlasswallProcessManager` context by invoking the `process_manager.as_completed()` generator method. Once any task is completed, its corresponding `TaskResult` object is yielded. This allows results to be accessed as they become available, rather than waiting for the completion of all tasks. The `process_manager.task_results` list attribute will not be populated.

As each task is completed, this example prints the yielded `TaskResult` object, and if the `task_result.result` attribute is populated, it also prints information on the file size of the export zip file.

```py
import os
import time

from tqdm import tqdm

import glasswall
from glasswall.multiprocessing import GlasswallProcessManager, Task
from glasswall.multiprocessing.memory_usage import get_available_memory_gib


INPUT_DIRECTORY = r"C:\gwpw\input"
OUTPUT_DIRECTORY = r"C:\gwpw\output\editor\multiprocessing"
LIBRARY_DIRECTORY = r"C:\gwpw\libraries\10.0"

glasswall.config.logging.console.setLevel("CRITICAL")
EDITOR = glasswall.Editor(LIBRARY_DIRECTORY)
gw_policy = glasswall.content_management.policies.Editor(default="sanitise")


def worker_function(*args, **kwargs):
    return EDITOR.export_file(*args, **kwargs)


def main():
    start_time = time.time()
    available_memory_gib = get_available_memory_gib()
    print(f"Available memory: {available_memory_gib} GiB")
    # Set max_workers to lowest between cpu_count or available memory // 4 (4gib per process)
    cpu_count = os.cpu_count() or 1
    max_workers = int(min(cpu_count, available_memory_gib // 4))
    print(f"Max workers: {max_workers}")

    input_files = glasswall.utils.list_file_paths(INPUT_DIRECTORY)
    with GlasswallProcessManager(max_workers=max_workers, worker_timeout_seconds=5, memory_limit_in_gib=4) as process_manager:
        for input_file in tqdm(input_files, desc="Queueing files", miniters=len(input_files) // 10):
            # No output_file specified, export_file will run in file to memory mode
            task = Task(
                func=worker_function,
                args=tuple(),
                kwargs=dict(
                    input_file=input_file,
                    content_management_policy=gw_policy,
                ),
            )
            process_manager.queue_task(task)

        for task_result in tqdm(process_manager.as_completed(), total=len(input_files), desc="Processing tasks", miniters=len(input_files) // 100):
            print(task_result)
            # Do something with export zip file bytes in memory
            if task_result.result:
                print(f"Export zip file size is: {len(task_result.result)} bytes for input_file: '{task_result.task.kwargs['input_file']}'")
            # task_result no longer referenced and is garbage collected here, freeing up memory

    print(f"Elapsed: {time.time() - start_time} seconds")


if __name__ == "__main__":
    main()
```

```
Available memory: 13.020416259765625 GiB
Max workers: 3
Queueing files: 100%|█████████████████████████████████████████████████████████████████████| 3/3 [00:00<?, ?it/s]
Processing tasks:   0%|                                                                   | 0/3 [00:00<?, ?it/s]
TaskResult(task=Task(func=worker_function, args=(), kwargs=(input_file='C:\\gwpw\\input\\TestFile_11.doc', cont..., success=True, result=b'PK\x03\x04\x14\x00\x0e\x00\x08\x00\xceloX\xc7\x95\x89\xba\xce\x07\x00\x00-\x19\x00\x00\x19\..., exception=None, exit_code=0, timeout_seconds=5, memory_limit_in_gib=4, start_time=1710509905.3188772, end_time=1710509908.5976403, elapsed_time=3.2787630558013916, timed_out=False, max_memory_used_in_gib=0.06348419189453125, out_of_memory=False)
Export zip file size is: 97553 bytes for input_file: 'C:\gwpw\input\TestFile_11.doc'
Processing tasks:  33%|███████████████████▋                                       | 1/3 [00:04<00:09,  4.99s/it]
TaskResult(task=Task(func=worker_function, args=(), kwargs=(input_file='C:\\gwpw\\input\\PDFWithGifAndJpeg.pdf'..., success=True, result=b'PK\x03\x04\x14\x00\x0e\x00\x08\x00\xcdloX\xca@\xc8\x8a\xf0\x1d\x00\x00k\xc6\x00\x00\x19\x00..., exception=None, exit_code=0, timeout_seconds=5, memory_limit_in_gib=4, start_time=1710509905.1324441, end_time=1710509908.958884, elapsed_time=3.82643985748291, timed_out=False, max_memory_used_in_gib=0.166259765625, out_of_memory=False)
Export zip file size is: 664734 bytes for input_file: 'C:\gwpw\input\PDFWithGifAndJpeg.pdf'
Processing tasks:  67%|███████████████████████████████████████▎                   | 2/3 [00:05<00:02,  2.25s/it]
TaskResult(task=Task(func=worker_function, args=(), kwargs=(input_file='C:\\gwpw\\input\\TestFile_9.doc', conte..., success=True, result=b'PK\x03\x04\x14\x00\x0e\x00\x08\x00\xcfloX\xc7\x95\x89\xba\xce\x07\x00\x00-\x19\x00\x00\x19\..., exception=None, exit_code=0, timeout_seconds=5, memory_limit_in_gib=4, start_time=1710509907.833435, end_time=1710509910.3073368, elapsed_time=2.4739017486572266, timed_out=False, max_memory_used_in_gib=0.0728759765625, out_of_memory=False)
Export zip file size is: 139697 bytes for input_file: 'C:\gwpw\input\TestFile_9.doc'
Processing tasks: 100%|███████████████████████████████████████████████████████████| 3/3 [00:06<00:00,  2.23s/it] 
Elapsed: 6.706916809082031 seconds
```

</details>

---

### Editor

#### Protect

Files can be protected individually from a file path or in memory using the [`protect_file`](https://gw-engineering.github.io/glasswall-python-wrapper/libraries/editor/editor.html#glasswall.libraries.editor.editor.Editor.protect_file) method, or all files from a directory can be protected using the [`protect_directory`](https://gw-engineering.github.io/glasswall-python-wrapper/libraries/editor/editor.html#glasswall.libraries.editor.editor.Editor.protect_directory) method.

##### Protect from file path to file path

```py   
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Use the default policy to sanitise a file, writing the sanitised file to a new path
editor.protect_file(
    input_file=r"C:\gwpw\input\TestFile_11.doc",
    output_file=r"C:\gwpw\output\editor\protect_f2f\TestFile_11.doc",
)

```

##### Protect from file path to memory

`protect_file` returns the protected file's bytes. The below example demonstrates assigning the variable `file_bytes`. We can see that after sanitisation the first 8 bytes of `file_bytes` matches the [file signature](https://en.wikipedia.org/wiki/List_of_file_signatures) for the Microsoft Compound File Binary (CFB) format, `D0 CF 11 E0 A1 B1 1A E1`.

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Use the default policy to sanitise a file in memory, returning the file bytes in memory
file_bytes = editor.protect_file(
    input_file=r"C:\gwpw\input\TestFile_11.doc"
)

assert file_bytes[:8] == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'

```

##### Protect from memory

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Read file from disk to memory
with open(r"C:\gwpw\input\TestFile_11.doc", "rb") as f:
    input_bytes = f.read()

# Use the default policy to sanitise a file
file_bytes = editor.protect_file(
    input_file=input_bytes,
)

assert file_bytes[:8] == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'

```

##### Protect files in a directory

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Use the default policy to protect a directory of files, writing the sanitised files to a new directory.
editor.protect_directory(
    input_directory=r"C:\gwpw\input",
    output_directory=r"C:\gwpw\output\editor\protect_directory"
)

```

##### Protect files in a directory that may contain unsupported file types

The default behaviour of the Glasswall Python wrapper is to raise the relevant exception (see: [glasswall.libraries.editor.errors](https://gw-engineering.github.io/glasswall-python-wrapper/libraries/editor/errors.html)) if processing fails. Passing `raise_unsupported=False` will prevent an exception being raised and can be useful when working with a directory containing a mixture of both supported and unsupported file types when it is desired to process as many of the files as possible instead of terminating on the first failure.

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Use the default policy to protect a directory of files, writing the sanitised files to a new directory.
editor.protect_directory(
    input_directory=r"C:\gwpw\input_with_unsupported_file_types",
    output_directory=r"C:\gwpw\output\editor\protect_directory_unsupported",
    raise_unsupported=False
)

```

##### Protect files in a directory using a custom content management policy

Using `glasswall.content_management.policies.Editor`:

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Use a custom Editor policy to sanitise all files in the input directory
# and write them to the input_sanitised directory. If macros are present
# in ppt or word files, the file will be marked as non-conforming and blocked.
# If internal or external hyperlinks are present in word files they will not
# be sanitised, and will remain in the regenerated document.
editor.protect_directory(
    input_directory=r"C:\gwpw\input",
    output_directory=r"C:\gwpw\output\editor\protect_directory_custom",
    content_management_policy=glasswall.content_management.policies.Editor(
        default="sanitise",
        config={
            "pptConfig": {
                "macros": "disallow",
            },
            "wordConfig": {
                "internal_hyperlinks": "allow",
                "external_hyperlinks": "allow",
                "macros": "disallow",
            }
        }
    )
)

```

##### Protect files in a directory conditionally based on file format
The example below demonstrates processing of only doc and docx files from a nested directory containing multiple file formats.
```py
import os

import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

input_directory = r"C:\gwpw\input"
output_directory = r"C:\gwpw\output\editor\protect_directory_file_format"

# Iterate relative file paths from input_directory
for relative_file in glasswall.utils.list_file_paths(input_directory, absolute=False):
    # Construct absolute paths
    input_file = os.path.join(input_directory, relative_file)
    output_file = os.path.join(output_directory, relative_file)

    # Get the file type of the file
    file_type = editor.determine_file_type(
        input_file=input_file,
        as_string=True,
        raise_unsupported=False
    )

    # Protect only doc and docx files
    if file_type in ["doc", "docx"]:
        editor.protect_file(input_file, output_file)

```

---

#### Analysis

Files can be analysed individually from a file path or in memory using the [`analyse_file`](https://gw-engineering.github.io/glasswall-python-wrapper/libraries/editor/editor.html#glasswall.libraries.editor.editor.Editor.analyse_file) method, or all files from a directory can be analysed using the [`analyse_directory`](https://gw-engineering.github.io/glasswall-python-wrapper/libraries/editor/editor.html#glasswall.libraries.editor.editor.Editor.analyse_directory) method.


##### Analyse from file path to file path

```py   
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Use the default policy to analyse a file, writing the analysis report to a new path
editor.analyse_file(
    input_file=r"C:\gwpw\input\TestFile_11.doc",
    output_file=r"C:\gwpw\output\editor\analyse_f2f\TestFile_11.doc.xml",
)

```

##### Analyse from file path to memory

`analyse_file` returns the analysis report xml file's bytes. The below example demonstrates assigning the variable `analysis_report` and checking the contents of the beginning of an Editor analysis report.

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Use the default policy to analyse a file
analysis_report = editor.analyse_file(
    input_file=r"C:\gwpw\input\TestFile_11.doc",
)

assert analysis_report[:500] == b'<?xml version="1.0" encoding="utf-8"?>\n<gw:GWallInfo xsi:schemaLocation="http://glasswall.com/namespace/gwallInfo.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:gw="http://glasswall.com/namespace">\n\t<gw:DocumentStatistics>\n\t\t<gw:DocumentSummary>\n\t\t\t<gw:TotalSizeInBytes>35840</gw:TotalSizeInBytes>\n\t\t\t<gw:FileType>doc</gw:FileType>\n\t\t\t<gw:Version>Not Applicable</gw:Version>\n\t\t\t<gw:InputSHA256>9FDE85B8800C1019D2865FA298A7F75873E09870B71F9825827E354B865686A6</gw:InputSHA256>\n\t\t\t<gw'

```

##### Analyse from memory

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Read file from disk to memory
with open(r"C:\gwpw\input\TestFile_11.doc", "rb") as f:
    input_bytes = f.read()

# Use the default policy to analyse a file
analysis_report = editor.analyse_file(
    input_file=input_bytes,
)

assert analysis_report[:500] == b'<?xml version="1.0" encoding="utf-8"?>\n<gw:GWallInfo xsi:schemaLocation="http://glasswall.com/namespace/gwallInfo.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:gw="http://glasswall.com/namespace">\n\t<gw:DocumentStatistics>\n\t\t<gw:DocumentSummary>\n\t\t\t<gw:TotalSizeInBytes>35840</gw:TotalSizeInBytes>\n\t\t\t<gw:FileType>doc</gw:FileType>\n\t\t\t<gw:Version>Not Applicable</gw:Version>\n\t\t\t<gw:InputSHA256>9FDE85B8800C1019D2865FA298A7F75873E09870B71F9825827E354B865686A6</gw:InputSHA256>\n\t\t\t<gw'

```

##### Analyse files in a directory

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Use the default policy to analyse a directory of files, writing the analysis reports to a new directory.
editor.analyse_directory(
    input_directory=r"C:\gwpw\input",
    output_directory=r"C:\gwpw\output\editor\analyse_directory"
)

```

##### Analyse files in a directory that may contain unsupported file types

The default behaviour of the Glasswall Python wrapper is to raise the relevant exception (see: [glasswall.libraries.editor.errors](https://gw-engineering.github.io/glasswall-python-wrapper/libraries/editor/errors.html)) if processing fails. Passing `raise_unsupported=False` will prevent an exception being raised and can be useful when working with a directory containing a mixture of both supported and unsupported file types when it is desired to process as many of the files as possible instead of terminating on the first failure.

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Use the default policy to analyse a directory of files, writing the analysis reports to a new directory.
editor.analyse_directory(
    input_directory=r"C:\gwpw\input_with_unsupported_file_types",
    output_directory=r"C:\gwpw\output\editor\analyse_directory_unsupported",
    raise_unsupported=False
)

```

##### Analyse files in a directory using a custom content management policy

Using `glasswall.content_management.policies.Editor`:

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Use a custom Editor policy to analyse all files in the input directory
# and write them to analyse_directory_custom directory. If macros are
# present in ppt or word files, a GeneralFail exception will be raised if the
# raise_unsupported argument is left at it's default value of False, but the
# analysis report will still be written to file and will contain IssueItems.
# If internal or external hyperlinks are present in word files they will not
# be sanitised, and will remain in the regenerated document.
editor.analyse_directory(
    input_directory=r"C:\gwpw\input",
    output_directory=r"C:\gwpw\output\editor\analyse_directory_custom",
    content_management_policy=glasswall.content_management.policies.Editor(
        default="sanitise",
        config={
            "pptConfig": {
                "macros": "disallow",
            },
            "wordConfig": {
                "internal_hyperlinks": "allow",
                "external_hyperlinks": "allow",
                "macros": "disallow",
            }
        }
    ),
    raise_unsupported=False
)

```


##### Analyse files in a directory conditionally based on file format
The example below demonstrates processing of only doc and docx files from a nested directory containing multiple file formats.
```py
import os

import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

input_directory = r"C:\gwpw\input"
output_directory = r"C:\gwpw\output\editor\analyse_directory_file_format"

# Iterate relative file paths from input_directory
for relative_file in glasswall.utils.list_file_paths(input_directory, absolute=False):
    # Construct absolute paths
    input_file = os.path.join(input_directory, relative_file)
    output_file = os.path.join(output_directory, relative_file + ".xml")

    # Get the file type of the file
    file_type = editor.determine_file_type(
        input_file=input_file,
        as_string=True,
        raise_unsupported=False
    )

    # Analyse only doc and docx files
    if file_type in ["doc", "docx"]:
        editor.analyse_file(input_file, output_file)

```

---

#### Export

Files can be exported individually from a file path or in memory using the [`export_file`](https://gw-engineering.github.io/glasswall-python-wrapper/libraries/editor/editor.html#glasswall.libraries.editor.editor.Editor.export_file) method, or all files from a directory can be exported using the [`export_directory`](https://gw-engineering.github.io/glasswall-python-wrapper/libraries/editor/editor.html#glasswall.libraries.editor.editor.Editor.export_directory) method.


##### Export from file path to file path

```py   
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Use the default policy to export a file, writing the export archive to a new path
editor.export_file(
    input_file=r"C:\gwpw\input\TestFile_11.doc",
    output_file=r"C:\gwpw\output\editor\export_f2f\TestFile_11.doc.zip",
)

```

##### Export from file path to memory

`export_file` returns the exported archive file's bytes. The below example demonstrates assigning the variable `export_archive` and checking the contents of the beginning of an Editor export archive.

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Use the default policy to export a file
export_archive = editor.export_file(
    input_file=r"C:\gwpw\input\TestFile_11.doc",
)

assert export_archive[:8] == b'PK\x03\x04\x14\x00\x0e\x00'

```

##### Export from memory

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Read file from disk to memory
with open(r"C:\gwpw\input\TestFile_11.doc", "rb") as f:
    input_bytes = f.read()

# Use the default policy to export a file
export_archive = editor.export_file(
    input_file=input_bytes,
)

assert export_archive[:8] == b'PK\x03\x04\x14\x00\x0e\x00'

```

##### Export files in a directory

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Use the default policy to export a directory of files, writing the export archives to a new directory.
editor.export_directory(
    input_directory=r"C:\gwpw\input",
    output_directory=r"C:\gwpw\output\editor\export_directory"
)

```

##### Export files in a directory that may contain unsupported file types

The default behaviour of the Glasswall Python wrapper is to raise the relevant exception (see: [glasswall.libraries.editor.errors](https://gw-engineering.github.io/glasswall-python-wrapper/libraries/editor/errors.html)) if processing fails. Passing `raise_unsupported=False` will prevent an exception being raised and can be useful when working with a directory containing a mixture of both supported and unsupported file types when it is desired to process as many of the files as possible instead of terminating on the first failure.

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Use the default policy to export a directory of files, writing the export archives to a new directory.
editor.export_directory(
    input_directory=r"C:\gwpw\input_with_unsupported_file_types",
    output_directory=r"C:\gwpw\output\editor\export_directory_unsupported",
    raise_unsupported=False
)

```

##### Export files in a directory using a custom content management policy

Using `glasswall.content_management.policies.Editor`:

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Use a custom Editor policy to export all files in the input directory
# and write them to export_directory_custom directory. Write streams as
# ".xml" instead of the default interchange_type, ".sisl". Export embedded
# images as ".xml" instead of their default image file type.
editor.export_directory(
    input_directory=r"C:\gwpw\input",
    output_directory=r"C:\gwpw\output\editor\export_directory_custom",
    content_management_policy=glasswall.content_management.policies.Editor(
        default="sanitise",
        config={
            "sysConfig": {
                "interchange_type": "xml",
                "export_embedded_images": "true",
            },
        }
    ),
    raise_unsupported=False
)

```


##### Export files in a directory conditionally based on file format
The example below demonstrates processing of only doc and docx files from a nested directory containing multiple file formats.
```py
import os

import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

input_directory = r"C:\gwpw\input"
output_directory = r"C:\gwpw\output\editor\export_directory_file_format"

# Iterate relative file paths from input_directory
for relative_file in glasswall.utils.list_file_paths(input_directory, absolute=False):
    # Construct absolute paths
    input_file = os.path.join(input_directory, relative_file)
    output_file = os.path.join(output_directory, relative_file + ".zip")

    # Get the file type of the file
    file_type = editor.determine_file_type(
        input_file=input_file,
        as_string=True,
        raise_unsupported=False
    )

    # Export only doc and docx files
    if file_type in ["doc", "docx"]:
        editor.export_file(input_file, output_file)

```

---

#### Import

Export archives can be imported individually from a file path or in memory using the [`import_file`](https://gw-engineering.github.io/glasswall-python-wrapper/libraries/editor/editor.html#glasswall.libraries.editor.editor.Editor.import_file) method, or all export archives from a directory can be imported using the [`import_directory`](https://gw-engineering.github.io/glasswall-python-wrapper/libraries/editor/editor.html#glasswall.libraries.editor.editor.Editor.import_directory) method.


##### Import from file path to file path

```py   
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Use the default policy to import an export archive, writing the imported file to a new path
editor.import_file(
    input_file=r"C:\gwpw\output\editor\export_f2f\TestFile_11.doc.zip",
    output_file=r"C:\gwpw\output\editor\import_f2f\TestFile_11.doc",
)

```

##### Import from file path to memory

`import_file` returns the imported file's bytes. The below example demonstrates assigning the variable `file_bytes` and checking the contents of the beginning of an Editor export archive.

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Use the default policy to import an export archive
file_bytes = editor.import_file(
    input_file=r"C:\gwpw\output\editor\export_f2f\TestFile_11.doc.zip",
)

assert file_bytes[:8] == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'

```

##### Import from memory

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Read file from disk to memory
with open(r"C:\gwpw\output\editor\export_f2f\TestFile_11.doc.zip", "rb") as f:
    export_archive_bytes = f.read()

# Use the default policy to import an export archive
file_bytes = editor.import_file(
    input_file=export_archive_bytes,
)

assert file_bytes[:8] == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'

```

##### Import files in a directory

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Use the default policy to import a directory of export archives, writing the import archives to a new directory.
editor.import_directory(
    input_directory=r"C:\gwpw\output\editor\export_directory",
    output_directory=r"C:\gwpw\output\editor\import_directory"
)

```

##### Import files in a directory that may contain unsupported file types

The default behaviour of the Glasswall Python wrapper is to raise the relevant exception (see: [glasswall.libraries.editor.errors](https://gw-engineering.github.io/glasswall-python-wrapper/libraries/editor/errors.html)) if processing fails. Passing `raise_unsupported=False` will prevent an exception being raised and can be useful when working with a directory containing a mixture of both supported and unsupported file types when it is desired to process as many of the files as possible instead of terminating on the first failure.

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Use the default policy to export a directory of export archives, writing the export archives to a new directory.
editor.import_directory(
    input_directory=r"C:\gwpw\output\editor\export_directory_unsupported",
    output_directory=r"C:\gwpw\output\editor\import_directory_unsupported",
    raise_unsupported=False
)

```

##### Import files in a directory using a custom content management policy

Using `glasswall.content_management.policies.Editor`:

```py
import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Use a custom Editor policy to import all files in the export directory
# and write them to import_directory_custom directory. Read streams as
# ".xml" instead of the default interchange_type, ".sisl".
editor.import_directory(
    input_directory=r"C:\gwpw\output\editor\export_directory_custom",
    output_directory=r"C:\gwpw\output\editor\import_directory_custom",
    content_management_policy=glasswall.content_management.policies.Editor(
        default="sanitise",
        config={
            "sysConfig": {
                "interchange_type": "xml",
            },
        }
    ),
    raise_unsupported=False
)

```


##### Import files in a directory conditionally based on file format
The example below demonstrates processing of only doc and docx files from a nested directory containing multiple file formats.
```py
import os

import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

input_directory = r"C:\gwpw\output\editor\export_directory_file_format"
output_directory = r"C:\gwpw\output\editor\import_directory_file_format"

# Iterate relative file paths from input_directory
for relative_file in glasswall.utils.list_file_paths(input_directory, absolute=False):
    # Construct absolute paths
    input_file = os.path.join(input_directory, relative_file)
    output_file = os.path.join(output_directory, os.path.splitext(relative_file)[0])

    # Get the file type of the file
    file_type = editor.determine_file_type(
        input_file=input_file,
        as_string=True,
        raise_unsupported=False
    )

    # Import only doc.zip and docx.zip files
    if file_type == "zip" and input_file.endswith(("doc.zip", "docx.zip",)):
        editor.import_file(input_file, output_file)

```

---

### Rebuild

See [Editor](#editor) documentation. High level functionality is the same between the Editor and Rebuild classes, simply use the Rebuild class instead of the Editor class:

```py
import glasswall


# Load the Glasswall Rebuild library
rebuild = glasswall.Rebuild(r"C:\gwpw\libraries\rebuild\1.661.0")

# Use the default policy to sanitise a file, writing the sanitised file to a new path
rebuild.protect_file(
    input_file=r"C:\gwpw\input\TestFile_11.doc",
    output_file=r"C:\gwpw\output\rebuild\protect_f2f\TestFile_11.doc",
)

```

---

### Archive Manager

##### Protect an archive

```py
import glasswall

# Load the Glasswall Archive Manager library
am = glasswall.ArchiveManager(r"C:\gwpw\libraries\10.0")

# Use the default Archive Manager policy: sanitise all, process all, writing
# the sanitised archive and the analysis report to the output directory.
am.protect_archive(
    input_file=r"C:\gwpw\input_archives\7Zip\0000001.jpg.7z",
    output_file=r"C:\gwpw\output\archive_manager\protect_archive\7Zip\0000001.jpg.7z",
    output_report=r"C:\gwpw\output\archive_manager\protect_archive\7Zip\0000001.jpg.7z.xml"
)
```

##### Protect all archives in a directory using a custom content management policy

```py
import glasswall

# Load the Glasswall Archive Manager library
am = glasswall.ArchiveManager(r"C:\gwpw\libraries\10.0")

# Use a custom Archive Manager policy: sanitise all, process all, but discard
# mp3 and mp4 files. Write the sanitised archives and the analysis reports to
# different directories
am.protect_directory(
    input_directory=r"C:\gwpw\input_archives",
    output_directory=r"C:\gwpw\output\archive_manager\protect_directory_custom",
    output_report_directory=r"C:\gwpw\output\archive_manager\protect_directory_custom_reports",
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

#### Extraction - Unpacking an archive

```py
import glasswall

# Load the Glasswall Archive Manager library
am = glasswall.ArchiveManager(r"C:\gwpw\libraries\10.0")

# Unpack the Nested_4_layers.zip archive to a new directory
am.unpack(
    input_file=r"C:\gwpw\input_archives\Nested_4_layers.zip",
    output_directory=r"C:\gwpw\output\archive_manager\unpack"
)
```

A new directory is created: `C:\gwpw\output\archive_manager\unpack\Nested_4_layers` containing the unpacked contents of the `Nested_4_layers` zip archive. Nested archives are recursively unpacked while maintaining the same directory structure. To disable recursive unpacking use the `recursive` arg:

```py
import glasswall

# Load the Glasswall Archive Manager library
am = glasswall.ArchiveManager(r"C:\gwpw\libraries\10.0")

# Unpack the Nested_4_layers.zip archive to a new directory without recursing the archive.
am.unpack(
    input_file=r"C:\gwpw\input_archives\Nested_4_layers.zip",
    output_directory=r"C:\gwpw\output\archive_manager\unpack_nonrecursive",
    recursive=False
)
```

##### Other useful arguments when unpacking

- `include_file_type` default False, keep the archive format in the directory name when unpacking. e.g. when True `Nested_4_layers.zip` will be unpacked to a directory `Nested_4_layers.zip` instead of `Nested_4_layers`. This can be necessary when unpacking multiple same-named archives that have different archive formats.
- `raise_unsupported` default True, raise an error if the Glasswall library encounters an error.
- `delete_origin` default False, delete the `input_file` after it has been unpacked to `output_directory`.

#### Extraction - Unpacking a directory of archives

```py
import glasswall

# Load the Glasswall Archive Manager library
am = glasswall.ArchiveManager(r"C:\gwpw\libraries\10.0")

# Recursively unpack all archives found in the `archives` directory
am.unpack_directory(
    input_directory=r"C:\gwpw\input_archives",
    output_directory=r"C:\gwpw\output\archive_manager\unpack_directory"
)
```

The `unpack_directory` method shares the same optional arguments as `unpack`. See also: `Extraction - Unpacking an archive`

#### Compression - Packing a directory into an archive

```py
import glasswall

# Load the Glasswall Archive Manager library
am = glasswall.ArchiveManager(r"C:\gwpw\libraries\10.0")

# Pack the `input_archives` directory as zip to `input_archives.zip` in the 'C:\gwpw\output\archive_manager\pack' directory
am.pack_directory(
    input_directory=r"C:\gwpw\input_archives",
    output_directory=r"C:\gwpw\output\archive_manager\pack",
    file_type="zip",
)
```

---

### WordSearch

Glasswall WordSearch can be used to redact text from files and generates an XML report on the redacted file's details.

This report includes details on the file size, the determined file type, the total number of text matches, and the location of each of the text matches.

<details>
    <summary>Example report</summary>

```xml
<gw:WordSearchStatistics xmlns:gw="http://glasswall.com/namespace">
	<gw:DocumentSummary>
		<gw:TotalSizeInBytes>13084</gw:TotalSizeInBytes>
		<gw:FileType>docx</gw:FileType>
		<gw:TotalItemMatchCount>8</gw:TotalItemMatchCount>
	</gw:DocumentSummary>
	<gw:WordItem>
		<gw:Name>ipsum</gw:Name>
		<gw:ItemMatchCount>5</gw:ItemMatchCount>
		<gw:Locations>
			<gw:Location>
				<gw:Offset>120</gw:Offset>
				<gw:Page>0</gw:Page>
				<gw:Paragraph>0</gw:Paragraph>
			</gw:Location>
			<gw:Location>
				<gw:Offset>267</gw:Offset>
				<gw:Page>0</gw:Page>
				<gw:Paragraph>0</gw:Paragraph>
			</gw:Location>
			<gw:Location>
				<gw:Offset>691</gw:Offset>
				<gw:Page>0</gw:Page>
				<gw:Paragraph>0</gw:Paragraph>
			</gw:Location>
			<gw:Location>
				<gw:Offset>973</gw:Offset>
				<gw:Page>0</gw:Page>
				<gw:Paragraph>0</gw:Paragraph>
			</gw:Location>
			<gw:Location>
				<gw:Offset>1034</gw:Offset>
				<gw:Page>0</gw:Page>
				<gw:Paragraph>0</gw:Paragraph>
			</gw:Location>
		</gw:Locations>
	</gw:WordItem>
	<gw:WordItem>
		<gw:Name>lorem</gw:Name>
		<gw:ItemMatchCount>3</gw:ItemMatchCount>
		<gw:Locations>
			<gw:Location>
				<gw:Offset>114</gw:Offset>
				<gw:Page>0</gw:Page>
				<gw:Paragraph>0</gw:Paragraph>
			</gw:Location>
			<gw:Location>
				<gw:Offset>244</gw:Offset>
				<gw:Page>0</gw:Page>
				<gw:Paragraph>0</gw:Paragraph>
			</gw:Location>
			<gw:Location>
				<gw:Offset>1224</gw:Offset>
				<gw:Page>0</gw:Page>
				<gw:Paragraph>0</gw:Paragraph>
			</gw:Location>
		</gw:Locations>
	</gw:WordItem>
</gw:WordSearchStatistics>


```

</details>

A homoglyphs JSON file can be specified either as a file path or in memory as bytes, bytearray, or io.BytesIO. If this is not specified then the default will be used:

<details>
    <summary>Default homoglyphs.json file</summary>

```json
{
	"!": "ǃⵑ",
	"$": "＄",
	"%": "％",
	"&": "ꝸ＆",
	"'": "`´ʹʻʼʽʾˈˊˋ˴ʹ΄՚՝י׳ߴߵᑊᛌ᾽᾿`´῾‘’‛′‵ꞌ＇｀𖽑𖽒",
	"(": "❨❲〔﴾（［",
	")": "❩❳〕﴿）］",
	"*": "٭⁎∗＊𐌟",
	"+": "᛭＋𐊛",
	",": "¸؍٫‚ꓹ，",
	"-": "˗۔‐‑‒–⁃−➖Ⲻ﹘",
	".": "٠۰܁܂․ꓸ꘎．𐩐𝅭",
	"/": "᜵⁁⁄∕╱⟋⧸Ⳇ⼃〳ノ㇓丿／𝈺",
	"0": "OoΟοσОоՕօסه٥ھہە۵߀०০੦૦ଠ୦௦ం౦ಂ೦ംഠ൦ං๐໐ဝ၀ჿዐᴏᴑℴⲞⲟⵔ〇ꓳꬽﮦﮧﮨﮩﮪﮫﮬﮭﻩﻪﻫﻬ０Ｏｏ𐊒𐊫𐐄𐐬𐓂𐓪𐔖𑓐𑢵𑣈𑣗𑣠𝐎𝐨𝑂𝑜𝑶𝒐𝒪𝓞𝓸𝔒𝔬𝕆𝕠𝕺𝖔𝖮𝗈𝗢𝗼𝘖𝘰𝙊𝙤𝙾𝚘𝚶𝛐𝛔𝛰𝜊𝜎𝜪𝝄𝝈𝝤𝝾𝞂𝞞𝞸𝞼𝟎𝟘𝟢𝟬𝟶𞸤𞹤𞺄",
	"1": "Il|ƖǀΙІӀ׀וןا١۱ߊᛁℐℑℓⅠⅼ∣⏽Ⲓⵏꓲﺍﺎ１Ｉｌ￨𐊊𐌉𐌠𖼨𝐈𝐥𝐼𝑙𝑰𝒍𝓁𝓘𝓵𝔩𝕀𝕝𝕴𝖑𝖨𝗅𝗜𝗹𝘐𝘭𝙄𝙡𝙸𝚕𝚰𝛪𝜤𝝞𝞘𝟏𝟙𝟣𝟭𝟷𞣇𞸀𞺀",
	"2": "ƧϨᒿꙄꛯꝚ２𝟐𝟚𝟤𝟮𝟸",
	"3": "ƷȜЗӠⳌꝪꞫ３𑣊𖼻𝈆𝟑𝟛𝟥𝟯𝟹",
	"4": "Ꮞ４𑢯𝟒𝟜𝟦𝟰𝟺",
	"5": "Ƽ５𑢻𝟓𝟝𝟧𝟱𝟻",
	"6": "бᏮⳒ６𑣕𝟔𝟞𝟨𝟲𝟼",
	"7": "７𐓒𑣆𝈒𝟕𝟟𝟩𝟳𝟽",
	"8": "Ȣȣ৪੪ଃ８𐌚𝟖𝟠𝟪𝟴𝟾𞣋",
	"9": "৭੧୨൭ⳊꝮ９𑢬𑣌𑣖𝟗𝟡𝟫𝟵𝟿",
	"A": "4ΑАᎪᗅᴀꓮꭺＡ𐊠𖽀𝐀𝐴𝑨𝒜𝓐𝔄𝔸𝕬𝖠𝗔𝘈𝘼𝙰𝚨𝛢𝜜𝝖𝞐",
	"B": "ʙΒВвᏴᏼᗷᛒℬꓐꞴＢ𐊂𐊡𐌁𝐁𝐵𝑩𝓑𝔅𝔹𝕭𝖡𝗕𝘉𝘽𝙱𝚩𝛣𝜝𝝗𝞑",
	"C": "ϹСᏟℂℭⅭⲤꓚＣ𐊢𐌂𐐕𐔜𑣩𑣲𝐂𝐶𝑪𝒞𝓒𝕮𝖢𝗖𝘊𝘾𝙲🝌",
	"D": "ᎠᗞᗪᴅⅅⅮꓓꭰＤ𝐃𝐷𝑫𝒟𝓓𝔇𝔻𝕯𝖣𝗗𝘋𝘿𝙳",
	"E": "ΕЕᎬᴇℰ⋿ⴹꓰꭼＥ𐊆𑢦𑢮𝐄𝐸𝑬𝓔𝔈𝔼𝕰𝖤𝗘𝘌𝙀𝙴𝚬𝛦𝜠𝝚𝞔",
	"F": "ϜᖴℱꓝꞘＦ𐊇𐊥𐔥𑢢𑣂𝈓𝐅𝐹𝑭𝓕𝔉𝔽𝕱𝖥𝗙𝘍𝙁𝙵𝟊",
	"G": "ɢԌԍᏀᏳᏻꓖꮐＧ𝐆𝐺𝑮𝒢𝓖𝔊𝔾𝕲𝖦𝗚𝘎𝙂𝙶",
	"H": "ʜΗНнᎻᕼℋℌℍⲎꓧꮋＨ𐋏𝐇𝐻𝑯𝓗𝕳𝖧𝗛𝘏𝙃𝙷𝚮𝛨𝜢𝝜𝞖",
	"I": "",
	"J": "ͿЈᎫᒍᴊꓙꞲꭻＪ𝐉𝐽𝑱𝒥𝓙𝔍𝕁𝕵𝖩𝗝𝘑𝙅𝙹",
	"K": "ΚКᏦᛕKⲔꓗＫ𐔘𝐊𝐾𝑲𝒦𝓚𝔎𝕂𝕶𝖪𝗞𝘒𝙆𝙺𝚱𝛫𝜥𝝟𝞙",
	"L": "ʟᏞᒪℒⅬⳐⳑꓡꮮＬ𐐛𐑃𐔦𑢣𑢲𖼖𝈪𝐋𝐿𝑳𝓛𝔏𝕃𝕷𝖫𝗟𝘓𝙇𝙻",
	"M": "ΜϺМᎷᗰᛖℳⅯⲘꓟＭ𐊰𐌑𝐌𝑀𝑴𝓜𝔐𝕄𝕸𝖬𝗠𝘔𝙈𝙼𝚳𝛭𝜧𝝡𝞛",
	"N": "ɴΝℕⲚꓠＮ𐔓𝐍𝑁𝑵𝒩𝓝𝔑𝕹𝖭𝗡𝘕𝙉𝙽𝚴𝛮𝜨𝝢𝞜",
	"O": "0",
	"P": "ΡРᏢᑭᴘᴩℙⲢꓑꮲＰ𐊕𝐏𝑃𝑷𝒫𝓟𝔓𝕻𝖯𝗣𝘗𝙋𝙿𝚸𝛲𝜬𝝦𝞠",
	"Q": "ℚⵕＱ𝐐𝑄𝑸𝒬𝓠𝔔𝕼𝖰𝗤𝘘𝙌𝚀",
	"R": "ƦʀᎡᏒᖇᚱℛℜℝꓣꭱꮢＲ𐒴𖼵𝈖𝐑𝑅𝑹𝓡𝕽𝖱𝗥𝘙𝙍𝚁",
	"S": "$ЅՏᏕᏚꓢＳ𐊖𐐠𖼺𝐒𝑆𝑺𝒮𝓢𝔖𝕊𝕾𝖲𝗦𝘚𝙎𝚂",
	"T": "ŤΤτТтᎢᴛ⊤⟙ⲦꓔꭲＴ𐊗𐊱𐌕𑢼𖼊𝐓𝑇𝑻𝒯𝓣𝔗𝕋𝕿𝖳𝗧𝘛𝙏𝚃𝚻𝛕𝛵𝜏𝜯𝝉𝝩𝞃𝞣𝞽🝨",
	"U": "Սሀᑌ∪⋃ꓴＵ𐓎𑢸𖽂𝐔𝑈𝑼𝒰𝓤𝔘𝕌𝖀𝖴𝗨𝘜𝙐𝚄",
	"V": "Ѵ٧۷ᏙᐯⅤⴸꓦꛟＶ𐔝𑢠𖼈𝈍𝐕𝑉𝑽𝒱𝓥𝔙𝕍𝖁𝖵𝗩𝘝𝙑𝚅",
	"W": "ԜᎳᏔꓪＷ𑣦𑣯𝐖𝑊𝑾𝒲𝓦𝔚𝕎𝖂𝖶𝗪𝘞𝙒𝚆",
	"X": "ΧХ᙭ᚷⅩ╳ⲬⵝꓫꞳＸ𐊐𐊴𐌗𐌢𐔧𑣬𝐗𝑋𝑿𝒳𝓧𝔛𝕏𝖃𝖷𝗫𝘟𝙓𝚇𝚾𝛸𝜲𝝬𝞦",
	"Y": "ΥϒУҮᎩᎽⲨꓬＹ𐊲𑢤𖽃𝐘𝑌𝒀𝒴𝓨𝔜𝕐𝖄𝖸𝗬𝘠𝙔𝚈𝚼𝛶𝜰𝝪𝞤",
	"Z": "ΖᏃℤℨꓜＺ𐋵𑢩𑣥𝐙𝑍𝒁𝒵𝓩𝖅𝖹𝗭𝘡𝙕𝚉𝚭𝛧𝜡𝝛𝞕",
	"a": "@ɑαа⍺ａ𝐚𝑎𝒂𝒶𝓪𝔞𝕒𝖆𝖺𝗮𝘢𝙖𝚊𝛂𝛼𝜶𝝰𝞪",
	"b": "ƄЬᏏᖯｂ𝐛𝑏𝒃𝒷𝓫𝔟𝕓𝖇𝖻𝗯𝘣𝙗𝚋",
	"c": "ϲсᴄⅽⲥꮯｃ𐐽𝐜𝑐𝒄𝒸𝓬𝔠𝕔𝖈𝖼𝗰𝘤𝙘𝚌",
	"d": "ԁᏧᑯⅆⅾꓒｄ𝐝𝑑𝒅𝒹𝓭𝔡𝕕𝖉𝖽𝗱𝘥𝙙𝚍",
	"e": "еҽ℮ℯⅇꬲｅ𝐞𝑒𝒆𝓮𝔢𝕖𝖊𝖾𝗲𝘦𝙚𝚎",
	"f": "ſϝքẝꞙꬵｆ𝐟𝑓𝒇𝒻𝓯𝔣𝕗𝖋𝖿𝗳𝘧𝙛𝚏𝟋",
	"g": "ƍɡցᶃℊｇ𝐠𝑔𝒈𝓰𝔤𝕘𝖌𝗀𝗴𝘨𝙜𝚐",
	"h": "һհᏂℎｈ𝐡𝒉𝒽𝓱𝔥𝕙𝖍𝗁𝗵𝘩𝙝𝚑",
	"i": "ıɩɪ˛ͺιіӏᎥιℹⅈⅰ⍳ꙇꭵｉ𑣃𝐢𝑖𝒊𝒾𝓲𝔦𝕚𝖎𝗂𝗶𝘪𝙞𝚒𝚤𝛊𝜄𝜾𝝸𝞲",
	"j": "ϳјⅉｊ𝐣𝑗𝒋𝒿𝓳𝔧𝕛𝖏𝗃𝗷𝘫𝙟𝚓",
	"k": "ｋ𝐤𝑘𝒌𝓀𝓴𝔨𝕜𝖐𝗄𝗸𝘬𝙠𝚔",
	"l": "1",
	"m": "ｍ",
	"n": "ոռｎ𝐧𝑛𝒏𝓃𝓷𝔫𝕟𝖓𝗇𝗻𝘯𝙣𝚗",
	"o": "",
	"p": "ρϱр⍴ⲣｐ𝐩𝑝𝒑𝓅𝓹𝔭𝕡𝖕𝗉𝗽𝘱𝙥𝚙𝛒𝛠𝜌𝜚𝝆𝝔𝞀𝞎𝞺𝟈",
	"q": "ԛգզｑ𝐪𝑞𝒒𝓆𝓺𝔮𝕢𝖖𝗊𝗾𝘲𝙦𝚚",
	"r": "гᴦⲅꭇꭈꮁｒ𝐫𝑟𝒓𝓇𝓻𝔯𝕣𝖗𝗋𝗿𝘳𝙧𝚛",
	"s": "$ƽѕꜱꮪｓ𐑈𑣁𝐬𝑠𝒔𝓈𝓼𝔰𝕤𝖘𝗌𝘀𝘴𝙨𝚜",
	"t": "ｔ𝐭𝑡𝒕𝓉𝓽𝔱𝕥𝖙𝗍𝘁𝘵𝙩𝚝",
	"u": "ʋυսᴜꞟꭎꭒｕ𐓶𑣘𝐮𝑢𝒖𝓊𝓾𝔲𝕦𝖚𝗎𝘂𝘶𝙪𝚞𝛖𝜐𝝊𝞄𝞾",
	"v": "νѵטᴠⅴ∨⋁ꮩｖ𑜆𑣀𝐯𝑣𝒗𝓋𝓿𝔳𝕧𝖛𝗏𝘃𝘷𝙫𝚟𝛎𝜈𝝂𝝼𝞶",
	"w": "ɯѡԝաᴡꮃｗ𑜊𑜎𑜏𝐰𝑤𝒘𝓌𝔀𝔴𝕨𝖜𝗐𝘄𝘸𝙬𝚠",
	"x": "×хᕁᕽ᙮ⅹ⤫⤬⨯ｘ𝐱𝑥𝒙𝓍𝔁𝔵𝕩𝖝𝗑𝘅𝘹𝙭𝚡",
	"y": "ɣʏγуүყᶌỿℽꭚｙ𑣜𝐲𝑦𝒚𝓎𝔂𝔶𝕪𝖞𝗒𝘆𝘺𝙮𝚢𝛄𝛾𝜸𝝲𝞬",
	"z": "ᴢꮓｚ𑣄𝐳𝑧𝒛𝓏𝔃𝔷𝕫𝖟𝗓𝘇𝘻𝙯𝚣",
	"£": "₤",
	"©": "Ⓒ",
	"®": "Ⓡ"
}
```

</details>

#### Redact

Files can be redacted individually from a file path or in memory using the [`redact_file`](https://gw-engineering.github.io/glasswall-python-wrapper/libraries/word_search/word_search.html#glasswall.libraries.word_search.word_search.WordSearch.redact_file) method, or all files from a directory can be redacted using the [`redact_directory`](https://gw-engineering.github.io/glasswall-python-wrapper/libraries/word_search/word_search.html#glasswall.libraries.word_search.word_search.WordSearch.redact_directory) method.

##### Redact from file path to file path

```py
import glasswall


# Load the Glasswall WordSearch library
word_search = glasswall.WordSearch(r"C:\gwpw\libraries\10.0")

# Redact occurrences of the text "lorem" and "ipsum" within the input file, writing the redacted file to a new path
word_search.redact_file(
    input_file=r"C:\gwpw\input_redact\lorem_ipsum.docx",
    output_file=r"C:\gwpw\output\word_search\redact_f2f\lorem_ipsum.docx",
    content_management_policy=glasswall.content_management.policies.WordSearch(
        config={
            "textSearchConfig": {
                "@libVersion": "core2",
                "textList": [
                    {"name": "textItem", "switches": [
                        {"name": "text", "value": "lorem"},
                        {"name": "textSetting", "@replacementChar": "*", "value": "redact"},
                    ]},
                    {"name": "textItem", "switches": [
                        {"name": "text", "value": "ipsum"},
                        {"name": "textSetting", "@replacementChar": "*", "value": "redact"},
                    ]},
                ]
            }
        }
    )
)

```

##### Redact from file path to memory

`redact_file` returns an object with the attributes: "status" (int), "output_file" (bytes), "output_report" (bytes). The below example demonstrates assigning the variable `result` and checking the contents of the beginning of the redacted output_file and the output_report.

```py
import glasswall


# Load the Glasswall WordSearch library
word_search = glasswall.WordSearch(r"C:\gwpw\libraries\10.0")

# Redact occurrences of the text "lorem" and "ipsum" within the input file, writing the redacted file to a new path
result = word_search.redact_file(
    input_file=r"C:\gwpw\input_redact\lorem_ipsum.docx",
    output_file=None,
    content_management_policy=glasswall.content_management.policies.WordSearch(
        config={
            "textSearchConfig": {
                "@libVersion": "core2",
                "textList": [
                    {"name": "textItem", "switches": [
                        {"name": "text", "value": "lorem"},
                        {"name": "textSetting", "@replacementChar": "*", "value": "redact"},
                    ]},
                    {"name": "textItem", "switches": [
                        {"name": "text", "value": "ipsum"},
                        {"name": "textSetting", "@replacementChar": "*", "value": "redact"},
                    ]},
                ]
            }
        }
    )
)

assert result.output_file[:6] == b'PK\x03\x04\x14\x00'
assert result.output_report[:500] == b'<gw:WordSearchStatistics xmlns:gw="http://glasswall.com/namespace">\n\t<gw:DocumentSummary>\n\t\t<gw:TotalSizeInBytes>14292</gw:TotalSizeInBytes>\n\t\t<gw:FileType>docx</gw:FileType>\n\t\t<gw:TotalItemMatchCount>14</gw:TotalItemMatchCount>\n\t</gw:DocumentSummary>\n\t<gw:WordItem>\n\t\t<gw:Name>ipsum</gw:Name>\n\t\t<gw:ItemMatchCount>8</gw:ItemMatchCount>\n\t\t<gw:Locations>\n\t\t\t<gw:Location>\n\t\t\t\t<gw:Offset>120</gw:Offset>\n\t\t\t\t<gw:Page>0</gw:Page>\n\t\t\t\t<gw:Paragraph>0</gw:Paragraph>\n\t\t\t</gw:Location>\n\t\t\t<gw:Location>\n\t\t\t'

```

##### Redact from memory

```py
import glasswall


# Load the Glasswall WordSearch library
word_search = glasswall.WordSearch(r"C:\gwpw\libraries\10.0")

# Read file from disk to memory
with open(r"C:\gwpw\input_redact\lorem_ipsum.docx", "rb") as f:
    input_bytes = f.read()

# Redact occurrences of the text "lorem" and "ipsum" within the input file, writing the redacted file to a new path
result = word_search.redact_file(
    input_file=input_bytes,
    output_file=r"C:\gwpw\output\word_search\redact_m2f\lorem_ipsum.docx",
    content_management_policy=glasswall.content_management.policies.WordSearch(
        config={
            "textSearchConfig": {
                "@libVersion": "core2",
                "textList": [
                    {"name": "textItem", "switches": [
                        {"name": "text", "value": "lorem"},
                        {"name": "textSetting", "@replacementChar": "*", "value": "redact"},
                    ]},
                    {"name": "textItem", "switches": [
                        {"name": "text", "value": "ipsum"},
                        {"name": "textSetting", "@replacementChar": "*", "value": "redact"},
                    ]},
                ]
            }
        }
    )
)

assert result.output_file[:6] == b'PK\x03\x04\x14\x00'
assert result.output_report[:500] == b'<gw:WordSearchStatistics xmlns:gw="http://glasswall.com/namespace">\n\t<gw:DocumentSummary>\n\t\t<gw:TotalSizeInBytes>14292</gw:TotalSizeInBytes>\n\t\t<gw:FileType>docx</gw:FileType>\n\t\t<gw:TotalItemMatchCount>14</gw:TotalItemMatchCount>\n\t</gw:DocumentSummary>\n\t<gw:WordItem>\n\t\t<gw:Name>ipsum</gw:Name>\n\t\t<gw:ItemMatchCount>8</gw:ItemMatchCount>\n\t\t<gw:Locations>\n\t\t\t<gw:Location>\n\t\t\t\t<gw:Offset>120</gw:Offset>\n\t\t\t\t<gw:Page>0</gw:Page>\n\t\t\t\t<gw:Paragraph>0</gw:Paragraph>\n\t\t\t</gw:Location>\n\t\t\t<gw:Location>\n\t\t\t'

```

##### Redact files in a directory

`redact_directory` returns a dictionary of file paths relative to the input_directory, and an object with the attributes: "status" (int), "output_file" (bytes), "output_report" (bytes). The below example demonstrates assigning the variable `results` and checking the keys and values of the `results` dictionary.

```py
import glasswall


# Load the Glasswall WordSearch library
word_search = glasswall.WordSearch(r"C:\gwpw\libraries\10.0")

# Redact occurrences of the text "lorem" and "ipsum" within each file in the input_directory, writing the redacted file
# to a new path in the output_directory
results = word_search.redact_directory(
    input_directory=r"C:\gwpw\input_redact",
    output_directory=r"C:\gwpw\output\word_search\redact_directory",
    content_management_policy=glasswall.content_management.policies.WordSearch(
        config={
            "textSearchConfig": {
                "@libVersion": "core2",
                "textList": [
                    {"name": "textItem", "switches": [
                        {"name": "text", "value": "lorem"},
                        {"name": "textSetting", "@replacementChar": "*", "value": "redact"},
                    ]},
                    {"name": "textItem", "switches": [
                        {"name": "text", "value": "ipsum"},
                        {"name": "textSetting", "@replacementChar": "*", "value": "redact"},
                    ]},
                ]
            }
        }
    )
)

assert list(results.keys()) == ['lorem_ipsum.docx', 'lorem_ipsum.pptx']
assert all(result.status == 1 for result in results.values())

```

##### Redact files in a directory that may contain unsupported file types

The default behaviour of the Glasswall Python wrapper is to raise the relevant exception (see: [glasswall.libraries.word_search.errors](https://gw-engineering.github.io/glasswall-python-wrapper/libraries/word_search/errors.html)) if processing fails. Passing `raise_unsupported=False` will prevent an exception being raised and can be useful when working with a directory containing a mixture of both supported and unsupported file types when it is desired to process as many of the files as possible instead of terminating on the first failure.

The below example input directory contains the same two files in the above example as well as a file with an unsupported file format: `python-package.yml`. We can inspect the key value pairs in the `results` dictionary and see that the object returned for the `python-package.yml` file returned a `status: 0`, a failure. The `output_file` attribute is empty bytes, and the `output_report` bytes is populated with a report that includes an `IssueItem` describing the problems encountered while attempting to redact the file: `File contents could not be accessed`.

```py
import glasswall


# Load the Glasswall WordSearch library
word_search = glasswall.WordSearch(r"C:\gwpw\libraries\10.0")

# Redact occurrences of the text "lorem" and "ipsum" within each file in the input_directory, writing the redacted file
# to a new path in the output_directory
results = word_search.redact_directory(
    input_directory=r"C:\gwpw\input_redact_with_unsupported_file_types",
    output_directory=r"C:\gwpw\output\word_search\redact_directory_unsupported",
    content_management_policy=glasswall.content_management.policies.WordSearch(
        config={
            "textSearchConfig": {
                "@libVersion": "core2",
                "textList": [
                    {"name": "textItem", "switches": [
                        {"name": "text", "value": "lorem"},
                        {"name": "textSetting", "@replacementChar": "*", "value": "redact"},
                    ]},
                    {"name": "textItem", "switches": [
                        {"name": "text", "value": "ipsum"},
                        {"name": "textSetting", "@replacementChar": "*", "value": "redact"},
                    ]},
                ]
            }
        }
    ),
    raise_unsupported=False
)

assert list(results.keys()) == ["lorem_ipsum.docx", "lorem_ipsum.pptx", "python-package.yml"]
assert [result.status for result in results.values()] == [1, 1, 0]

print(results["python-package.yml"].__dict__)
# {'status': 0,
# 'output_file': b'',
# 'output_report': b'<gw:WordSearchStatistics xmlns:gw="http://glasswall.com/namespace">\n\t<gw:IssueItem>\n\t\t<gw:Description>File contents could not be accessed</gw:Description>\n\t</gw:IssueItem>\n\t<gw:DocumentSummary>\n\t\t<gw:TotalSizeInBytes>1460</gw:TotalSizeInBytes>\n\t\t<gw:FileType>Unknown</gw:FileType>\n\t\t<gw:TotalItemMatchCount>0</gw:TotalItemMatchCount>\n\t</gw:DocumentSummary>\n\t<gw:WordItem>\n\t\t<gw:Name>ipsum</gw:Name>\n\t\t<gw:ItemMatchCount>0</gw:ItemMatchCount>\n\t\t<gw:Locations/>\n\t</gw:WordItem>\n\t<gw:WordItem>\n\t\t<gw:Name>lorem</gw:Name>\n\t\t<gw:ItemMatchCount>0</gw:ItemMatchCount>\n\t\t<gw:Locations/>\n\t</gw:WordItem>\n</gw:WordSearchStatistics>\n\n'}

```

##### Redact files in a directory conditionally based on file format

The example below demonstrates redacting of only docx and pptx files from a directory that also contains other unsupported file types.

```py
import os

import glasswall


# Load the Glasswall Editor library
editor = glasswall.Editor(r"C:\gwpw\libraries\10.0")

# Load the Glasswall WordSearch library
word_search = glasswall.WordSearch(r"C:\gwpw\libraries\10.0")

input_directory = r"C:\gwpw\input_redact_with_unsupported_file_types"
output_directory = r"C:\gwpw\output\word_search\redact_directory_file_format"

# Iterate relative file paths from input_directory
for relative_file in glasswall.utils.list_file_paths(input_directory, absolute=False):
    # Construct absolute paths
    input_file = os.path.join(input_directory, relative_file)
    output_file = os.path.join(output_directory, relative_file)

    # Get the file type of the file
    file_type = editor.determine_file_type(
        input_file=input_file,
        as_string=True,
        raise_unsupported=False
    )

    # Protect only doc and docx files
    if file_type in ["docx", "pptx"]:
        # Redact occurrences of the text "lorem" and "ipsum" within the input file, writing the redacted file to a new path
        word_search.redact_file(
            input_file=input_file,
            output_file=output_file,
            content_management_policy=glasswall.content_management.policies.WordSearch(
                config={
                    "textSearchConfig": {
                        "@libVersion": "core2",
                        "textList": [
                            {"name": "textItem", "switches": [
                                {"name": "text", "value": "lorem"},
                                {"name": "textSetting", "@replacementChar": "*", "value": "redact"},
                            ]},
                            {"name": "textItem", "switches": [
                                {"name": "text", "value": "ipsum"},
                                {"name": "textSetting", "@replacementChar": "*", "value": "redact"},
                            ]},
                        ]
                    }
                }
            )
        )

```