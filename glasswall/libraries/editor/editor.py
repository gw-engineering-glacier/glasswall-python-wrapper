

import ctypes as ct
import io
import os
from contextlib import contextmanager
from typing import Union

import glasswall
from glasswall import determine_file_type as dft
from glasswall import utils
from glasswall.config.logging import log
from glasswall.libraries.editor import errors, successes
from glasswall.libraries.library import Library


class Editor(Library):
    """ A high level Python wrapper for Glasswall Editor / Core2. """

    def __init__(self, library_path: str):
        super().__init__(library_path)
        self.library = self.load_library(os.path.abspath(library_path))

        # Validate killswitch has not activated
        self.validate_license()

        log.info(f"Loaded Glasswall {self.__class__.__name__} version {self.version()} from {self.library_path}")

    def validate_license(self):
        """ Validates the license of the library by attempting to call protect_file on a known supported file.

        Raises:
            LicenseExpired: If the license has expired.
            EditorError: If the license could not be validated.
        """
        # Call protect file on a known good bitmap to see if license has expired
        try:
            self.protect_file(
                input_file=b"BM:\x00\x00\x00\x00\x00\x00\x006\x00\x00\x00(\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\x00",
                raise_unsupported=True
            )
            log.debug(f"{self.__class__.__name__} license validated successfully.")
        except errors.EditorError:
            log.warning(f"{self.__class__.__name__} license validation failed.")
            raise

    def version(self):
        """ Returns the Glasswall library version.

        Returns:
            version (str): The Glasswall library version.
        """
        # API function declaration
        self.library.GW2LibVersion.restype = ct.c_char_p

        # API call
        version = self.library.GW2LibVersion()

        # Convert to Python string
        version = ct.string_at(version).decode()

        return version

    def open_session(self):
        """ Open a new Glasswall session.

        Returns:
            session (int): An incrementing integer repsenting the current session.
        """
        # API call
        session = self.library.GW2OpenSession()

        log.debug(f"\n\tsession: {session}")

        return session

    def close_session(self, session: int):
        """ Close the Glasswall session. All resources allocated by the session will be destroyed.

        Args:
            session (int): The session to close.

        Returns:
            None
        """
        if not isinstance(session, int):
            raise TypeError(session)

        # API function declaration
        self.library.GW2CloseSession.argtypes = [ct.c_size_t]

        # Variable initialisation
        ct_session = ct.c_size_t(session)

        # API call
        status = self.library.GW2CloseSession(ct_session)

        if status not in successes.success_codes:
            log.warning(f"\n\tsession: {session}\n\tstatus: {status}")
        else:
            log.debug(f"\n\tsession: {session}\n\tstatus: {status}")

        return status

    @contextmanager
    def new_session(self):
        """ Context manager. Opens a new session on entry and closes the session on exit. """
        try:
            session = self.open_session()
            yield session
        finally:
            self.close_session(session)

    def run_session(self, session):
        """ Runs the Glasswall session and begins processing of a file.

        Args:
            session (int): The session to run.

        Returns:
            status (int): The status of the function call.
        """
        # API function declaration
        self.library.GW2RunSession.argtypes = [ct.c_size_t]

        # Variable initialisation
        ct_session = ct.c_size_t(session)

        # API call
        status = self.library.GW2RunSession(ct_session)

        if status not in successes.success_codes:
            log.warning(f"\n\tsession: {session}\n\tstatus: {status}")
        else:
            log.debug(f"\n\tsession: {session}\n\tstatus: {status}")

        return status

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

            # convert to ct.c_char_p of bytes
            ct_input_file = ct.c_char_p(input_file.encode("utf-8"))

            # API call
            file_type = self.library.GW2DetermineFileTypeFromFile(ct_input_file)

        elif isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            # convert to bytes
            bytes_input_file = utils.as_bytes(input_file)

            # ctypes conversion
            ct_buffer = ct.c_char_p(bytes_input_file)
            ct_butter_length = ct.c_size_t(len(bytes_input_file))

            # API call
            file_type = self.library.GW2DetermineFileTypeFromMemory(
                ct_buffer,
                ct_butter_length
            )

        else:
            raise TypeError(input_file)

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

    def get_content_management_policy(self, session: int):
        """ Returns the content management configuration for a given session.

        Args:
            session (int): The current session.

        Returns:
            xml_string (str): The XML string of the current content management configuration.
        """
        # NOTE GW2GetPolicySettings is current not implemented in editor

        # set xml_string as loaded default config
        xml_string = glasswall.content_management.policies.Editor(default="sanitise").text,

        # log.debug(f"xml_string:\n{xml_string}")

        return xml_string

        # # API function declaration
        # self.library.GW2GetPolicySettings.argtypes = [
        #     ct.c_size_t,
        #     ct.c_void_p,
        # ]

        # # Variable initialisation
        # ct_session = ct.c_size_t(session)
        # ct_buffer = ct.c_void_p()
        # ct_butter_length = ct.c_size_t()
        # # ct_file_format = ct.c_int(file_format)

        # # API Call
        # status = self.library.GW2GetPolicySettings(
        #     ct_session,
        #     ct.byref(ct_buffer),
        #     ct.byref(ct_butter_length)
        # )

        # print("GW2GetPolicySettings status:", status)

        # file_bytes = utils.buffer_to_bytes(
        #     ct_buffer,
        #     ct_butter_length,
        # )

        # return file_bytes

    def set_content_management_policy(self, session: int, input_file: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None, file_format=0):
        """ Sets the content management policy configuration. If input_file is None then default settings (sanitise) are applied.

        Args:
            session (int): The current session.
            input_file (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): Default None (sanitise). The content management policy to apply.
            file_format (int): The file format of the content management policy. 0 is xml.

        Returns:
            status (int): The result of the Glasswall API call.
        """
        # Validate type
        if not isinstance(session, int):
            raise TypeError(session)
        if not isinstance(input_file, (type(None), str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            raise TypeError(input_file)
        if not isinstance(file_format, int):
            raise TypeError(file_format)

        # Set input_file to default if input_file is None
        if input_file is None:
            input_file = glasswall.content_management.policies.Editor(default="sanitise")

        # Validate xml content is parsable
        utils.validate_xml(input_file)

        gw_return_object = glasswall.GwReturnObj()

        # From file
        if isinstance(input_file, str) and os.path.isfile(input_file):
            # API function declaration
            self.library.GW2RegisterPoliciesFile.argtypes = [
                ct.c_size_t,
                ct.c_char_p,
                ct.c_int,
            ]

            # Variable initialisation
            gw_return_object.ct_session = ct.c_size_t(session)
            gw_return_object.ct_input_file = ct.c_char_p(input_file.encode("utf-8"))
            gw_return_object.ct_file_format = ct.c_int(file_format)

            gw_return_object.status = self.library.GW2RegisterPoliciesFile(
                gw_return_object.ct_session,
                gw_return_object.ct_input_file,
                gw_return_object.ct_file_format
            )

        # From memory
        elif isinstance(input_file, (str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            # Convert bytearray, io.BytesIO to bytes
            if isinstance(input_file, (bytearray, io.BytesIO)):
                input_file = utils.as_bytes(input_file)
            # Convert string xml or Policy to bytes
            if isinstance(input_file, (str, glasswall.content_management.policies.policy.Policy)):
                input_file = input_file.encode("utf-8")

            # API function declaration
            self.library.GW2RegisterPoliciesMemory.argtype = [
                ct.c_size_t,
                ct.c_char_p,
                ct.c_int
            ]

            # Variable initialisation
            gw_return_object.ct_session = ct.c_size_t(session)
            gw_return_object.ct_buffer = ct.c_char_p(input_file)
            gw_return_object.ct_buffer_length = ct.c_size_t(len(input_file))
            gw_return_object.ct_file_format = ct.c_int(file_format)

            # API Call
            gw_return_object.status = self.library.GW2RegisterPoliciesMemory(
                gw_return_object.ct_session,
                gw_return_object.ct_buffer,
                gw_return_object.ct_buffer_length,
                gw_return_object.ct_file_format
            )

        if gw_return_object.status not in successes.success_codes:
            log.warning(f"\n\tsession: {session}\n\tstatus: {gw_return_object.status}")
            raise errors.error_codes.get(gw_return_object.status, errors.UnknownErrorCode)(gw_return_object.status)
        else:
            log.debug(f"\n\tsession: {session}\n\tstatus: {gw_return_object.status}")

        return gw_return_object

    def register_input(self, session: int, input_file: Union[str, bytes, bytearray, io.BytesIO]):
        """ Register an input file or bytes for the given session.

        Args:
            session (int): The current session.
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The input file path or bytes.

        Returns:
            status (int): The result of the Glasswall API call.
        """

        if not isinstance(input_file, (str, bytes, bytearray, io.BytesIO,)):
            raise TypeError(input_file)

        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)

            # API function declaration
            self.library.GW2RegisterInputFile.argtypes = [
                ct.c_size_t,
                ct.c_char_p
            ]

            # Variable initialisation
            ct_session = ct.c_size_t(session)
            ct_input_file = ct.c_char_p(input_file.encode("utf-8"))

            # API call
            status = self.library.GW2RegisterInputFile(
                ct_session,
                ct_input_file
            )

        elif isinstance(input_file, (bytes, bytearray, io.BytesIO,)):
            # Convert bytearray and io.BytesIO to bytes
            input_file = utils.as_bytes(input_file)

            # API function declaration
            self.library.GW2RegisterInputMemory.argtypes = [
                ct.c_size_t,
                ct.c_char_p,
                ct.c_size_t,
            ]

            # Variable initialisation
            ct_session = ct.c_size_t(session)
            ct_buffer = ct.c_char_p(input_file)
            ct_buffer_length = ct.c_size_t(len(input_file))

            # API call
            status = self.library.GW2RegisterInputMemory(
                ct_session,
                ct_buffer,
                ct_buffer_length
            )

        if status not in successes.success_codes:
            log.warning(f"\n\tsession: {session}\n\tstatus: {status}")
            raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
        else:
            log.debug(f"\n\tsession: {session}\n\tstatus: {status}")

        return status

    def register_output(self, session, output_file: Union[None, str] = None):
        """ Register an output file for the given session. If output_file is None the file will be returned as 'buffer' and 'buffer_length' attributes.

        Args:
            session (int): The current session.
            output_file (Union[None, str], optional): If specified, during run session the file will be written to output_file, otherwise the file will be written to the glasswall.GwReturnObj 'buffer' and 'buffer_length' attributes.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attribute 'status' indicating the result of the function call. If output_file is None (memory mode), 'buffer', and 'buffer_length' are included containing the file content and file size.
        """

        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)

        gw_return_object = glasswall.GwReturnObj()

        if isinstance(output_file, str):
            # API function declaration
            self.library.GW2RegisterOutFile.argtypes = [
                ct.c_size_t,
                ct.c_char_p
            ]

            # Variable initialisation
            ct_session = ct.c_size_t(session)
            ct_output_file = ct.c_char_p(output_file.encode("utf-8"))

            # API call
            gw_return_object.status = self.library.GW2RegisterOutFile(
                ct_session,
                ct_output_file
            )

        else:
            # API function declaration
            self.library.GW2RegisterOutputMemory.argtypes = [
                ct.c_size_t,
                ct.POINTER(ct.c_void_p),
                ct.POINTER(ct.c_size_t)
            ]

            # Variable initialisation
            ct_session = ct.c_size_t(session)
            gw_return_object.buffer = ct.c_void_p()
            gw_return_object.buffer_length = ct.c_size_t(0)

            # API call
            gw_return_object.status = self.library.GW2RegisterOutputMemory(
                ct_session,
                ct.byref(gw_return_object.buffer),
                ct.byref(gw_return_object.buffer_length)
            )

        if gw_return_object.status not in successes.success_codes:
            log.warning(f"\n\tsession: {session}\n\tstatus: {gw_return_object.status}")
            raise errors.error_codes.get(gw_return_object.status, errors.UnknownErrorCode)(gw_return_object.status)
        else:
            log.debug(f"\n\tsession: {session}\n\tstatus: {gw_return_object.status}")

        return gw_return_object

    def register_analysis(self, session: int, output_file: Union[None, str] = None):
        """ Registers an analysis file for the given session. The analysis file will be created during the session's run_session call.

        Args:
            session (int): The session number.
            output_file (Union[None, str], optional): Default None. The file path where the analysis will be written. None returns the analysis as bytes.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attribute 'status' indicating the result of the function call. If output_file is None (memory mode), 'buffer', and 'buffer_length' are included containing the file content and file size.
        """

        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)

        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)

            # API function declaration
            self.library.GW2RegisterAnalysisFile.argtypes = [
                ct.c_size_t,
                ct.c_char_p,
                ct.c_int,
            ]

            # Variable initialisation
            ct_session = ct.c_size_t(session)
            ct_output_file = ct.c_char_p(output_file.encode("utf-8"))
            analysis_file_format = ct.c_int()
            gw_return_object = glasswall.GwReturnObj()

            # API call
            status = self.library.GW2RegisterAnalysisFile(
                ct_session,
                ct_output_file,
                analysis_file_format
            )

        elif isinstance(output_file, type(None)):
            # API function declaration
            self.library.GW2RegisterAnalysisMemory.argtypes = [
                ct.c_size_t,
                ct.POINTER(ct.c_void_p),
                ct.POINTER(ct.c_size_t)
            ]

            # Variable initialisation
            ct_session = ct.c_size_t(session)
            gw_return_object = glasswall.GwReturnObj()
            gw_return_object.buffer = ct.c_void_p()
            gw_return_object.buffer_length = ct.c_size_t()

            # API call
            status = self.library.GW2RegisterAnalysisMemory(
                ct_session,
                ct.byref(gw_return_object.buffer),
                ct.byref(gw_return_object.buffer_length)
            )

        if status not in successes.success_codes:
            log.warning(f"\n\tsession: {session}\n\tstatus: {status}")
            raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
        else:
            log.debug(f"\n\tsession: {session}\n\tstatus: {status}")

        gw_return_object.status = status

        return gw_return_object

    def protect_file(self, input_file: Union[str, bytes, bytearray, io.BytesIO], output_file: Union[None, str] = None, content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None, raise_unsupported: bool = True):
        """ Protects a file using the current content management configuration, returning the file bytes. The protected file is written to output_file if it is provided.

        Args:
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The input file path or bytes.
            output_file (Union[None, str], optional): The output file path where the protected file will be written.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): The content management policy to apply to the session.
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

        # Convert memory inputs to bytes
        if isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            input_file = utils.as_bytes(input_file)

        # Check that file type is supported
        try:
            self.determine_file_type(input_file=input_file)
        except dft.errors.FileTypeEnumError:
            if raise_unsupported:
                raise
            else:
                return None

        with utils.CwdHandler(self.library_path):
            with self.new_session() as session:
                content_management_policy = self.set_content_management_policy(session, content_management_policy)
                register_input = self.register_input(session, input_file)
                register_output = self.register_output(session, output_file=output_file)
                status = self.run_session(session)
                # Ensure memory allocated is not garbage collected until after run_session
                content_management_policy, register_input, register_output

                if status not in successes.success_codes:
                    if raise_unsupported:
                        raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
                    else:
                        file_bytes = None
                else:
                    # Get file bytes
                    if isinstance(output_file, str):
                        # File to file and memory to file, Editor wrote to a file, read it to get the file bytes
                        if not os.path.isfile(output_file):
                            log.warning(f"Editor returned success code: {status} but no output file was found: {output_file}")
                            file_bytes = None
                        else:
                            with open(output_file, "rb") as f:
                                file_bytes = f.read()
                    else:
                        # File to memory and memory to memory, Editor wrote to a buffer, convert it to bytes
                        file_bytes = utils.buffer_to_bytes(
                            register_output.buffer,
                            register_output.buffer_length
                        )

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
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): The content management policy to apply to the session.
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

        # Check that file type is supported
        try:
            self.determine_file_type(input_file=input_file)
        except dft.errors.FileTypeEnumError:
            if raise_unsupported:
                raise
            else:
                return None

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

        # Convert memory inputs to bytes
        if isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            input_file = utils.as_bytes(input_file)

        with utils.CwdHandler(self.library_path):
            with self.new_session() as session:
                content_management_policy = self.set_content_management_policy(session, content_management_policy)
                register_input = self.register_input(session, input_file)
                register_analysis = self.register_analysis(session, output_file)
                status = self.run_session(session)
                # Ensure memory allocated is not garbage collected until after run_session
                content_management_policy, register_input, register_analysis

                if isinstance(output_file, str):
                    # File to file and memory to file, Editor wrote to a file, read it to get the file bytes
                    if not os.path.isfile(output_file):
                        log.warning(f"Editor returned success code: {status} and no output file was found: {output_file}")
                        file_bytes = None
                    else:
                        with open(output_file, "rb") as f:
                            file_bytes = f.read()
                else:
                    # File to memory and memory to memory, Editor wrote to a buffer, convert it to bytes
                    file_bytes = utils.buffer_to_bytes(
                        register_analysis.buffer,
                        register_analysis.buffer_length
                    )

                if status not in successes.success_codes:
                    if raise_unsupported:
                        raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)

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

    def register_export(self, session: int, output_file: Union[None, str] = None):
        """ Registers a file to be exported for the given session. The export file will be created during the session's run_session call.

        Args:
            session (int): The session number.
            output_file (Union[None, str], optional): Default None. The file path where the export will be written. None returns the export as bytes.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attribute 'status' indicating the result of the function call. If output_file is None (memory mode), 'buffer', and 'buffer_length' are included containing the file content and file size.
        """

        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)

        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)

            # API function declaration
            self.library.GW2RegisterExportFile.argtypes = [
                ct.c_size_t,
                ct.c_char_p
            ]

            # Variable initialisation
            ct_session = ct.c_size_t(session)
            ct_output_file = ct.c_char_p(output_file.encode("utf-8"))
            gw_return_object = glasswall.GwReturnObj()

            # API Call
            status = self.library.GW2RegisterExportFile(
                ct_session,
                ct_output_file
            )

        elif isinstance(output_file, type(None)):
            # API function declaration
            self.library.GW2RegisterExportMemory.argtypes = [
                ct.c_size_t,
                ct.POINTER(ct.c_void_p),
                ct.POINTER(ct.c_size_t)
            ]

            # Variable initialisation
            ct_session = ct.c_size_t(session)
            gw_return_object = glasswall.GwReturnObj()
            gw_return_object.buffer = ct.c_void_p()
            gw_return_object.buffer_length = ct.c_size_t()

            # API call
            status = self.library.GW2RegisterExportMemory(
                ct_session,
                ct.byref(gw_return_object.buffer),
                ct.byref(gw_return_object.buffer_length)
            )

        if status not in successes.success_codes:
            log.warning(f"\n\tsession: {session}\n\tstatus: {status}")
            raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
        else:
            log.debug(f"\n\tsession: {session}\n\tstatus: {status}")

        gw_return_object.status = status

        return gw_return_object

    def export_file(self, input_file: Union[str, bytes, bytearray, io.BytesIO], output_file: Union[None, str] = None, content_management_policy: Union[None, str, bytes, bytearray, io.BytesIO, "glasswall.content_management.policies.policy.Policy"] = None, raise_unsupported: bool = True):
        """ Export a file, returning the .zip file bytes. The .zip file is written to output_file if it is provided.

        Args:
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The input file path or bytes.
            output_file (Union[None, str], optional): The output file path where the .zip file will be written.
            content_management_policy (Union[None, str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], optional): The content management policy to apply to the session.
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

        # Check that file type is supported
        try:
            self.determine_file_type(input_file=input_file)
        except dft.errors.FileTypeEnumError:
            if raise_unsupported:
                raise
            else:
                return None

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

        # Convert memory inputs to bytes
        if isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            input_file = utils.as_bytes(input_file)

        with utils.CwdHandler(self.library_path):
            with self.new_session() as session:
                content_management_policy = self.set_content_management_policy(session, content_management_policy)
                register_input = self.register_input(session, input_file)
                register_export = self.register_export(session, output_file)
                status = self.run_session(session)
                # Ensure memory allocated is not garbage collected until after run_session
                content_management_policy, register_input, register_export

                if status not in successes.success_codes:
                    log.warning(f"\n\tsession: {session}\n\tstatus: {status}")
                    if raise_unsupported:
                        raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
                    else:
                        file_bytes = None
                else:
                    # Get file bytes
                    if isinstance(output_file, str):
                        # File to file and memory to file, Editor wrote to a file, read it to get the file bytes
                        if not os.path.isfile(output_file):
                            log.warning(f"Editor returned success code: {status} but no output file was found: {output_file}")
                            file_bytes = None
                        else:
                            with open(output_file, "rb") as f:
                                file_bytes = f.read()
                    else:
                        # File to memory and memory to memory, Editor wrote to a buffer, convert it to bytes
                        file_bytes = utils.buffer_to_bytes(
                            register_export.buffer,
                            register_export.buffer_length
                        )

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

    def register_import(self, session: int, input_file: Union[str, bytes, bytearray, io.BytesIO]):
        """ Registers a .zip file to be imported for the given session. The constructed file will be created during the session's run_session call.

        Args:
            session (int): The session number.
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The input file path or bytes.

        Returns:
            gw_return_object (glasswall.GwReturnObj): A GwReturnObj instance with the attribute 'status' indicating the result of the function call. If output_file is None (memory mode), 'buffer', and 'buffer_length' are included containing the file content and file size.
        """
        if not isinstance(input_file, (str, bytes, bytearray, io.BytesIO,)):
            raise TypeError(input_file)

        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)

        gw_return_object = glasswall.GwReturnObj()

        if isinstance(input_file, str):
            input_file = os.path.abspath(input_file)

            # API function declaration
            self.library.GW2RegisterImportFile.argtypes = [
                ct.c_size_t,
                ct.c_char_p
            ]

            # Variable initialisation
            ct_session = ct.c_size_t(session)
            ct_input_file = ct.c_char_p(input_file.encode("utf-8"))

            # API Call
            gw_return_object.status = self.library.GW2RegisterImportFile(
                ct_session,
                ct_input_file
            )

        elif isinstance(input_file, (bytes, bytearray, io.BytesIO,)):
            # Convert bytearray and io.BytesIO to bytes
            input_file = utils.as_bytes(input_file)

            # API function declaration
            self.library.GW2RegisterImportMemory.argtypes = [
                ct.c_size_t,
                ct.c_void_p,
                ct.c_size_t
            ]

            # Variable initialisation
            ct_session = ct.c_size_t(session)
            gw_return_object.buffer = ct.c_char_p(input_file)
            gw_return_object.buffer_length = ct.c_size_t(len(input_file))

            # API call
            gw_return_object.status = self.library.GW2RegisterImportMemory(
                ct_session,
                gw_return_object.buffer,
                gw_return_object.buffer_length
            )

        if gw_return_object.status not in successes.success_codes:
            log.warning(f"\n\tsession: {session}\n\tstatus: {gw_return_object.status}")
            raise errors.error_codes.get(gw_return_object.status, errors.UnknownErrorCode)(gw_return_object.status)
        else:
            log.debug(f"\n\tsession: {session}\n\tstatus: {gw_return_object.status}")

        return gw_return_object

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

        # Check that file type is supported
        try:
            self.determine_file_type(input_file=input_file)
        except dft.errors.FileTypeEnumError:
            if raise_unsupported:
                raise
            else:
                return None

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

        # Convert memory inputs to bytes
        if isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            input_file = utils.as_bytes(input_file)

        with utils.CwdHandler(self.library_path):
            with self.new_session() as session:
                content_management_policy = self.set_content_management_policy(session, content_management_policy)
                register_import = self.register_import(session, input_file)
                register_output = self.register_output(session, output_file)
                status = self.run_session(session)
                # Ensure memory allocated is not garbage collected until after run_session
                content_management_policy, register_import, register_output

                if status not in successes.success_codes:
                    log.warning(f"\n\tsession: {session}\n\tstatus: {status}")
                    if raise_unsupported:
                        raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
                    else:
                        file_bytes = None
                else:
                    # Get file bytes
                    if isinstance(output_file, str):
                        # File to file and memory to file, Editor wrote to a file, read it to get the file bytes
                        if not os.path.isfile(output_file):
                            log.warning(f"Editor returned success code: {status} but no output file was found: {output_file}")
                            file_bytes = None
                        else:
                            with open(output_file, "rb") as f:
                                file_bytes = f.read()
                    else:
                        # File to memory and memory to memory, Editor wrote to a buffer, convert it to bytes
                        file_bytes = utils.buffer_to_bytes(
                            register_output.buffer,
                            register_output.buffer_length
                        )

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
