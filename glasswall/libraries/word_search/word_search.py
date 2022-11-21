

import ctypes as ct
import io
import os
from typing import Optional, Union

import glasswall
from glasswall import utils
from glasswall.config.logging import log
from glasswall.libraries.library import Library
from glasswall.libraries.word_search import errors, successes


class WordSearch(Library):
    """ A high level Python wrapper for Glasswall WordSearch. """

    def __init__(self, library_path: str):
        super().__init__(library_path=library_path)
        self.library = self.load_library(os.path.abspath(library_path))

        log.info(f"Loaded Glasswall {self.__class__.__name__} version {self.version()} from {self.library_path}")

    def version(self):
        """ Returns the Glasswall library version.

        Returns:
            version (str): The Glasswall library version.
        """
        # API function declaration
        self.library.GwWordSearchVersion.restype = ct.c_char_p

        # API call
        version = self.library.GwWordSearchVersion()

        # Convert to Python string
        version = ct.string_at(version).decode()

        return version

    @glasswall.utils.deprecated_alias(xml_config="content_management_policy")
    def redact_file(self, input_file: Union[str, bytes, bytearray, io.BytesIO], content_management_policy: Union[str, bytes, bytearray, io.BytesIO], output_file: Union[None, str] = None, output_report: Union[None, str] = None, homoglyphs: Union[None, str, bytes, bytearray, io.BytesIO] = None, raise_unsupported: bool = True):
        """ Redacts text from input_file using the given content_management_policy and homoglyphs file, optionally writing the redacted file and report to the paths specified by output_file and output_report.

        Args:
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The input file path or bytes.
            content_management_policy (Union[str, bytes, bytearray, io.BytesIO)]): The content management policy to apply.
            output_file (Union[None, str], optional): Default None. If str, write output_file to that path.
            output_report (Union[None, str], optional): Default None. If str, write output_file to that path.
            homoglyphs (Union[None, str, bytes, bytearray, io.BytesIO)], optional): Default None. The homoglyphs json file path or bytes.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            gw_return_object (glasswall.GwReturnObj): An instance of class glasswall.GwReturnObj containing attributes: "status" (int), "output_file" (bytes), "output_report" (bytes)
        """
        # Validate arg types
        if not isinstance(input_file, (str, bytes, bytearray, io.BytesIO)):
            raise TypeError(input_file)
        if not isinstance(content_management_policy, (str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            raise TypeError(content_management_policy)
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)
        if not isinstance(output_report, (type(None), str)):
            raise TypeError(output_report)
        if not isinstance(homoglyphs, (type(None), str, bytes, bytearray, io.BytesIO)):
            raise TypeError(homoglyphs)

        # Convert string path arguments to absolute paths
        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)

        if isinstance(output_report, str):
            output_report = os.path.abspath(output_report)

        # Convert inputs to bytes
        if isinstance(input_file, str):
            with open(input_file, "rb") as f:
                input_file_bytes = f.read()
        elif isinstance(input_file, (bytes, bytearray, io.BytesIO)):
            input_file_bytes = utils.as_bytes(input_file)
        # warn if input_file is 0 bytes
        if not input_file_bytes:
            log.warning(f"input_file is 0 bytes\n\tinput_file: {input_file}")

        if isinstance(homoglyphs, str):
            with open(homoglyphs, "rb") as f:
                homoglyphs_bytes = f.read()
        elif isinstance(homoglyphs, (bytes, bytearray, io.BytesIO)):
            homoglyphs_bytes = utils.as_bytes(homoglyphs)
        elif isinstance(homoglyphs, type(None)):
            # Load default
            with open(os.path.join(glasswall._ROOT, "config", "word_search", "homoglyphs.json"), "rb") as f:
                homoglyphs_bytes = f.read()

        if isinstance(content_management_policy, str) and os.path.isfile(content_management_policy):
            with open(content_management_policy, "rb") as f:
                content_management_policy = f.read()
        content_management_policy = utils.validate_xml(content_management_policy)

        # Variable initialisation
        ct_input_buffer = ct.c_char_p(input_file_bytes)
        ct_input_buffer_length = ct.c_size_t(len(input_file_bytes))
        ct_output_buffer = ct.c_void_p()
        ct_output_buffer_length = ct.c_size_t()
        ct_output_report_buffer = ct.c_void_p()
        ct_output_report_buffer_length = ct.c_size_t()
        ct_homoglyphs = ct.c_char_p(homoglyphs_bytes)
        ct_content_management_policy = ct.c_char_p(content_management_policy.encode())
        gw_return_object = glasswall.GwReturnObj()

        with utils.CwdHandler(new_cwd=self.library_path):
            gw_return_object.status = self.library.GwWordSearch(
                ct_input_buffer,
                ct_input_buffer_length,
                ct.byref(ct_output_buffer),
                ct.byref(ct_output_buffer_length),
                ct.byref(ct_output_report_buffer),
                ct.byref(ct_output_report_buffer_length),
                ct_homoglyphs,
                ct_content_management_policy
            )

        gw_return_object.output_file = utils.buffer_to_bytes(
            ct_output_buffer,
            ct_output_buffer_length
        )
        gw_return_object.output_report = utils.buffer_to_bytes(
            ct_output_report_buffer,
            ct_output_report_buffer_length
        )

        input_file_repr = f"{type(input_file_bytes)} length {len(input_file_bytes)}" if not isinstance(input_file, str) else input_file
        output_file_repr = f"{type(gw_return_object.output_file)} length {len(gw_return_object.output_file)}"
        output_report_repr = f"{type(gw_return_object.output_report)} length {len(gw_return_object.output_report)}"
        homoglyphs_repr = f"{type(homoglyphs_bytes)} length {len(homoglyphs_bytes)}" if not isinstance(homoglyphs, str) else homoglyphs
        if gw_return_object.status not in successes.success_codes:
            log.error(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file_repr}\n\toutput_report: {output_report_repr}\n\thomoglyphs: {homoglyphs_repr}\n\tstatus: {gw_return_object.status}\n\tcontent_management_policy:\n{content_management_policy}")
            if raise_unsupported:
                raise errors.error_codes.get(gw_return_object.status, errors.UnknownErrorCode)(gw_return_object.status)
        else:
            log.debug(f"\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file_repr}\n\toutput_report: {output_report_repr}\n\thomoglyphs: {homoglyphs_repr}\n\tstatus: {gw_return_object.status}\n\tcontent_management_policy:\n{content_management_policy}")

        # Write output file
        if gw_return_object.output_file:
            if isinstance(output_file, str):
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, "wb") as f:
                    f.write(gw_return_object.output_file)

        # Write output report
        if gw_return_object.output_report:
            if isinstance(output_report, str):
                os.makedirs(os.path.dirname(output_report), exist_ok=True)
                with open(output_report, "wb") as f:
                    f.write(gw_return_object.output_report)

        if input_file_bytes and not gw_return_object.output_file:
            # input_file_bytes was not empty but output_file is unexpectedly empty
            log.error(f"output_file empty\n\tinput_file: {input_file_repr}\n\tct_output_buffer: {ct_output_buffer}\n\tct_output_buffer_length: {ct_output_buffer_length}\n\toutput_file: {gw_return_object.output_file}")
            if raise_unsupported:
                raise errors.WordSearchError(f"Unexpected empty output_file after calling GwWordSearch\n\toutput_file: {output_file}")

        if input_file_bytes and not gw_return_object.output_report:
            # input_file_bytes was not empty but output_report is unexpectedly empty
            log.error(f"output_report empty\n\tinput_file: {input_file_repr}\n\tct_output_report_buffer: {ct_output_report_buffer}\n\tct_output_report_buffer_length: {ct_output_report_buffer_length}")
            if raise_unsupported:
                raise errors.WordSearchError(f"Unexpected empty output_report after calling GwWordSearch\n\toutput_report: {output_report}")

        return gw_return_object

    @glasswall.utils.deprecated_alias(xml_config="content_management_policy")
    def redact_directory(self, input_directory: str, content_management_policy: Union[str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy], output_directory: Optional[str] = None, output_report_directory: Optional[str] = None, homoglyphs: Union[None, str, bytes, bytearray, io.BytesIO] = None, raise_unsupported: bool = True):
        """ Redacts all files in a directory and it's subdirectories using the given content_management_policy and homoglyphs file. The redacted files are written to output_directory maintaining the same directory structure as input_directory.

        Args:
            input_directory (str): The input directory containing files to redact.
            output_directory (str): The output directory where the redacted files will be written.
            output_report_directory (Optional[str], optional): Default None. If str, the output directory where analysis reports for each redacted file will be written.
            content_management_policy (Union[str, bytes, bytearray, io.BytesIO)]): The content management policy to apply.
            homoglyphs (Union[None, str, bytes, bytearray, io.BytesIO)], optional): Default None. The homoglyphs file path, str, or bytes.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            redacted_files_dict (dict): A dictionary of file paths relative to input_directory, and glasswall.GwReturnObj with attributes: "status" (int), "output_file" (bytes), "output_report" (bytes)
        """
        redacted_files_dict = {}
        # Call redact_file on each file in input_directory
        for input_file in utils.list_file_paths(input_directory):
            relative_path = os.path.relpath(input_file, input_directory)
            # Construct paths for output file and output report
            output_file = None if output_directory is None else os.path.join(os.path.abspath(output_directory), relative_path)
            output_report = None if output_report_directory is None else os.path.join(os.path.abspath(output_report_directory), relative_path + ".xml")

            result = self.redact_file(
                input_file=input_file,
                output_file=output_file,
                output_report=output_report,
                homoglyphs=homoglyphs,
                content_management_policy=content_management_policy,
                raise_unsupported=raise_unsupported,
            )

            redacted_files_dict[relative_path] = result

        return redacted_files_dict
