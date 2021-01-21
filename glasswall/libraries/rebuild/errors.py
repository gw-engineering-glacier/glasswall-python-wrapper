

from glasswall.libraries.rebuild.classes import RebuildError


class UnknownErrorCode(RebuildError):
    """ Unknown error code. """
    pass


# Statuses from sdk.rebuild\src\code\dll.gwfile\dll.gwfilestatus.h
class Error(RebuildError):
    """ Rebuild error code 0. This value indicates that the document was non-conformant in some way, but any requested output files were written. """
    pass


class SuccessDocumentWriteFailure(RebuildError):
    """ Rebuild error code -1. This value indicates that the document was managed successfully, but a failure occured when writing the managed version of the document to file. """
    pass


class SuccessAnalysisWriteFailure(RebuildError):
    """ Rebuild error code -2. This value indicates that the document was analysed successfully, but a failure occured when writing the analysis of the document to file. """
    pass


class ErrorAnalysisWriteFailure(RebuildError):
    """ Rebuild error code -3. This value indicates that the document was non-conformant in some way, and a failure occured when writing the analysis of the document to file. """
    pass


class SuccessReportWriteFailure(RebuildError):
    """ Rebuild error code -4. This value indicates that the document was processed successfully, but that a failure occured when writing the processing report to file. """
    pass


class SuccessDocumentReportWriteFailure(RebuildError):
    """ Rebuild error code -5. This value indicates that the document was managed successfully, but a failure occured when writing both the managed version of the document and the processing report to file. """
    pass


class ErrorReportWriteFailure(RebuildError):
    """ Rebuild error code -6. This value indicates that the document was non-conformant in some way,  and that a failure occured when writing the processing report to file. """
    pass


class SuccessAnalysisReportWriteFailure(RebuildError):
    """ Rebuild error code -7. This value indicates that the document was analysed successfully, but a failure occured when writing both the analysis of the document and the processing report to file. """
    pass


class ErrorAnalysisReportWriteFailure(RebuildError):
    """ Rebuild error code -8. This value indicates that the document was non-conformant in some way, but a failure occured when writing both the analysis of the document and the processing report to file. """
    pass


class InternalError(RebuildError):
    """ Rebuild error code -9. This value indicates an uncategorised error """
    pass


class SuccessDocumentAnalysisReportWriteFailure(RebuildError):
    """ Rebuild error code -10. This value indicates that the document was analysed successfully, but failures occured when writing the document, the analysis of the document and the processing report to file (AMP mode). """
    pass


class SuccessDocumentAnalysisWriteFailure(RebuildError):
    """ Rebuild error code -11. This value indicates that the document was analysed successfully, but failures occured when writing the document and the analysis of the document to file (AMP mode). """
    pass


class SuccessExportWriteFailure(RebuildError):
    """ Rebuild error code -12. This value indicates that the document was exported successfully, but failures occured when writing the archive package. (Export mode) """
    pass


class ErrorExportWriteFailure(RebuildError):
    """ Rebuild error code -13. This value indicates that the document was non-conformant in some way, and failures occured when writing the archive package. (Export mode) """
    pass


error_codes = {
    0: Error,
    -1: SuccessDocumentWriteFailure,
    -2: SuccessAnalysisWriteFailure,
    -3: ErrorAnalysisWriteFailure,
    -4: SuccessReportWriteFailure,
    -5: SuccessDocumentReportWriteFailure,
    -6: ErrorReportWriteFailure,
    -7: SuccessAnalysisReportWriteFailure,
    -8: ErrorAnalysisReportWriteFailure,
    -9: InternalError,
    -10: SuccessDocumentAnalysisReportWriteFailure,
    -11: SuccessDocumentAnalysisWriteFailure,
    -12: SuccessExportWriteFailure,
    -13: ErrorExportWriteFailure,
}
