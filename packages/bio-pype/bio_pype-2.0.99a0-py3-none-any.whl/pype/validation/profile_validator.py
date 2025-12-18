"""Profile validation implementation.

Validates bio_pype YAML profile configurations using the Profile class.
The Profile class handles all YAML loading, parsing, and structure validation.
"""

import logging
from pathlib import Path
from typing import Dict, Optional, List
from typing_extensions import NoDefault

from pype.exceptions import ProfileError, CommandNamespaceError
from pype.process import Namespace
from pype.utils.profiles import Profile
from pype.validation.core import (
    Diagnostic,
    DiagnosticSeverity,
    Location,
    ValidationContext,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class ProfileValidator:
    """Validator for bio_pype YAML profiles.

    Uses the Profile class from pype.utils.profiles for all validation.
    The Profile class handles:
    - YAML loading and parsing
    - Structure validation
    - Program conversion to ProfileProgram objects
    - All attribute setting and validation
    """

    def __init__(self, context: ValidationContext) -> None:
        """Initialize profile validator.

        Args:
            context: ValidationContext for workspace information
        """
        self.context = context

        self.profile: Profile = None
        self.profile_files = {}
        self.profile_programs = {}
        self.file_lines = []

    def _load_file_lines(self, file_path: Path) -> None:
        """
        Return the line number
        """
        if len(self.file_lines) == 0:
            with open(file_path, 'rt') as f:
                for line in f:
                    self.file_lines.append(line)


    def _load_profile(self, file_path: Path) -> None:
        profile_name = file_path.stem
        self._load_file_lines(file_path)
        self.profile = Profile(str(file_path), profile_name)

    def _get_line_nr(self, words_match: List) -> int:
        """Find line number for a section, using pre-loaded file lines."""
        for line_nr, line in enumerate(self.file_lines):
            if all(x in line for x in words_match):
                return line_nr
        return 0

    def _run_diagnostics(self, file_path: Path) -> List:
        diagnostics = []

        try:
            if self.profile is None:
                self._load_profile(file_path)

            # Successfully loaded profile - structure is valid
            # The Profile class has:
            # - Loaded the YAML
            # - Parsed it
            # - Validated structure
            # - Converted programs to ProfileProgram objects

        except ProfileError as e:
            # Profile class raised a validation error
            diagnostics.append(
                Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    location=Location(0, 0, 10),
                    message=f"Profile validation failed: {e}",
                    code="profile-error",
                )
            )

        except Exception as e:
            # Other unexpected errors
            diagnostics.append(
                Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    location=Location(0, 0, 10),
                    message=f"Failed to load profile: {e}",
                    code="profile-load-error",
                )
            )
        if self.profile:
            for profile_file in self.profile.files:
                if isinstance(self.profile.files[profile_file], str):
                    self.profile_files[profile_file] = f"{self.profile.__name__}: {self.profile.files[profile_file]}"
                else:
                    files_line_nr = self._get_line_nr([profile_file, ":"])
                    diagnostics.append(
                        Diagnostic(
                            severity=DiagnosticSeverity.ERROR,
                            location=Location(files_line_nr, 0, 10),
                            message=f"Profile file: {profile_file} is not a string",
                            code="profile-file-error",
                        )
                    )

            for profile_program in self.profile.programs:
                try:
                    self.profile_programs[profile_program] = Namespace(
                        self.profile.programs[profile_program],
                        logger,
                        self.profile).namespace
                except CommandNamespaceError as e:
                    files_line_nr = self._get_line_nr([profile_program, ":"])
                    diagnostics.append(
                        Diagnostic(
                            severity=DiagnosticSeverity.ERROR,
                            location=Location(files_line_nr, 0, 10),
                            message=f"Profile program {profile_program} error: {e}",
                            code="profile-program-error",
                        )
                    )
        return diagnostics


    def validate(self, file_path: Path) -> ValidationResult:
        """Validate a profile file by attempting to load it with the Profile class.

        The Profile class does all the validation - if it loads successfully,
        the profile is valid. If it raises an exception, that's a validation error.

        Args:
            file_path: Path to the profile file to validate

        Returns:
            ValidationResult with diagnostics
        """
        diagnostics = self._run_diagnostics(file_path)

        is_valid = not any(d.severity == DiagnosticSeverity.ERROR for d in diagnostics)
        return ValidationResult(file_path, "profile", diagnostics, is_valid)

    def load_profile(self, file_path: Path) -> tuple[Optional[Profile], list]:
        """Load a profile and return it with any diagnostics.

        Args:
            file_path: Path to the profile file

        Returns:
            Tuple of (Profile object or None, list of diagnostics)
        """
        diagnostics = self._run_diagnostics(file_path)
        return self.profile, diagnostics

    def extract_profile_files(self, profile_path: Path) -> Dict[str, str]:
        """Extract profile files from a loaded Profile object.

        Args:
            profile: Profile object (or None if profile failed to load)

        Returns:
            Dict mapping file keys to file paths, or empty dict if profile is None
        """


        diagnostics = self._run_diagnostics(profile_path)
        return self.profile_files

    def extract_profile_programs(self, profile_path: Path) -> Dict[str, str]:
        """Extract profile programs from a loaded Profile object.

        Args:
            profile: Profile object (or None if profile failed to load)

        Returns:
            Dict mapping file keys to file paths, or empty dict if profile is None
        """
        diagnostics = self._run_diagnostics(profile_path)
        return self.profile_programs
