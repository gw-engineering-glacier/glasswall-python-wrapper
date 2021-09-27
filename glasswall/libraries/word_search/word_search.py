

import ctypes as ct
import io
import os
from typing import Union

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

    def redact_file(self, input_file: Union[str, bytes, bytearray, io.BytesIO], xml_config: Union[None, str, bytes, bytearray, io.BytesIO], output_file: Union[None, str] = None, output_report: Union[None, str] = None, homoglyphs: Union[None, str, bytes, bytearray, io.BytesIO] = None, raise_unsupported: bool = True):
        """ Performs GwWordSearch on a given input file.

        Args:
            input_file (Union[str, bytes, bytearray, io.BytesIO]): The input file path or bytes.
            output_file (Union[None, str], optional): Default None. If str, write output_file to that path.
            output_report (Union[None, str], optional): Default None. If str, write output_file to that path.
            xml_config (Union[None, str, bytes, bytearray, io.BytesIO)], optional): The xml_config file path or bytes.
            homoglyphs (Union[None, str, bytes, bytearray, io.BytesIO)], optional): Default None. The homoglyphs json file path or bytes.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            gw_return_object (glasswall.GwReturnObj): An instance of class glasswall.GwReturnObj containing attributes: "status" (int), "output_file" (bytes), "output_report" (bytes)
        """
        # Validate arg types
        if not isinstance(input_file, (str, bytes, bytearray, io.BytesIO)):
            raise TypeError(input_file)
        if not isinstance(output_file, (type(None), str)):
            raise TypeError(output_file)
        if not isinstance(output_report, (type(None), str)):
            raise TypeError(output_report)
        if not isinstance(homoglyphs, (type(None), str, bytes, bytearray, io.BytesIO)):
            raise TypeError(homoglyphs)
        if not isinstance(xml_config, (type(None), str, bytes, bytearray, io.BytesIO, glasswall.content_management.policies.policy.Policy)):
            raise TypeError(xml_config)

        # Convert string path arguments to absolute paths
        if isinstance(output_file, str):
            output_file = os.path.abspath(output_file)

        if isinstance(output_report, str):
            output_report = os.path.abspath(output_report)

        # Convert inputs to bytes
        if isinstance(input_file, str):
            if not os.path.isfile(input_file):
                raise FileNotFoundError(input_file)
            with open(input_file, "rb") as f:
                input_file_bytes = f.read()
        elif isinstance(input_file, (bytearray, io.BytesIO)):
            input_file_bytes = utils.as_bytes(input_file)

        if isinstance(homoglyphs, str):
            if os.path.isfile(homoglyphs):
                with open(homoglyphs, "rb") as f:
                    homoglyphs_bytes = f.read()
            else:
                raise FileNotFoundError(homoglyphs)
        elif isinstance(homoglyphs, (bytearray, io.BytesIO)):
            homoglyphs_bytes = utils.as_bytes(homoglyphs)
        elif isinstance(homoglyphs, type(None)):
            # Load default
            with open(os.path.join(glasswall._ROOT, "config", "word_search", "homoglyphs.json"), "rb") as f:
                homoglyphs_bytes = f.read()

        if isinstance(xml_config, str) and os.path.isfile(xml_config):
            with open(xml_config, "rb") as f:
                xml_config = f.read()
        elif isinstance(xml_config, type(None)):
            # Load default
            xml_config = glasswall.content_management.policies.WordSearch(
                default="allow",
                config={
                    "textSearchConfig": {
                        "@libVersion": "core2",
                        "textList": []
                    }
                }
            ).text,
        xml_config = utils.validate_xml(xml_config)

        # Variable initialisation
        ct_input_buffer = ct.c_char_p(input_file_bytes)
        ct_input_buffer_length = ct.c_size_t(len(input_file_bytes))
        output_buffer = ct.c_void_p()
        output_buffer_length = ct.c_size_t()
        output_report_buffer = ct.c_void_p()
        output_report_buffer_length = ct.c_size_t()
        ct_homoglyphs = ct.c_char_p(homoglyphs_bytes)
        ct_xml_config = ct.c_char_p(xml_config.encode())
        gw_return_object = glasswall.GwReturnObj()

        with utils.CwdHandler(new_cwd=self.library_path):
            gw_return_object.status = self.library.GwWordSearch(
                ct_input_buffer,
                ct_input_buffer_length,
                ct.byref(output_buffer),
                ct.byref(output_buffer_length),
                ct.byref(output_report_buffer),
                ct.byref(output_report_buffer_length),
                ct_homoglyphs,
                ct_xml_config
            )

        gw_return_object.output_file = utils.buffer_to_bytes(
            output_buffer,
            output_buffer_length
        )
        gw_return_object.output_report = utils.buffer_to_bytes(
            output_report_buffer,
            output_report_buffer_length
        )

        input_file_repr = f"{type(input_file)} length {len(input_file)}" if isinstance(input_file, (bytes, bytearray,)) else input_file.__sizeof__() if isinstance(input_file, io.BytesIO) else input_file
        output_file_repr = f"{type(gw_return_object.output_file)} length {len(gw_return_object.output_file)}"
        output_report_repr = f"{type(gw_return_object.output_report)} length {len(gw_return_object.output_report)}"
        homoglyphs_repr = f"{type(homoglyphs_bytes)} length {len(homoglyphs_bytes)}" if not isinstance(homoglyphs, str) else homoglyphs
        if gw_return_object.status not in successes.success_codes:
            log.warning(f"\n\tstatus: {gw_return_object.status}\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file_repr}\n\toutput_report: {output_report_repr}\n\thomoglyphs: {homoglyphs_repr}\n\txml_config:\n{xml_config}")
            if raise_unsupported:
                raise errors.error_codes.get(gw_return_object.status, errors.UnknownErrorCode)(gw_return_object.status)
        else:
            # TODO arabic UnicodeEncodeError
            log.debug(f"\n\tstatus: {gw_return_object.status}\n\tinput_file: {input_file_repr}\n\toutput_file: {output_file_repr}\n\toutput_report: {output_report_repr}\n\thomoglyphs: {homoglyphs_repr}\n\txml_config:\n{xml_config}")

        if raise_unsupported:
            if not gw_return_object.output_file:
                log.warning(f"output_file empty\n\toutput_buffer: {output_buffer}\n\toutput_buffer_length: {output_buffer_length}")
            if not gw_return_object.output_report:
                log.warning(f"output_report empty\n\toutput_report_buffer: {output_report_buffer}\n\toutput_report_buffer_length: {output_report_buffer_length}")

        # Write output file
        if isinstance(output_file, str):
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, "wb") as f:
                f.write(gw_return_object.output_file)

        # Write output report
        if isinstance(output_report, str):
            os.makedirs(os.path.dirname(output_report), exist_ok=True)
            with open(output_report, "wb") as f:
                f.write(gw_return_object.output_report)

        return gw_return_object

    def redact_directory(self, input_directory: str, output_directory: str, xml_config: Union[str, bytes, bytearray, io.BytesIO], homoglyphs: Union[None, str, bytes, bytearray, io.BytesIO] = None, raise_unsupported: bool = True):
        """ Redacts all files in a directory using the given XML config and homoglyphs JSON file. The redacted files are written to output_directory maintaining the same directory structure as input_directory.

        Args:
            input_directory (str): The input directory containing files to protect.
            output_directory (str): The output directory where the protected file will be written.
            xml_config (Union[str, bytes, bytearray, io.BytesIO)], optional): The xml_config file path or bytes.
            homoglyphs (Union[None, str, bytes, bytearray, io.BytesIO)], optional): Default None. The homoglyphs file path or bytes.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            None
        """
        for relative_path in utils.list_file_paths(input_directory, absolute=False):
            # construct absolute paths
            input_file = os.path.abspath(os.path.join(input_directory, relative_path))
            output_file = os.path.abspath(os.path.join(output_directory, relative_path))
            output_report = os.path.abspath(os.path.join(output_directory, relative_path + ".xml"))

            # call protect_file on each file in input to output
            self.redact_file(
                input_file=input_file,
                output_file=output_file,
                output_report=output_report,
                homoglyphs=homoglyphs,
                xml_config=xml_config,
                raise_unsupported=raise_unsupported,
            )
