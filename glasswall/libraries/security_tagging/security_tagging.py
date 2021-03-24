

import ctypes as ct
import os
import sys

from glasswall import utils
from glasswall.config.logging import log
from glasswall.libraries.library import Library
from glasswall.libraries.security_tagging import errors, successes


class SecurityTagging(Library):
    """ A high level Python wrapper for Glasswall Security Tagging. """

    def __init__(self, library_path: str):
        super().__init__(library_path=library_path)
        self.library = self.load_library(os.path.abspath(library_path))

        log.info(f"Loaded Glasswall {self.__class__.__name__} version {self.version()} from {self.library_path}")

    def version(self):
        """ Returns the Glasswall library version.

        Returns:
            version (str): The Glasswall library version.
        """
        # TODO security tagging currently has no version function
        return "NOT_IMPLEMENTED"

    def tag_file(self, tags_path: str, input_file: str, output_file: str, raise_unsupported: bool = True):
        """ Tags the input_file with xml loaded from tags_path, writing to output_file.

        Args:
            tags_path (str): The path to the .xml file containing tags to add.
            input_file (str): The path to the input file.
            output_file (str): The path to the output file where the tagged input_file will be written to.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            status (int): An integer indicating the file process status.

        Raises:
            TypeError: If any arguments are of incorrect type.
            NotImplementedError: If raise_unsupported is True and the status of calling GWSecuTag_TagFile is not 1 (success)
        """
        # Validate arg types
        if not isinstance(tags_path, str):
            raise TypeError(tags_path)
        elif not os.path.isfile(tags_path):
            raise FileNotFoundError(tags_path)

        if not isinstance(input_file, str):
            raise TypeError(input_file)
        elif not os.path.isfile(input_file):
            raise FileNotFoundError(input_file)

        if not isinstance(output_file, str):
            raise TypeError(output_file)

        if not isinstance(raise_unsupported, bool):
            raise TypeError(raise_unsupported)

        # Convert paths to absolute paths
        tags_path = os.path.abspath(tags_path)
        input_file = os.path.abspath(input_file)
        output_file = os.path.abspath(output_file)

        # Make output directory if it does not exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with utils.CwdHandler(self.library_path):
            # API function declaration
            self.library.GWSecuTag_TagFile.argtypes = [ct.c_char_p]

            # Variable initialisation
            ct_tags_path = ct.c_char_p(tags_path.encode("utf-8"))
            ct_input_file = ct.c_char_p(input_file.encode("utf-8"))
            ct_output_file = ct.c_char_p(output_file.encode("utf-8"))

            # API call
            status = self.library.GWSecuTag_TagFile(
                ct_input_file,
                ct_tags_path,
                ct_output_file,
            )

            if status not in successes.success_codes:
                log.warning(f"\n\tstatus: {status}\n\tinput_file: {input_file}\n\toutput_file: {output_file}\n\ttags_path: {tags_path}")
                if raise_unsupported:
                    raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
            else:
                log.debug(f"\n\tstatus: {status}\n\tinput_file: {input_file}\n\toutput_file: {output_file}\n\ttags_path: {tags_path}")

            # TODO remove, temp fix - check if tags are retrievable, if not delete the file just created by glasswall
            # if status not in successes.success_codes: # status is currently incorrect in the library
            if not os.path.isfile(output_file):
                log.warning(f"\n\tstatus: {status}\n\toutput file does not exist: {output_file}")
                status = "OUTPUT_NOT_CREATED"
            elif os.path.isfile(output_file):
                with utils.TempFilePath() as temp_file:
                    self.retrieve_tags(
                        input_file=output_file,
                        output_file=temp_file,
                        raise_unsupported=False
                    )
                    try:
                        dict_ = utils.xml_as_dict(temp_file)
                    except ValueError:
                        dict_ = {}
                    if not dict_:
                        os.remove(output_file)
                        log.debug(f"\n\tunable to retrieve tags, deleted output file\n\toutput_file: {output_file}\n\t")
                        status = "OUTPUT_NOT_RETRIEVABLE"

            return status

    def tag_directory(self, tags_path: str, input_directory: str, output_directory: str, raise_unsupported: bool = True):
        """ Tags all files in input_directory with the xml loaded from tags_path, writing to output_directory and maintaining the same directory structure.

        Args:
            tags_path (str): The path to the .xml file containing tags to add.
            input_directory (str): The path to the input directory.
            output_directory (str): The path to the output directory where the tagged files will be written to.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            status (int): An integer indicating the file process status.

        Raises:
            TypeError: If any arguments are of incorrect type.
            NotImplementedError: If raise_unsupported is True and the status of calling GWSecuTag_TagFile is not 1 (success)
        """
        # Validate arg types
        if not isinstance(tags_path, str):
            raise TypeError(tags_path)
        elif not os.path.isfile(tags_path):
            raise FileNotFoundError(tags_path)

        if not isinstance(input_directory, str):
            raise TypeError(input_directory)
        elif not os.path.isdir(input_directory):
            raise NotADirectoryError(input_directory)

        if not isinstance(output_directory, str):
            raise TypeError(output_directory)

        if not isinstance(raise_unsupported, bool):
            raise TypeError(raise_unsupported)

        for relative_path in utils.list_file_paths(input_directory, absolute=False):
            # construct absolute paths
            input_file = os.path.abspath(os.path.join(input_directory, relative_path))
            output_file = os.path.abspath(os.path.join(output_directory, relative_path))

            # call tag_file on each file in input to output
            self.tag_file(
                tags_path=tags_path,
                input_file=input_file,
                output_file=output_file,
                raise_unsupported=raise_unsupported,
            )

        utils.delete_empty_subdirectories(output_directory)

    def retrieve_tags(self, input_file: str, output_file: str, raise_unsupported=True):
        """ Retrieves the xml tags of the input_file and writes it to output_file.

        Args:
            input_file (str): The path to the input file.
            output_file (str): The path to the output file where the xml tags will be written to.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            status (int): An integer indicating the file process status.

        Raises:
            TypeError: If any arguments are of incorrect type.
            NotImplementedError: If raise_unsupported is True and the status of calling GWSecuTag_RetrieveTagFile is not 1 (success)
        """
        if not isinstance(input_file, str):
            raise TypeError(input_file)
        elif not os.path.isfile(input_file):
            raise FileNotFoundError(input_file)

        if not isinstance(output_file, str):
            raise TypeError(output_file)

        # Convert paths to absolute paths
        input_file = os.path.abspath(input_file)
        output_file = os.path.abspath(output_file)

        # Make output directory if it does not exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        log.debug(f"Attempting {sys._getframe().f_code.co_name}:\n\tinput_file: {input_file}\n\toutput_file: {output_file}")

        with utils.CwdHandler(self.library_path):
            # API function declaration
            self.library.GWSecuTag_RetrieveTagFile.argtypes = [ct.c_char_p]

            # Variable initialisation
            ct_input_file = ct.c_char_p(input_file.encode("utf-8"))
            ct_output_file = ct.c_char_p(output_file.encode("utf-8"))

            # API call
            status = self.library.GWSecuTag_RetrieveTagFile(
                ct_input_file,
                ct_output_file,
            )

            if status not in successes.success_codes:
                log.warning(f"\n\tstatus: {status}\n\tinput_file: {input_file}\n\toutput_file: {output_file}")
                if raise_unsupported:
                    raise errors.error_codes.get(status, errors.UnknownErrorCode)(status)
            else:
                log.debug(f"\n\tstatus: {status}\n\tinput_file: {input_file}\n\toutput_file: {output_file}")

            return status

    def retrieve_tags_directory(self, input_directory: str, output_directory: str, raise_unsupported=True):
        """ Retrieves all tags from files in input_directory, writing XML to output_directory and maintaining the same directory structure.

        Args:
            input_directory (str): The path to the input directory.
            output_directory (str): The path to the output directory where the tagged files will be written to.
            raise_unsupported (bool, optional): Default True. Raise exceptions when Glasswall encounters an error. Fail silently if False.

        Returns:
            status (int): The status of the function call.

        Raises:
            TypeError: If any arguments are of incorrect type.
            NotImplementedError: If raise_unsupported is True and the status of calling GWSecuTag_RetrieveTagFile is not 1 (success)
        """
        # Validate arg types
        if not isinstance(input_directory, str):
            raise TypeError(input_directory)
        elif not os.path.isdir(input_directory):
            raise NotADirectoryError(input_directory)

        if not isinstance(output_directory, str):
            raise TypeError(output_directory)

        if not isinstance(raise_unsupported, bool):
            raise TypeError(raise_unsupported)

        for relative_path in utils.list_file_paths(input_directory, absolute=False):
            # construct absolute paths
            input_file = os.path.abspath(os.path.join(input_directory, relative_path))
            output_file = os.path.abspath(os.path.join(output_directory, relative_path + ".xml"))

            # call retrieve_tags on each file in input to output
            self.retrieve_tags(
                input_file=input_file,
                output_file=output_file,
                raise_unsupported=raise_unsupported,
            )

        utils.delete_empty_subdirectories(output_directory)
