"""Custom exceptions for the RootCauseAI application."""


class RootCauseAIError(Exception):
    """Base class for RootCauseAI exceptions."""

    pass


class LogAnalysisError(RootCauseAIError):
    """Raised when log analysis fails."""

    def __init__(self, message: str, original_error: Exception | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Error message describing what went wrong.
            original_error: The original exception that caused this error, if any.
        """
        super().__init__(message)
        self.message = message
        self.original_error = original_error


class FileReadError(RootCauseAIError):
    """Raised when file reading fails."""

    def __init__(self, filename: str, reason: str) -> None:
        """Initialize the exception.

        Args:
            filename: Name of the file that failed to read.
            reason: Reason for the failure.
        """
        message = f"Failed to read file '{filename}': {reason}"
        super().__init__(message)
        self.filename = filename
        self.reason = reason


class LLMServiceError(RootCauseAIError):
    """Raised when LLM service calls fail."""

    def __init__(self, message: str, original_error: Exception | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Error message describing what went wrong.
            original_error: The original exception that caused this error, if any.
        """
        super().__init__(message)
        self.message = message
        self.original_error = original_error
