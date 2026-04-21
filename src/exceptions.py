EC_ARG_GENERAL = 10
EC_ARG_TEMPLATE_JSON = 11
EC_ARG_INPUT_PDF_OUTPUT_PDF = 12

EC_PDFIX_ERROR = 20

MESSAGE_ARG_GENERAL = "Failed to parse arguments. Please check the usage and try again."
MESSAGE_ARG_TEMPLATE_JSON = "PDFix layout template was not provided."
MESSAGE_ARG_INPUT_PDF_OUTPUT_PDF = "Input and output file must be PDF documents."


class ExpectedException(BaseException):
    def __init__(self, error_code: int) -> None:
        self.error_code: int = error_code
        self.message: str = ""

    def _add_note(self, note: str) -> None:
        self.message = note


class ArgumentException(ExpectedException):
    def __init__(self, message: str = MESSAGE_ARG_GENERAL, error_code: int = EC_ARG_GENERAL) -> None:
        super().__init__(error_code)
        self._add_note(message)


class ArgumentTemplateJsonException(ArgumentException):
    def __init__(self) -> None:
        super().__init__(MESSAGE_ARG_TEMPLATE_JSON, EC_ARG_TEMPLATE_JSON)


class ArgumentInputPdfOutputPdfException(ArgumentException):
    def __init__(self) -> None:
        super().__init__(MESSAGE_ARG_INPUT_PDF_OUTPUT_PDF, EC_ARG_INPUT_PDF_OUTPUT_PDF)


class PdfixException(ExpectedException):
    def __init__(self, error_code: int, message: str = "") -> None:
        super().__init__(EC_PDFIX_ERROR)
        self._add_note(f"[{error_code}] {message}")
