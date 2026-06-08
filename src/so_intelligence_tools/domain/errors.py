class ToolRunnerError(RuntimeError):
    """Base error for runner workflows."""


class NoSelectionError(ToolRunnerError):
    """Raised when the tool expected text selection and none was available."""


class InferenceUnavailableError(ToolRunnerError):
    """Raised when the inference backend cannot satisfy a request."""


class UserCancelledError(ToolRunnerError):
    """Raised when the user cancels an interactive system operation."""


class UnsupportedEnvironmentError(ToolRunnerError):
    """Raised when the current environment lacks a required integration."""


class ToolRunnerConfigurationError(ToolRunnerError):
    """Raised when a runner dependency is misconfigured."""


class AudioCaptureError(ToolRunnerError):
    """Raised when system audio capture cannot start or continue."""


class StreamingSessionError(ToolRunnerError):
    """Raised when a live streaming session cannot proceed."""
