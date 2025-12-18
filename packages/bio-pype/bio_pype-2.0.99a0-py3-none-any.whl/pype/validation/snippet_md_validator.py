"""Snippet validation implementation.

Validates bio_pype Markdown snippets for structural and semantic correctness.
Ports validation logic from VSCode plugin while using bio_pype API for runtime validation.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

logger = logging.getLogger(__name__)

from pype.utils.snippets import SnippetMd, ArgumentList
from pype.validation.context import WorkspaceIndex
from pype.validation.core import (
    Diagnostic,
    DiagnosticSeverity,
    Location,
    ValidationContext,
    ValidationResult,
)
from pype.validation.parsers import (
    CodeChunkHeaderParser,
    IODeclarationParser,
    MarkdownSectionParser,
    VariableTracker,
)
from pype.validation.profile_validator import ProfileValidator


class SnippetValidator:
    """Validator for bio_pype Markdown snippets.

    Validates:
    - Required sections (description, requirements, results, arguments, snippet)
    - Requirements format (ncpu, time, mem)
    - Arguments structure (sequential numbering, types, options)
    - Code chunk headers and format
    - Variable definitions and usage
    - I/O declarations
    - Namespace references to profiles
    - Runtime validation (attempting to load with SnippetMd)
    """

    # Required sections for all snippets
    REQUIRED_SECTIONS = {
        "description",
        "requirements",
        "results",
        "arguments",
        "snippet",
    }

    # All valid section names (required + optional like "name")
    VALID_SECTIONS = REQUIRED_SECTIONS | {"name"}

    # Valid argument types
    VALID_ARG_TYPES = {"str", "int", "float", "bool"}

    # Valid argument options
    VALID_ARG_OPTIONS = {
        "help",
        "type",
        "required",
        "default",
        "nargs",
        "action",
        "choices",
    }

    # Valid actions for arguments
    VALID_ACTIONS = {"store_true", "store_false"}

    def __init__(self, context: ValidationContext) -> None:
        """Initialize snippet validator.

        Args:
            context: ValidationContext for workspace information
        """
        self.context = context

    def _add_diagnostic(
        self,
        diagnostics: List[Diagnostic],
        severity: DiagnosticSeverity,
        line: int,
        start_char: int,
        end_char: int,
        message: str,
        code: str,
    ) -> None:
        """Add a diagnostic to the list."""
        diagnostics.append(
            Diagnostic(
                severity=severity,
                location=Location(line, start_char, end_char),
                message=message,
                code=code,
            )
        )

    def validate(self, file_path: Path) -> ValidationResult:
        """Validate a snippet file.

        Args:
            file_path: Path to the snippet file to validate

        Returns:
            ValidationResult with diagnostics
        """
        diagnostics: List[Diagnostic] = []

        # Read file content
        try:
            with open(file_path, "r") as f:
                content = f.read()
        except IOError as e:
            error_diagnostics: List[Diagnostic] = []
            self._add_diagnostic(
                error_diagnostics,
                DiagnosticSeverity.ERROR,
                0,
                0,
                10,
                f"Failed to read file: {e}",
                "file-read-error",
            )
            return ValidationResult(
                file_path,
                "snippet",
                error_diagnostics,
            )

        # Parse sections
        sections = MarkdownSectionParser.parse_sections(content)

        # Create single SnippetMd instance early for reuse (efficient bio_pype API access)
        snippet = None
        try:
            snippet_name = file_path.stem
            parent = type("TempModule", (), {})()
            snippet = SnippetMd(parent, snippet_name, str(file_path))
        except Exception as e:
            logger.debug(f"Could not create SnippetMd for bio_pype API calls: {e}")

        # 0. Validate section headers (must be before other validation)
        diagnostics.extend(self._validate_section_headers(content))

        # 1. Validate required sections
        diagnostics.extend(self._validate_required_sections(sections))

        # 2. Validate requirements section (use SnippetMd to avoid YAML re-parsing)
        if "requirements" in sections:
            diagnostics.extend(self._validate_requirements(sections["requirements"], snippet))

        # 3. Validate results section
        if "results" in sections:
            diagnostics.extend(self._validate_results(sections["results"]))

        # 4. Validate arguments section
        if "arguments" in sections:
            diagnostics.extend(self._validate_arguments(sections["arguments"]))

        # 5. Validate code chunks
        if "snippet" in sections:
            diagnostics.extend(
                self._validate_code_chunks(sections["snippet"], sections)
            )

        # 6. Extract results variables (will be available to other parts of snippet)
        results_variables, parsed_results = self._extract_results_variables(
            snippet, sections.get("results"), diagnostics)

        # 7. Validate variables and cross-references
        diagnostics.extend(
            self._validate_variables(content, sections, results_variables)
        )

        # 8. Cross-file validation (profiles, pipelines)
        profile_diagnostic, profile_files_dict, profile_programs_dict = self._validate_cross_references(
            content, sections)
        diagnostics.extend(profile_diagnostic)

        # 8. Runtime validation (reuse SnippetMd instance)
        diagnostics.extend(self._runtime_validation(snippet))

        # Extract parsed data for use in completions and other features
        parsed_arguments = self._extract_parsed_arguments(sections.get("arguments"))
        # parsed_results already extracted above from _extract_results_variables
        # which uses the actual bio_pype API with UPPERCASE dummy values
        parsed_requirements = self._extract_parsed_requirements(snippet)
        available_profiles = [p.stem for p in self.context.profile_paths]

        # Extract profile files and programs for completions
        # (handled by _validate_cross_references)

        is_valid = not any(d.severity == DiagnosticSeverity.ERROR for d in diagnostics)
        return ValidationResult(
            file_path,
            "snippet",
            diagnostics,
            is_valid,
            parsed_arguments=parsed_arguments,
            parsed_results=parsed_results,
            parsed_requirements=parsed_requirements,
            available_profiles=available_profiles,
            profile_files=profile_files_dict,
            profile_programs=profile_programs_dict
        )

    def _validate_required_sections(self, sections: Dict) -> List[Diagnostic]:
        """Validate that all required sections are present."""
        diagnostics: List[Diagnostic] = []
        for required in self.REQUIRED_SECTIONS:
            if required not in sections:
                self._add_diagnostic(
                    diagnostics,
                    DiagnosticSeverity.ERROR,
                    0,
                    0,
                    10,
                    f"Missing required section: ## {required}",
                    f"missing-section-{required}",
                )
        return diagnostics

    def _validate_section_headers(self, content: str) -> List[Diagnostic]:
        """Validate that all ## headers are valid section names."""
        diagnostics: List[Diagnostic] = []
        in_code_block = False

        for line_num, line in enumerate(content.split("\n")):
            if line.strip().startswith("```"):
                in_code_block = not in_code_block

            if line.startswith("## "):
                section_name = line[3:].strip().lower()
                if in_code_block:
                    self._add_diagnostic(
                        diagnostics,
                        DiagnosticSeverity.ERROR,
                        line_num,
                        0,
                        len(line),
                        f"Invalid '## {section_name}' inside code block. Double hashes break chunk parsing - everything after this line is lost. Use '#' for comments instead.",
                        "invalid-section-in-code",
                    )
                elif section_name and section_name not in self.VALID_SECTIONS:
                    self._add_diagnostic(
                        diagnostics,
                        DiagnosticSeverity.ERROR,
                        line_num,
                        0,
                        len(line),
                        f"Invalid section header: '## {section_name}'. Valid sections are: {', '.join(sorted(self.VALID_SECTIONS))}",
                        "invalid-section-header",
                    )

        return diagnostics

    def _validate_requirements(self, section, snippet: Optional[SnippetMd]) -> List[Diagnostic]:
        """Validate requirements section using SnippetMd API."""
        diagnostics: List[Diagnostic] = []
        required_fields = {"ncpu", "time", "mem"}

        if not snippet:
            self._add_diagnostic(
                diagnostics,
                DiagnosticSeverity.ERROR,
                section.start_line,
                0,
                10,
                "Could not load snippet for requirements validation",
                "snippet-load-error",
            )
            return diagnostics

        try:
            requirements = snippet.requirements()
            if not isinstance(requirements, dict):
                self._add_diagnostic(
                    diagnostics,
                    DiagnosticSeverity.ERROR,
                    section.start_line,
                    0,
                    10,
                    "Requirements must be a YAML object (key: value pairs)",
                    "invalid-requirements-format",
                )
                return diagnostics

            for field in required_fields:
                if field not in requirements:
                    self._add_diagnostic(
                        diagnostics,
                        DiagnosticSeverity.ERROR,
                        section.start_line,
                        0,
                        10,
                        f"Missing required field in requirements: {field}",
                        f"missing-requirement-{field}",
                    )

        except Exception as e:
            self._add_diagnostic(
                diagnostics,
                DiagnosticSeverity.ERROR,
                section.start_line,
                0,
                10,
                f"Failed to parse requirements: {e}",
                "requirements-parse-error",
            )

        return diagnostics

    def _validate_results(self, section) -> List[Diagnostic]:
        """Validate results section.

        Should contain a code chunk with header: @interpreter, parser_format

        Args:
            section: ParsedSection object

        Returns:
            List of diagnostics
        """
        diagnostics: List[Diagnostic] = []
        content = section.content.strip()

        if not content:
            self._add_diagnostic(
                diagnostics,
                DiagnosticSeverity.ERROR,
                section.start_line,
                0,
                10,
                "Results section cannot be empty",
                "empty-results-section",
            )
            return diagnostics

        # Look for code chunk
        if "```" not in content:
            self._add_diagnostic(
                diagnostics,
                DiagnosticSeverity.ERROR,
                section.start_line,
                0,
                10,
                "Results section must contain a code chunk (``` ... ```)",
                "missing-results-code-chunk",
            )
            return diagnostics

        # Extract header (first line after ```)
        lines = content.split("\n")
        header_line = None
        for i, line in enumerate(lines):
            if line.startswith("```"):
                if i + 1 < len(lines):
                    header_line = lines[i + 1]
                break

        if not header_line or not header_line.startswith("@"):
            self._add_diagnostic(
                diagnostics,
                DiagnosticSeverity.ERROR,
                section.start_line,
                0,
                10,
                "Results code chunk must have header: @interpreter, parser_format",
                "missing-results-header",
            )
            return diagnostics

        # Parse and validate header
        header_info = CodeChunkHeaderParser.parse_results_chunk_header(header_line)
        if not header_info["is_valid"]:
            for error in header_info["errors"]:
                self._add_diagnostic(
                    diagnostics,
                    DiagnosticSeverity.ERROR,
                    section.start_line,
                    0,
                    50,
                    f"Invalid results chunk header: {error}",
                    "invalid-results-header",
                )

        return diagnostics

    def _validate_arguments(self, section) -> List[Diagnostic]:
        """Validate arguments section using bio_pype ArgumentList.

        Args should be numbered sequentially (1, 2, 3, ...) with:
        - argument: name
        - help: description (required)
        - type: str/int/float/bool (required)
        - required: true/false (optional)
        - default: value (optional)
        - nargs: * + ? number (optional)
        - action: store_true/store_false (optional)
        - choices: comma/space separated list (optional)

        Args:
            section: ParsedSection object

        Returns:
            List of diagnostics
        """
        diagnostics: List[Diagnostic] = []
        content = section.content.strip()

        try:
            # Use ArgumentList from bio_pype API (same parser as snippet execution)
            arg_list = ArgumentList("snippet", content)
            arguments = arg_list.arguments

            # Validate sequential numbering (ArgumentList is 0-indexed)
            for i, arg_dict in enumerate(arguments):
                expected = i + 1
                if expected > len(arguments):
                    break
                # Note: ArgumentList doesn't track numbers, so we assume sequential parsing
                # Convert to our format for validation
                arg_num_data = {
                    "number": i + 1,
                    "names": arg_dict.get("argument", "").split("/"),
                    "line": section.start_line + i,  # Approximate line number
                    "options": arg_dict.get("options", {}),
                }
                diagnostics.extend(self._validate_argument(arg_num_data))

            return diagnostics
        except Exception as e:
            self._add_diagnostic(
                diagnostics,
                DiagnosticSeverity.ERROR,
                0,
                0,
                50,
                f"Arguments section can't be properly parsed {e}",
                "error-argument-parsing",
            )
            logger.debug(f"Could not validate arguments using ArgumentList: {e}")
            # Fallback to manual parsing if ArgumentList fails
            return diagnostics

    def _validate_argument(self, arg: Dict) -> List[Diagnostic]:
        """Validate a single argument.

        Args:
            arg: Argument dict with keys: number, names, line, options

        Returns:
            List of diagnostics
        """
        diagnostics: List[Diagnostic] = []
        options = arg.get("options", {})

        # Check required fields
        if "help" not in options:
            self._add_diagnostic(
                diagnostics,
                DiagnosticSeverity.WARNING,
                arg["line"],
                0,
                50,
                f"Argument '{arg['names'][0]}' missing 'help' field",
                "missing-argument-help",
            )

        if "type" not in options:
            self._add_diagnostic(
                diagnostics,
                DiagnosticSeverity.WARNING,
                arg["line"],
                0,
                50,
                f"Argument '{arg['names'][0]}' missing 'type' field",
                "missing-argument-type",
            )
        else:
            arg_type = options["type"]
            if arg_type not in self.VALID_ARG_TYPES:
                self._add_diagnostic(
                    diagnostics,
                    DiagnosticSeverity.ERROR,
                    arg["line"],
                    0,
                    50,
                    f"Invalid type '{arg_type}' for argument '{arg['names'][0]}'. "
                    f"Must be one of: {', '.join(self.VALID_ARG_TYPES)}",
                    "invalid-argument-type",
                )

        # Validate option names
        for opt_key in options.keys():
            if opt_key not in self.VALID_ARG_OPTIONS:
                self._add_diagnostic(
                    diagnostics,
                    DiagnosticSeverity.WARNING,
                    arg["line"],
                    0,
                    50,
                    f"Unknown option '{opt_key}' for argument '{arg['names'][0]}'",
                    "unknown-argument-option",
                )

        # Validate action if present
        if "action" in options:
            action = options["action"]
            if action not in self.VALID_ACTIONS:
                self._add_diagnostic(
                    diagnostics,
                    DiagnosticSeverity.ERROR,
                    arg["line"],
                    0,
                    50,
                    f"Invalid action '{action}'. Must be one of: {', '.join(self.VALID_ACTIONS)}",
                    "invalid-argument-action",
                )

        # Validate required field
        if "required" in options:
            req_val = options["required"].lower()
            if req_val not in ("true", "false"):
                self._add_diagnostic(
                    diagnostics,
                    DiagnosticSeverity.ERROR,
                    arg["line"],
                    0,
                    50,
                    f"Invalid 'required' value: '{options['required']}'. Must be 'true' or 'false'",
                    "invalid-required-value",
                )

        return diagnostics

    def _validate_code_chunks(self, section, all_sections: Dict) -> List[Diagnostic]:
        """Validate code chunks in snippet section."""
        diagnostics: List[Diagnostic] = []
        content = section.content.strip()

        if "```" not in content:
            self._add_diagnostic(
                diagnostics,
                DiagnosticSeverity.ERROR,
                section.start_line,
                0,
                10,
                "Snippet section must contain at least one code chunk",
                "missing-snippet-chunks",
            )
            return diagnostics

        # Parse code chunks inline
        chunks = []
        lines = content.split("\n")
        in_chunk = False
        chunk_start = 0
        chunk_header = ""
        chunk_code = []

        for i, line in enumerate(lines):
            if line.startswith("```") and not in_chunk:
                in_chunk = True
                chunk_start = i
                chunk_header = ""
                chunk_code = []
            elif line.startswith("```") and in_chunk:
                in_chunk = False
                chunks.append({
                    "header": chunk_header,
                    "code": "\n".join(chunk_code),
                    "start_line": chunk_start,
                    "end_line": i,
                })
            elif in_chunk and chunk_header == "":
                chunk_header = line
            elif in_chunk:
                chunk_code.append(line)

        # Validate chunks
        for chunk in chunks:
            header_info = CodeChunkHeaderParser.parse_snippet_chunk_header(chunk["header"])
            if not header_info["is_valid"]:
                for error in header_info["errors"]:
                    self._add_diagnostic(
                        diagnostics,
                        DiagnosticSeverity.ERROR,
                        chunk["start_line"] + section.start_line,
                        0,
                        50,
                        f"Invalid snippet chunk header: {error}",
                        "invalid-chunk-header",
                    )

        return diagnostics

    def _validate_variables(
        self, content: str, sections: Dict, results_variables: Set[str] = None
    ) -> List[Diagnostic]:
        """Validate variable definitions and usage.

        Args:
            content: Full file content
            sections: Parsed sections
            results_variables: Set of variable names from results section

        Returns:
            List of diagnostics
        """
        if results_variables is None:
            results_variables = set()

        diagnostics: List[Diagnostic] = []

        # Find all variables used in content
        used_variables = VariableTracker.find_variables(content)

        # Find defined variables (from arguments section)
        defined_variables: Set[str] = set()
        if "arguments" in sections:
            defined_variables = VariableTracker.get_defined_variables(
                sections["arguments"].content
            )

        # Add results variables to defined variables (for I/O declaration checks)
        # Note: Results variables are still validated separately above
        for results_var in results_variables:
            defined_variables.add(f"results_{results_var}")

        # Check for undefined variables
        for var_name, var_info in used_variables.items():
            # Special handling for requirements variables
            if var_name.startswith("requirements_"):
                req_field = var_name[len("requirements_") :]
                if req_field not in {"ncpu", "time", "mem", "gpu"}:
                    for loc in var_info.locations:
                        self._add_diagnostic(
                            diagnostics,
                            DiagnosticSeverity.ERROR,
                            loc.line,
                            loc.start_char,
                            loc.end_char,
                            f"Invalid requirements variable '{var_name}'",
                            "invalid-requirements-variable",
                        )
            # Special handling for profile variables
            elif var_name.startswith("profile_"):
                # Profile variables are ok as long as profile is loaded
                pass
            # Special handling for results variables
            elif var_name.startswith("results_"):
                # Validate that the results variable key exists in extracted results
                key = var_name[len("results_") :]
                if key not in results_variables:
                    for loc in var_info.locations:
                        available = (
                            ", ".join(sorted(results_variables))
                            if results_variables
                            else "none"
                        )
                        self._add_diagnostic(
                            diagnostics,
                            DiagnosticSeverity.ERROR,
                            loc.line,
                            loc.start_char,
                            loc.end_char,
                            f"Undefined results variable '{var_name}'. Available results variables: {available}",
                            "undefined-results-variable",
                        )
            # Regular argument variables
            elif var_name not in defined_variables:
                for loc in var_info.locations:
                    self._add_diagnostic(
                        diagnostics,
                        DiagnosticSeverity.ERROR,
                        loc.line,
                        loc.start_char,
                        loc.end_char,
                        f"Undefined variable '{var_name}'",
                        "undefined-variable",
                    )

        # Validate I/O declarations
        if "snippet" in sections:
            diagnostics.extend(
                self._validate_io_declarations(
                    sections["snippet"].content, defined_variables
                )
            )

        return diagnostics

    def _validate_cross_references(
        self, content: str, sections: Dict
    ) -> tuple[List[Diagnostic], Dict[str, str], Dict[str, str]]:
        """Validate cross-references to profiles (namespaces and profile variables).

        Args:
            content: Full file content
            sections: Parsed sections

        Returns:
            Tuple of (diagnostics, profile_files_dict, profile_programs_dict)
        """
        diagnostics: List[Diagnostic] = []
        profile_files_dict: Dict[str, str] = {}
        profile_programs_dict: Dict[str, str] = {}

        workspace_index = WorkspaceIndex(self.context)

        # Extract @profile directive inline
        profile_directive = None
        pattern = r"#\s+@profile\s*:?\s*(\w+)"
        for line in content.split("\n"):
            match = re.search(pattern, line)
            if match:
                profile_directive = match.group(1)
                break

        # Determine which profile to use
        profile_name = profile_directive
        if not profile_name:
            available_profiles = workspace_index.all_profile_names()
            if not available_profiles:
                return diagnostics, profile_files_dict, profile_programs_dict
            profile_name = sorted(available_profiles)[0]

        # Load the profile
        profile_path = workspace_index.get_profile_path(profile_name)
        if not profile_path:
            if profile_directive:
                self._add_diagnostic(
                    diagnostics,
                    DiagnosticSeverity.WARNING,
                    0,
                    0,
                    10,
                    f"Profile '{profile_directive}' not found in workspace",
                    "missing-profile-directive",
                )
            return diagnostics, profile_files_dict, profile_programs_dict

        # Load profile and extract data
        profile_validator = ProfileValidator(self.context)
        profile, profile_diagnostics = profile_validator.load_profile(profile_path)
        diagnostics.extend(profile_diagnostics)

        if not profile:
            return diagnostics, profile_files_dict, profile_programs_dict

        profile_files_dict = profile_validator.extract_profile_files(profile_path)
        profile_programs_dict = profile_validator.extract_profile_programs(profile_path)

        # Validate namespace references in code chunks
        if "snippet" in sections and profile_programs_dict:
            diagnostics.extend(
                self._validate_namespace_references(
                    sections["snippet"],
                    sections["snippet"].content,
                    profile_programs_dict.keys()
                )
            )

        # Validate profile variables
        if profile_files_dict:
            diagnostics.extend(
                self._validate_profile_variable_usage(content, profile_files_dict.keys())
            )

        return diagnostics, profile_files_dict, profile_programs_dict

    def _validate_namespace_references(
        self, section, snippet_content: str, available_programs: Set[str]
    ) -> List[Diagnostic]:
        """Validate that namespace references exist in profile.

        Args:
            snippet_content: Content of snippet section
            available_programs: Set of available program names from profile

        Returns:
            List of diagnostics
        """
        diagnostics: List[Diagnostic] = []

        if not available_programs:
            return diagnostics

        # Find all code chunks with namespace options
        lines = snippet_content.split("\n")
        for line_num, line in enumerate(lines):
            if line.startswith("@") and "namespace=" in line:
                # Parse namespace reference
                match = re.search(r"namespace=(\w+)", line)
                if match:
                    namespace_ref = match.group(1)
                    if namespace_ref not in available_programs:
                        self._add_diagnostic(
                            diagnostics,
                            DiagnosticSeverity.ERROR,
                            section.start_line + line_num,
                            0,
                            50,
                            f"Namespace reference '{namespace_ref}' not found in profile. "
                            f"Available programs: {', '.join(sorted(available_programs))}",
                            "missing-namespace-reference",
                        )

        return diagnostics

    def _validate_profile_variable_usage(
        self, content: str, available_profile_files: Set[str]
    ) -> List[Diagnostic]:
        """Validate that profile_ variables reference existing profile files.

        Args:
            content: Full file content
            available_profile_files: Set of available file variable names from profile

        Returns:
            List of diagnostics
        """
        diagnostics: List[Diagnostic] = []

        # Find all profile_ variables
        profile_var_pattern = re.compile(r"%\(profile_(\w+)\)[sdifxobe]")

        for line_num, line in enumerate(content.split("\n")):
            for match in profile_var_pattern.finditer(line):
                file_key = match.group(1)
                if file_key not in available_profile_files:
                    self._add_diagnostic(
                        diagnostics,
                        DiagnosticSeverity.ERROR,
                        line_num,
                        match.start(),
                        match.end(),
                        f"Profile file variable 'profile_{file_key}' not found in profile. "
                        f"Available files: {', '.join(sorted(available_profile_files))}",
                        "missing-profile-variable",
                    )

        return diagnostics

    def _validate_io_declarations(
        self, snippet_content: str, defined_variables: Set[str]
    ) -> List[Diagnostic]:
        """Validate I/O declarations against defined variables.

        Args:
            snippet_content: Content of snippet section
            defined_variables: Set of defined argument variables

        Returns:
            List of diagnostics
        """
        diagnostics: List[Diagnostic] = []

        # Parse I/O declarations
        input_vars, output_vars = IODeclarationParser.parse_io_declarations(
            snippet_content
        )

        # Validate input variables
        for var_name in input_vars:
            if var_name not in defined_variables and not var_name.startswith(
                "profile_"
            ):
                self._add_diagnostic(
                    diagnostics,
                    DiagnosticSeverity.ERROR,
                    0,
                    0,
                    10,
                    f"I/O declaration references undefined input variable '{var_name}'",
                    "missing-input-variable",
                )

        # Validate output variables
        for var_name in output_vars:
            if var_name not in defined_variables and not var_name.startswith(
                "profile_"
            ):
                self._add_diagnostic(
                    diagnostics,
                    DiagnosticSeverity.ERROR,
                    0,
                    0,
                    10,
                    f"I/O declaration references undefined output variable '{var_name}'",
                    "missing-output-variable",
                )

        return diagnostics

    def _extract_results_variables(self, snippet: Optional[SnippetMd], section, diagnostics: List[Diagnostic]) -> tuple[Set[str], Dict[str, Any]]:
        """Extract variable names and values from results section using SnippetMd.

        The results section returns a dictionary. Keys from that dictionary
        become available as %(results_<key>)s variables.

        Calls snippet.results() with dummy arguments (using UPPERCASE argument
        names to get meaningful output).

        Args:
            snippet: SnippetMd instance (or None to skip extraction)
            section: Results section (ParsedSection)
            diagnostics: List to append diagnostics to

        Returns:
            Tuple of (Set of variable names, Dict of variable names to values)
        """
        results_vars: Set[str] = set()
        results_dict: Dict[str, Any] = {}

        if not snippet or not section:
            return results_vars, results_dict

        try:
            # Extract argument names from snippet's arguments using ArgumentList
            dummy_args = {}
            if "arguments" in snippet.mod:
                arg_list = ArgumentList("snippet", snippet.mod["arguments"])
                # Create dummy values using UPPERCASE argument names
                # This ensures results chunk runs with meaningful values
                for arg_dict in arg_list.arguments:
                    arg_names = arg_dict.get("argument", "").split("/")
                    for arg_name in arg_names:
                        arg_name = arg_name.strip()
                        if arg_name:
                            dummy_args[arg_name] = arg_name.upper()

            # Call results() method to get the dictionary
            results_output = snippet.results(dummy_args)
            if isinstance(results_output, dict):
                results_vars.update(results_output.keys())
                results_dict = results_output
                return results_vars, results_dict
        except FileNotFoundError:
            self._add_diagnostic(
                diagnostics,
                DiagnosticSeverity.ERROR,
                section.start_line,
                0,
                10,
                "Results chunk could not execute.\n"
                "Check for shebang line or syntax errors in the code.",
                "missing-results-output",
            )
        except KeyError:
            self._add_diagnostic(
                diagnostics,
                DiagnosticSeverity.ERROR,
                section.start_line,
                0,
                10,
                "Results chunk could not execute.\n"
                "There are no corresponding arguments to replace in the chunk",
                "wrong-results-argument",
            )

        return results_vars, results_dict

    def _runtime_validation(self, snippet: Optional[SnippetMd]) -> List[Diagnostic]:
        """Perform runtime validation using the reused SnippetMd instance.

        Validates that the snippet can be loaded and requirements parsed.

        Args:
            snippet: SnippetMd instance (or None if creation failed)

        Returns:
            List of diagnostics
        """
        diagnostics: List[Diagnostic] = []

        if not snippet:
            self._add_diagnostic(
                diagnostics,
                DiagnosticSeverity.ERROR,
                0,
                0,
                10,
                "Could not create SnippetMd instance for runtime validation",
                "snippet-load-error",
            )
            return diagnostics

        # Try to parse requirements (ensures bio_pype can parse it)
        try:
            _ = snippet.requirements()
        except Exception as e:
            self._add_diagnostic(
                diagnostics,
                DiagnosticSeverity.ERROR,
                0,
                0,
                10,
                f"Failed to parse requirements: {e}",
                "requirements-parse-error",
            )

        return diagnostics

    def _extract_parsed_arguments(self, section) -> Dict[str, str]:
        """Extract parsed arguments with help text for completions using bio_pype API.

        Uses ArgumentList from bio_pype, the same class that processes arguments
        during snippet execution, ensuring consistency.

        Args:
            section: ParsedSection object for arguments section

        Returns:
            Dict mapping argument names to help text
        """
        if not section:
            return {}

        try:
            content = section.content.strip()
            # Use ArgumentList from bio_pype API (same as actual snippet execution)
            arg_list = ArgumentList("snippet", content)

            # Extract help text for each argument
            arguments = {}
            for arg_dict in arg_list.arguments:
                help_text = arg_dict.get("options", {}).get("help", "")
                # Extract all argument name variants (e.g., "bam/b" -> ["bam", "b"])
                arg_names = arg_dict.get("argument", "").split("/")
                for name in arg_names:
                    name = name.strip()
                    if name:
                        arguments[name] = help_text

            return arguments
        except Exception as e:
            logger.debug(f"Could not extract arguments using ArgumentList: {e}")
            return {}

    def _extract_parsed_requirements(self, snippet: Optional[SnippetMd]) -> Dict[str, Any]:
        """Extract parsed requirements for completions using SnippetMd API.

        Uses the reused SnippetMd instance to call requirements() and get the
        actual requirements dictionary, ensuring consistency with bio_pype's parsing.

        Args:
            snippet: SnippetMd instance (or None to skip extraction)

        Returns:
            Dict mapping requirement keys to values
        """
        if not snippet:
            return {}

        try:
            requirements = snippet.requirements()
            if isinstance(requirements, dict):
                return requirements
        except Exception as e:
            logger.debug(f"Could not extract requirements from snippet: {e}")

        return {}

