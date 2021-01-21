

class VisualComparisonToolError(Exception):
    """ Base exception for Visual Comparison Tool. """
    pass


class VisualComparisonToolUnexpectedError(VisualComparisonToolError):
    """ Unexpected exception for Visual Comparison Tool. """
    pass


class VisualComparisonToolContentMismatch(VisualComparisonToolError):
    """ Executing Visual Comparison Tool resulted in a content mismatch. """
    pass


class VisualComparisonToolFileMismatch(VisualComparisonToolError):
    """ Executing Visual Comparison Tool resulted in a file mismatch. """
    pass


class VisualComparisonToolProcessingError(VisualComparisonToolError):
    """ Executing Visual Comparison Tool resulted in a processing error. """
    pass


class VisualComparisonToolConversionError(VisualComparisonToolError):
    """ Executing Visual Comparison Tool resulted in a conversion error. """
    pass


class VisualComparisonToolUnsupportedFileType(VisualComparisonToolError):
    """ Executing Visual Comparison Tool resulted in an unsupported file type error. """
    pass


class VisualComparisonToolInvalidArguments(VisualComparisonToolError):
    """ Executing Visual Comparison Tool resulted in an invalid arguments error. """
    pass


class VisualComparisonToolTimeout(VisualComparisonToolError):
    """ Executing Visual Comparison Tool resulted in a timeout error. """
    pass
