

import ctypes as ct
import io
import os
from typing import Union

import glasswall
from glasswall import determine_file_type as dft
from glasswall import utils
from glasswall.config.logging import log
from glasswall.libraries.library import Library
from glasswall.libraries.rebuild import errors, successes


class Rebuild(Library):
    """ A high level Python wrapper for Glasswall Rebuild / Classic. """

    def __init__(self, library_path: str):
        super().__init__(library_path=library_path)
        self.library = self.load_library(os.path.abspath(library_path))

        # Set content management configuration to default
        self.set_content_management_policy(input_file=None)

        # Validate killswitch has not activated
        self.validate_license()

        log.info(f"Loaded Glasswall {self.__class__.__name__} version {self.version()} from {self.library_path}")

    def validate_license(self):
        """ Validates the license of the library by attempting to call protect_file on a known supported file.

        Raises:
            RebuildError: If the license could not be validated.
        """
        # Call protect file on a known good bitmap to see if license has expired
        try:
            self.protect_file(
                input_file=b"BM:\x00\x00\x00\x00\x00\x00\x006\x00\x00\x00(\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\x00",
                raise_unsupported=True
            )
            log.debug(f"{self.__class__.__name__} license validated successfully.")
        except errors.RebuildError:
            log.warning(f"{self.__class__.__name__} license validation failed.")
            raise

    def version(self):
        """ Returns the Glasswall library version.

        Returns:
            version (str): The Glasswall library version.
        """

        # Declare the return type
        self.library.GWFileVersion.restype = ct.c_wchar_p

        # API call
        version = self.library.GWFileVersion()

        return version

    def determine_file_type(self, input_file: Union[str, bytes, bytearray, io.BytesIO], as_string: bool = False):
        """ Returns an int representing the file type / file format of a file.

        Args:
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The input file, can be a local path.
            as_string (bool, optional): Return file type as string, eg: "bmp" instead of: 29. Defaults to False.

        Returns:
            file_type (Union[int, str]): The file format.
        """

        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)

            self.library.GWDetermineFileTypeFromFile.argtypes = [ct.c_wchar_p]
            self.library.GWDetermineFileTypeFromFile.restype = ct.c_int

            # convert to ct.c_wchar_p
            ct_input_file = ct.c_wchar_p(input_file)

            # API call
            file_type = self.library.GWDetermineFileTypeFromFile(ct_input_file)

        elif isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            self.library.GWDetermineFileTypeFromFileInMem.argtypes = [ct.c_char_p, ct.c_size_t]
            self.library.GWDetermineFileTypeFromFileInMem.restype = ct.c_int

            # convert to bytes
            bytes_input_file = utils.as_bytes(input_file)

            # ctypes conversion
            ct_input_buffer = ct.c_char_p(bytes_input_file)
            ct_butter_length = ct.c_size_t(len(bytes_input_file))

            # API call
            file_type = self.library.GWDetermineFileTypeFromFileInMem(
                ct_input_buffer,
                ct_butter_length
            )

        file_type_as_string = dft.file_type_int_to_str(file_type)
        input_file_repr = f"{type(input_file)} length {len(input_file)}" if isinstance(input_file, (bytes, bytearray,)) else input_file.__sizeof__() if isinstance(input_file, io.BytesIO) else input_file

        if not dft.is_success(file_type):
            log.warning(f"\n\tfile_type: {file_type}\n\tfile_type_as_string: {file_type_as_string}\n\tinput_file: {input_file_repr}")
            raise dft.int_class_map.get(file_type, dft.errors.UnknownErrorCode)(file_type)
        else:
            log.debug(f"\n\tfile_type: {file_type}\n\tfile_type_as_string: {file_type_as_string}\n\tinput_file: {input_file_repr}")

        if as_string:
            return file_type_as_string

        return file_type

    def get_content_management_policy(self):
        """ Gets the current content management configuration.

        Returns:
            xml_string (str): The XML string of the current content management configuration.
        """

        # Declare argument types
        self.library.GWFileConfigGet.argtypes = [
            ct.POINTER(ct.POINTER(ct.c_wchar)),
            ct.POINTER(ct.c_size_t)
        ]

        # Variable initialisation
        ct_input_buffer = ct.POINTER(ct.c_wchar)()
        ct_input_size = ct.c_size_t(0)

        # API call
        status = self.library.GWFileConfigGet(
            ct.byref(ct_input_buffer),
            ct.byref(ct_input_size)
        )

        if status not in successes.success_codes:
            log.warning(f"\n\tstatus: {status}")
            raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
        else:
            log.debug(f"\n\tstatus: {status}")

        # As string
        xml_string = utils.validate_xml(ct.wstring_at(ct_input_buffer))

        return xml_string

    def set_content_management_policy(self, input_file: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None):
        """ Sets the content management policy configuration. If input_file is None then default settings (sanitise) are applied.

        Args:
            input_file (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): Default None (sanitise). The content management policy to apply.

        Returns:
            status (int): The result of the Glasswall API call.
        """
        # Validate type
        if not isinstance(input_file, (type(None), str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            raise TypeError(input_file)

        # self.library.GWFileConfigRevertToDefaults doesn't work, load default instead
        # Set input_file to default if input_file is None
        if input_file is None:
            input_file = glasswall.content_management.policies.Rebuild(default="sanitise")

        # Validate xml content is parsable
        xml_string = utils.validate_xml(input_file)

        # Declare argument types
        self.library.GWFileConfigXML.argtypes = [ct.c_wchar_p]

        # API call
        status = self.library.GWFileConfigXML(
            ct.c_wchar_p(xml_string)
        )

        if status not in successes.success_codes:
            log.warning(f"\n\tstatus: {status}")
            raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
        else:
            log.debug(f"\n\tstatus: {status}")

        return status

    def protect_file(self, input_file: Union[str, bytes, bytearray, io.BytesIO], output_file: Union[None, str] = None, content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None, raise_unsupported: bool = True):
        """ Protects a file using the current content management configuration, returning the file bytes. The protected file is written to output_file if it is provided.

        Args:
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The input file path or bytes.
            output_file (Union[None, str], optional): The output file path where the protected file will be written.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): The content management policy to apply.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            file_bytes (bytes): The protected file bytes.
        """
        # Validate arg types
        if not isinstance(input_file, (str, bytes, bytearray, io.BytesIO)):
            raise TypeError(input_file)
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)
        if not isinstance(content_management_policy, (type(None), str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            raise TypeError(content_management_policy)
        if not isinstance(raise_unsupported, bool):
            raise TypeError(raise_unsupported)

        # Convert string path arguments to absolute paths
        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)
            input_file = os.path.abspath(input_file)
        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)
            # make directories that do not exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        if isinstance(content_management_policy, str) and os.path.isfile(content_management_policy):
            content_management_policy = os.path.abspath(content_management_policy)

        # Check that file type is supported
        try:
            file_type = self.determine_file_type(input_file=input_file)
        except dft.errors.FileTypeEnumError:
            if raise_unsupported:
                raise
            else:
                return None

        # Convert memory inputs to bytes
        if isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            input_file = utils.as_bytes(input_file)

        with utils.CwdHandler(self.library_path):
            # Set content management policy
            if content_management_policy:
                self.set_content_management_policy(content_management_policy)

            # file to file
            if isinstance(input_file, str) and isinstance(output_file, str):
                # API function declaration
                self.library.GWFileToFileProtect.argtypes = [
                    ct.c_wchar_p,
                    ct.c_wchar_p,
                    ct.c_wchar_p
                ]

                # Variable initialisation
                ct_input_file = ct.c_wchar_p(input_file)
                ct_file_type = ct.c_wchar_p(dft.file_type_int_to_str(file_type))
                ct_output_file = ct.c_wchar_p(output_file)

                # API call
                status = self.library.GWFileToFileProtect(
                    ct_input_file,
                    ct_file_type,
                    ct_output_file
                )

            # file to memory
            elif isinstance(input_file, str) and output_file is None:
                # API function declaration
                self.library.GWFileProtect.argtypes = [
                    ct.c_wchar_p,
                    ct.c_wchar_p,
                    ct.POINTER(ct.c_void_p),
                    ct.POINTER(ct.c_size_t)
                ]

                # Variable initialisation
                ct_input_file = ct.c_wchar_p(input_file)
                ct_file_type = ct.c_wchar_p(dft.file_type_int_to_str(file_type))
                ct_output_buffer = ct.c_void_p(0)
                ct_output_size = ct.c_size_t(0)

                # API call
                status = self.library.GWFileProtect(
                    ct_input_file,
                    ct_file_type,
                    ct.byref(ct_output_buffer),
                    ct.byref(ct_output_size)
                )

            # memory to memory and memory to file
            elif isinstance(input_file, bytes):
                # API function declaration
                self.library.GWMemoryToMemoryProtect.argtypes = [
                    ct.c_void_p,
                    ct.c_size_t,
                    ct.c_wchar_p,
                    ct.POINTER(ct.c_void_p),
                    ct.POINTER(ct.c_size_t)
                ]

                # Variable initialization
                bytearray_buffer = bytearray(input_file)
                ct_input_buffer = (ct.c_ubyte * len(bytearray_buffer)).from_buffer(bytearray_buffer)
                ct_input_size = ct.c_size_t(len(input_file))
                ct_file_type = ct.c_wchar_p(dft.file_type_int_to_str(file_type))
                ct_output_buffer = ct.c_void_p(0)
                ct_output_size = ct.c_size_t(0)

                status = self.library.GWMemoryToMemoryProtect(
                    ct_input_buffer,
                    ct_input_size,
                    ct_file_type,
                    ct.byref(ct_output_buffer),
                    ct.byref(ct_output_size)
                )

            input_file_repr = f"{type(input_file)} length {len(input_file)}" if isinstance(input_file, (bytes, bytearray,)) else input_file.__sizeof__() if isinstance(input_file, io.BytesIO) else input_file
            if status not in successes.success_codes:
                log.warning(f"\n\tstatus: {status}\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}")
                if raise_unsupported:
                    raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
                else:
                    file_bytes = None
            else:
                log.debug(f"\n\tstatus: {status}\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}")
                if isinstance(input_file, str) and isinstance(output_file, str):
                    # file to file, read the bytes of the file that Rebuild has already written
                    if not os.path.isfile(output_file):
                        log.warning(f"Rebuild returned success code: {status} and no output file was found: {output_file}")
                        file_bytes = None
                    else:
                        with open(output_file, "rb") as f:
                            file_bytes = f.read()
                else:
                    # file to memory, memory to memory
                    file_bytes = utils.buffer_to_bytes(
                        ct_output_buffer,
                        ct_output_size
                    )
                    if isinstance(output_file, str):
                        # memory to file
                        # no Rebuild function exists for memory to file, write the memory to file ourselves
                        with open(output_file, "wb") as f:
                            f.write(file_bytes)

            return file_bytes

    def protect_directory(self, input_directory: str, output_directory: Union[None, str], content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None, raise_unsupported: bool = True):
        """ Recursively processes all files in a directory in protect mode using the given content management policy.
        The protected files are written to output_directory maintaining the same directory structure as input_directory.

        Args:
            input_directory (str): The input directory containing files to protect.
            output_directory (Union[None, str]): The output directory where the protected file will be written, or None to not write files.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): Default None (sanitise). The content management policy to apply.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            protected_files_dict (dict): A dictionary of file paths relative to input_directory, and file bytes.
        """
        protected_files_dict = {}
        # Call protect_file on each file in input_directory to output_directory
        for input_file in utils.list_file_paths(input_directory):
            relative_path = os.path.relpath(input_file, input_directory)
            output_file = None if output_directory is None else os.path.join(os.path.abspath(output_directory), relative_path)

            protected_bytes = self.protect_file(
                input_file=input_file,
                output_file=output_file,
                raise_unsupported=raise_unsupported,
                content_management_policy=content_management_policy,
            )

            protected_files_dict[relative_path] = protected_bytes

        return protected_files_dict

    def analyse_file(self, input_file: Union[str, bytes, bytearray, io.BytesIO], output_file: Union[None, str] = None, content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None, raise_unsupported: bool = True):
        """ Analyses a file, returning the analysis bytes. The analysis is written to output_file if it is provided.

        Args:
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The input file path or bytes.
            output_file (Union[None, str], optional): The output file path where the analysis file will be written.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): The content management policy to apply.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            file_bytes (bytes): The analysis file bytes.
        """
        # Validate arg types
        if not isinstance(input_file, (str, bytes, bytearray, io.BytesIO)):
            raise TypeError(input_file)
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)
        if not isinstance(content_management_policy, (type(None), str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            raise TypeError(content_management_policy)
        if not isinstance(raise_unsupported, bool):
            raise TypeError(raise_unsupported)

        # Convert string path arguments to absolute paths
        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)
            input_file = os.path.abspath(input_file)
        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)
            # make directories that do not exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        if isinstance(content_management_policy, str) and os.path.isfile(content_management_policy):
            content_management_policy = os.path.abspath(content_management_policy)

        # Check that file type is supported
        try:
            file_type = self.determine_file_type(input_file=input_file)
        except dft.errors.FileTypeEnumError:
            if raise_unsupported:
                raise
            else:
                return None

        # Convert memory inputs to bytes
        if isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            input_file = utils.as_bytes(input_file)

        with utils.CwdHandler(self.library_path):
            # Set content management policy
            self.set_content_management_policy(content_management_policy)

            # file to file
            if isinstance(input_file, str) and isinstance(output_file, str):
                # API function declaration
                self.library.GWFileToFileAnalysisAudit.argtypes = [
                    ct.c_wchar_p,
                    ct.c_wchar_p,
                    ct.c_wchar_p
                ]

                # Variable initialisation
                ct_input_file = ct.c_wchar_p(input_file)
                ct_file_type = ct.c_wchar_p(dft.file_type_int_to_str(file_type))
                ct_output_file = ct.c_wchar_p(output_file)

                # API call
                status = self.library.GWFileToFileAnalysisAudit(
                    ct_input_file,
                    ct_file_type,
                    ct_output_file
                )

            # file to memory
            elif isinstance(input_file, str) and output_file is None:
                # API function declaration
                self.library.GWFileAnalysisAudit.argtypes = [
                    ct.c_wchar_p,
                    ct.c_wchar_p,
                    ct.POINTER(ct.c_void_p),
                    ct.POINTER(ct.c_size_t)
                ]

                # Variable initialisation
                ct_input_file = ct.c_wchar_p(input_file)
                ct_file_type = ct.c_wchar_p(dft.file_type_int_to_str(file_type))
                ct_output_buffer = ct.c_void_p(0)
                ct_output_size = ct.c_size_t(0)

                # API call
                status = self.library.GWFileAnalysisAudit(
                    ct_input_file,
                    ct_file_type,
                    ct.byref(ct_output_buffer),
                    ct.byref(ct_output_size)
                )

            # memory to memory and memory to file
            elif isinstance(input_file, bytes):
                # API function declaration
                self.library.GWMemoryToMemoryAnalysisAudit.argtypes = [
                    ct.c_void_p,
                    ct.c_size_t,
                    ct.c_wchar_p,
                    ct.POINTER(ct.c_void_p),
                    ct.POINTER(ct.c_size_t)
                ]

                # Variable initialization
                bytearray_buffer = bytearray(input_file)
                ct_input_buffer = (ct.c_ubyte * len(bytearray_buffer)).from_buffer(bytearray_buffer)
                ct_input_size = ct.c_size_t(len(input_file))
                ct_file_type = ct.c_wchar_p(dft.file_type_int_to_str(file_type))
                ct_output_buffer = ct.c_void_p(0)
                ct_output_size = ct.c_size_t(0)

                status = self.library.GWMemoryToMemoryAnalysisAudit(
                    ct.byref(ct_input_buffer),
                    ct_input_size,
                    ct_file_type,
                    ct.byref(ct_output_buffer),
                    ct.byref(ct_output_size)
                )

            if isinstance(input_file, str) and isinstance(output_file, str):
                # file to file, read the bytes of the file that Rebuild has already written
                if not os.path.isfile(output_file):
                    log.warning(f"Rebuild returned success code: {status} and no output file was found: {output_file}")
                    file_bytes = None
                else:
                    with open(output_file, "rb") as f:
                        file_bytes = f.read()
            else:
                # file to memory, memory to memory
                file_bytes = utils.buffer_to_bytes(
                    ct_output_buffer,
                    ct_output_size
                )
                if isinstance(output_file, str):
                    # memory to file
                    # no Rebuild function exists for memory to file, write the memory to file ourselves
                    with open(output_file, "wb") as f:
                        f.write(file_bytes)

            input_file_repr = f"{type(input_file)} length {len(input_file)}" if isinstance(input_file, (bytes, bytearray,)) else input_file.__sizeof__() if isinstance(input_file, io.BytesIO) else input_file
            if status not in successes.success_codes:
                log.warning(f"\n\tstatus: {status}\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}")
                if raise_unsupported:
                    raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
            else:
                log.debug(f"\n\tstatus: {status}\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}")

            return file_bytes

    def analyse_directory(self, input_directory: str, output_directory: Union[None, str], content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None, raise_unsupported: bool = True):
        """ Analyses all files in a directory and its subdirectories. The analysis files are written to output_directory maintaining the same directory structure as input_directory.

        Args:
            input_directory (str): The input directory containing files to analyse.
            output_directory (Union[None, str]): The output directory where the analysis files will be written, or None to not write files.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): Default None (sanitise). The content management policy to apply.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            analysis_files_dict (dict): A dictionary of file paths relative to input_directory, and file bytes.
        """
        analysis_files_dict = {}
        # Call analyse_file on each file in input_directory to output_directory
        for input_file in utils.list_file_paths(input_directory):
            relative_path = os.path.relpath(input_file, input_directory) + ".xml"
            output_file = None if output_directory is None else os.path.join(os.path.abspath(output_directory), relative_path)

            analysis_bytes = self.analyse_file(
                input_file=input_file,
                output_file=output_file,
                raise_unsupported=raise_unsupported,
                content_management_policy=content_management_policy,
            )

            analysis_files_dict[relative_path] = analysis_bytes

        return analysis_files_dict

    def export_file(self, input_file: Union[str, bytes, bytearray, io.BytesIO], output_file: Union[None, str] = None, content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None, raise_unsupported: bool = True):
        """ Export a file, returning the .zip file bytes. The .zip file is written to output_file.

        Args:
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The input file path or bytes.
            output_file (Union[None, str], optional): The output file path where the .zip file will be written.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): The content management policy to apply.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            file_bytes (bytes): The exported .zip file.
        """
        # Validate arg types
        if not isinstance(input_file, (str, bytes, bytearray, io.BytesIO)):
            raise TypeError(input_file)
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)
        if not isinstance(content_management_policy, (type(None), str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            raise TypeError(content_management_policy)
        if not isinstance(raise_unsupported, bool):
            raise TypeError(raise_unsupported)

        # Convert string path arguments to absolute paths
        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)
            input_file = os.path.abspath(input_file)
        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)
            # make directories that do not exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        if isinstance(content_management_policy, str) and os.path.isfile(content_management_policy):
            content_management_policy = os.path.abspath(content_management_policy)

        # Check that file type is supported
        try:
            self.determine_file_type(input_file=input_file)
        except dft.errors.FileTypeEnumError:
            if raise_unsupported:
                raise
            else:
                return None

        # Convert memory inputs to bytes
        if isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            input_file = utils.as_bytes(input_file)

        with utils.CwdHandler(self.library_path):
            # Set content management policy
            self.set_content_management_policy(content_management_policy)

            # file to file
            if isinstance(input_file, str) and isinstance(output_file, str):
                # API function declaration
                self.library.GWFileToFileAnalysisProtectAndExport.argtypes = [
                    ct.c_wchar_p,
                    ct.c_wchar_p
                ]

                # Variable initialisation
                ct_input_file = ct.c_wchar_p(input_file)
                ct_output_file = ct.c_wchar_p(output_file)

                # API call
                status = self.library.GWFileToFileAnalysisProtectAndExport(
                    ct_input_file,
                    ct_output_file
                )

            # file to memory
            elif isinstance(input_file, str) and output_file is None:
                # API function declaration
                self.library.GWFileToMemoryAnalysisProtectAndExport.argtypes = [
                    ct.c_wchar_p,
                    ct.POINTER(ct.c_void_p),
                    ct.POINTER(ct.c_size_t)
                ]

                # Variable initialisation
                ct_input_file = ct.c_wchar_p(input_file)
                ct_output_buffer = ct.c_void_p(0)
                ct_output_size = ct.c_size_t(0)

                # API call
                status = self.library.GWFileToMemoryAnalysisProtectAndExport(
                    ct_input_file,
                    ct.byref(ct_output_buffer),
                    ct.byref(ct_output_size)
                )

            # memory to memory and memory to file
            elif isinstance(input_file, bytes):
                # API function declaration
                self.library.GWMemoryToMemoryAnalysisProtectAndExport.argtypes = [
                    ct.c_void_p,
                    ct.c_size_t,
                    ct.POINTER(ct.c_void_p),
                    ct.POINTER(ct.c_size_t)
                ]

                # Variable initialization
                bytearray_buffer = bytearray(input_file)
                ct_input_buffer = (ct.c_ubyte * len(bytearray_buffer)).from_buffer(bytearray_buffer)
                ct_input_size = ct.c_size_t(len(input_file))
                ct_output_buffer = ct.c_void_p(0)
                ct_output_size = ct.c_size_t(0)

                status = self.library.GWMemoryToMemoryAnalysisProtectAndExport(
                    ct_input_buffer,
                    ct_input_size,
                    ct.byref(ct_output_buffer),
                    ct.byref(ct_output_size)
                )

            input_file_repr = f"{type(input_file)} length {len(input_file)}" if isinstance(input_file, (bytes, bytearray,)) else input_file.__sizeof__() if isinstance(input_file, io.BytesIO) else input_file
            if status not in successes.success_codes:
                log.warning(f"\n\tstatus: {status}\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}")
                if raise_unsupported:
                    raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
                else:
                    file_bytes = None
            else:
                log.debug(f"\n\tstatus: {status}\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}")
                if isinstance(input_file, str) and isinstance(output_file, str):
                    # file to file, read the bytes of the file that Rebuild has already written
                    if not os.path.isfile(output_file):
                        log.warning(f"Rebuild returned success code: {status} and no output file was found: {output_file}")
                        file_bytes = None
                    else:
                        with open(output_file, "rb") as f:
                            file_bytes = f.read()
                else:
                    # file to memory, memory to memory
                    file_bytes = utils.buffer_to_bytes(
                        ct_output_buffer,
                        ct_output_size
                    )
                    if isinstance(output_file, str):
                        # memory to file
                        # no Rebuild function exists for memory to file, write the memory to file ourselves
                        with open(output_file, "wb") as f:
                            f.write(file_bytes)

            return file_bytes

    def export_directory(self, input_directory: str, output_directory: Union[None, str], content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None, raise_unsupported: bool = True):
        """ Exports all files in a directory and its subdirectories. The export files are written to output_directory maintaining the same directory structure as input_directory.

        Args:
            input_directory (str): The input directory containing files to export.
            output_directory (Union[None, str]): The output directory where the export files will be written, or None to not write files.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): Default None (sanitise). The content management policy to apply.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            export_files_dict (dict): A dictionary of file paths relative to input_directory, and file bytes.
        """
        export_files_dict = {}
        # Call export_file on each file in input_directory to output_directory
        for input_file in utils.list_file_paths(input_directory):
            relative_path = os.path.relpath(input_file, input_directory) + ".zip"
            output_file = None if output_directory is None else os.path.join(os.path.abspath(output_directory), relative_path)

            export_bytes = self.export_file(
                input_file=input_file,
                output_file=output_file,
                raise_unsupported=raise_unsupported,
                content_management_policy=content_management_policy,
            )

            export_files_dict[relative_path] = export_bytes

        return export_files_dict

    def import_file(self, input_file: Union[str, bytes, bytearray, io.BytesIO], output_file: Union[None, str] = None, content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None, raise_unsupported: bool = True):
        """ Import a .zip file, constructs a file from the .zip file and returns the file bytes. The file is written to output_file if it is provided.

        Args:
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The .zip input file path or bytes.
            output_file (Union[None, str], optional): The output file path where the constructed file will be written.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): The content management policy to apply to the session.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            file_bytes (bytes): The imported file bytes.
        """
        # Validate arg types
        if not isinstance(input_file, (str, bytes, bytearray, io.BytesIO)):
            raise TypeError(input_file)
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)
        if not isinstance(content_management_policy, (type(None), str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            raise TypeError(content_management_policy)
        if not isinstance(raise_unsupported, bool):
            raise TypeError(raise_unsupported)

        # Convert string path arguments to absolute paths
        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)
            input_file = os.path.abspath(input_file)
        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)
            # make directories that do not exist
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        if isinstance(content_management_policy, str) and os.path.isfile(content_management_policy):
            content_management_policy = os.path.abspath(content_management_policy)

        # Check that file type is supported
        try:
            self.determine_file_type(input_file=input_file)
        except dft.errors.FileTypeEnumError:
            if raise_unsupported:
                raise
            else:
                return None

        # Convert memory inputs to bytes
        if isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            input_file = utils.as_bytes(input_file)

        with utils.CwdHandler(self.library_path):
            # Set content management policy
            self.set_content_management_policy(content_management_policy)

            # file to file
            if isinstance(input_file, str) and isinstance(output_file, str):
                # API function declaration
                self.library.GWFileToFileProtectAndImport.argtypes = [
                    ct.c_wchar_p,
                    ct.c_wchar_p
                ]

                # Variable initialisation
                ct_input_file = ct.c_wchar_p(input_file)
                ct_output_file = ct.c_wchar_p(output_file)

                # API call
                status = self.library.GWFileToFileProtectAndImport(
                    ct_input_file,
                    ct_output_file
                )

            # file to memory
            elif isinstance(input_file, str) and output_file is None:
                # API function declaration
                self.library.GWFileToMemoryProtectAndImport.argtypes = [
                    ct.c_wchar_p,
                    ct.POINTER(ct.c_void_p),
                    ct.POINTER(ct.c_size_t)
                ]

                # Variable initialisation
                ct_input_file = ct.c_wchar_p(input_file)
                ct_output_buffer = ct.c_void_p(0)
                ct_output_size = ct.c_size_t(0)

                # API call
                status = self.library.GWFileToMemoryProtectAndImport(
                    ct_input_file,
                    ct.byref(ct_output_buffer),
                    ct.byref(ct_output_size)
                )

            # memory to memory and memory to file
            elif isinstance(input_file, bytes):
                # API function declaration
                self.library.GWMemoryToMemoryProtectAndImport.argtypes = [
                    ct.c_void_p,
                    ct.c_size_t,
                    ct.POINTER(ct.c_void_p),
                    ct.POINTER(ct.c_size_t)
                ]

                # Variable initialization
                bytearray_buffer = bytearray(input_file)
                ct_input_buffer = (ct.c_ubyte * len(bytearray_buffer)).from_buffer(bytearray_buffer)
                ct_input_size = ct.c_size_t(len(input_file))
                ct_output_buffer = ct.c_void_p(0)
                ct_output_size = ct.c_size_t(0)

                status = self.library.GWMemoryToMemoryProtectAndImport(
                    ct_input_buffer,
                    ct_input_size,
                    ct.byref(ct_output_buffer),
                    ct.byref(ct_output_size)
                )

            input_file_repr = f"{type(input_file)} length {len(input_file)}" if isinstance(input_file, (bytes, bytearray,)) else input_file.__sizeof__() if isinstance(input_file, io.BytesIO) else input_file
            if status not in successes.success_codes:
                log.warning(f"\n\tstatus: {status}\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}")
                if raise_unsupported:
                    raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
                else:
                    file_bytes = None
            else:
                log.debug(f"\n\tstatus: {status}\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file}")
                if isinstance(input_file, str) and isinstance(output_file, str):
                    # file to file, read the bytes of the file that Rebuild has already written
                    if not os.path.isfile(output_file):
                        log.warning(f"Rebuild returned success code: {status} and no output file was found: {output_file}")
                        file_bytes = None
                    else:
                        with open(output_file, "rb") as f:
                            file_bytes = f.read()
                else:
                    # file to memory, memory to memory
                    file_bytes = utils.buffer_to_bytes(
                        ct_output_buffer,
                        ct_output_size
                    )
                    if isinstance(output_file, str):
                        # memory to file
                        # no Rebuild function exists for memory to file, write the memory to file ourselves
                        with open(output_file, "wb") as f:
                            f.write(file_bytes)

            return file_bytes

    def import_directory(self, input_directory: str, output_directory: Union[None, str], content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None, raise_unsupported: bool = True):
        """ Imports all files in a directory and its subdirectories. Files are expected as .zip but this is not forced.
        The constructed files are written to output_directory maintaining the same directory structure as input_directory.

        Args:
            input_directory (str): The input directory containing files to import.
            output_directory (Union[None, str]): The output directory where the constructed files will be written, or None to not write files.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): Default None (sanitise). The content management policy to apply.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            import_files_dict (dict): A dictionary of file paths relative to input_directory, and file bytes.
        """
        import_files_dict = {}
        # Call import_file on each file in input_directory to output_directory
        for input_file in utils.list_file_paths(input_directory):
            relative_path = os.path.relpath(input_file, input_directory)
            # Remove .zip extension from relative_path
            relative_path = os.path.splitext(relative_path)[0]
            output_file = None if output_directory is None else os.path.join(os.path.abspath(output_directory), relative_path)

            import_bytes = self.import_file(
                input_file=input_file,
                output_file=output_file,
                raise_unsupported=raise_unsupported,
                content_management_policy=content_management_policy,
            )

            import_files_dict[relative_path] = import_bytes

        return import_files_dict
