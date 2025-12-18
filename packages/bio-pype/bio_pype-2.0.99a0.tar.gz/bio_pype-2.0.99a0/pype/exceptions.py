"""Central exception handling for bio_pype.

Provides a hierarchy of custom exceptions for better error context and handling.
Each exception type includes contextual information specific to its domain.
"""


class PypeError(Exception):
    """Base exception for all pype errors."""

    def __init__(self, message: str, context: dict = None):
        self.context = context or {}
        super().__init__(message)


class PipelineError(PypeError):
    """Base class for pipeline-related errors."""

    def __init__(self, message: str, pipeline_name: str = None, **kwargs):
        context = {"pipeline_name": pipeline_name, **kwargs}
        super().__init__(f"Pipeline error: {message}", context)


class PipelineVersionError(PipelineError):
    """Raised when pipeline version is incompatible."""

    def __init__(
        self, current_version: str, required_version: str, pipeline_name: str = None
    ):
        super().__init__(
            f"Version mismatch: {current_version} != {required_version}",
            pipeline_name,
            current_version=current_version,
            required_version=required_version,
        )


class PipelineItemError(PipelineError):
    """Error in a specific pipeline item."""

    def __init__(
        self, message: str, item_name: str, item_type: str, pipeline_name: str = None
    ):
        super().__init__(
            f"Error in {item_type} '{item_name}': {message}",
            pipeline_name,
            item_name=item_name,
            item_type=item_type,
        )


class SnippetError(PypeError):
    """Base class for snippet-related errors."""

    def __init__(self, message: str, snippet_name: str = None, **kwargs):
        context = {"snippet_name": snippet_name, **kwargs}
        super().__init__(f"Snippet error: {message}", context)


class SnippetNotFoundError(SnippetError):
    """Raised when a snippet cannot be found."""

    def __init__(self, snippet_name: str):
        super().__init__(f"Snippet '{snippet_name}' not found", snippet_name)


class SnippetExecutionError(SnippetError):
    """Raised when snippet execution fails."""

    def __init__(self, message: str, snippet_name: str, exit_code: int = None):
        super().__init__(message, snippet_name, exit_code=exit_code)


class ArgumentError(PypeError):
    """Base class for argument-related errors."""

    def __init__(self, message: str, argument: str = None, **kwargs):
        context = {"argument": argument, **kwargs}
        super().__init__(f"Argument error: {message}", context)


class BatchArgumentError(ArgumentError):
    """Error in batch argument processing."""

    def __init__(self, message: str, batch_file: str = None):
        super().__init__(message, batch_file=batch_file)


class ProfileError(PypeError):
    """Base class for profile-related errors."""

    def __init__(self, message: str, profile_name: str = None, **kwargs):
        context = {"profile_name": profile_name, **kwargs}
        super().__init__(f"Profile error: {message}", context)


class CommandError(PypeError):
    """Base class for command execution errors."""

    def __init__(self, message: str, command: str = None, exit_code: int = None):
        context = {"command": command, "exit_code": exit_code}
        super().__init__(f"Command error: {message}", context)


class CommandNamespaceError(CommandError):
    """Error in command namespace."""

    pass


class EnvModulesError(PypeError):
    """Error in environment modules."""

    def __init__(self, message: str, module_name: str = None):
        super().__init__(
            f"Environment module error: {message}", {"module_name": module_name}
        )
