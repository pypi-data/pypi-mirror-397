"""Pipeline validation implementation.

Validates bio_pype YAML pipeline configurations.
"""

from pathlib import Path
from typing import Any, Dict, List, Set

import yaml

from pype.utils.pipeline import Pipeline
from pype.validation.context import WorkspaceIndex
from pype.validation.core import (
    Diagnostic,
    DiagnosticSeverity,
    Location,
    ValidationContext,
    ValidationResult,
)


class PipelineValidator:
    """Validator for bio_pype YAML pipelines.

    Validates both old format (2.0.0 with nested items) and new format
    (2.1.0 with flat steps and depends_on).

    Validates:
    - YAML structure and parsing
    - API version (2.0.0 or 2.1.0)
    - Info section (description, arguments, defaults)
    - Items/Steps structure
    - Snippet references (all snippets must exist)
    - Argument usage (pipeline arguments referenced correctly)
    - DAG structure (no circular dependencies)
    - Argument formats (%(name)s style)
    - Runtime validation (attempting to load with Pipeline class)
    """

    # Valid pipeline API versions
    VALID_APIS = {"2.0.0", "2.1.0"}

    def __init__(self, context: ValidationContext) -> None:
        """Initialize pipeline validator.

        Args:
            context: ValidationContext for workspace information
        """
        self.context = context

    def validate(self, file_path: Path) -> ValidationResult:
        """Validate a pipeline file.

        Args:
            file_path: Path to the pipeline file to validate

        Returns:
            ValidationResult with diagnostics
        """
        diagnostics: List[Diagnostic] = []

        # 1. Parse YAML
        try:
            with open(file_path, "r") as f:
                pipeline_dict = yaml.safe_load(f)
        except yaml.YAMLError as e:
            # Extract line number from error if possible
            line = 0
            if hasattr(e, "problem_mark"):
                line = e.problem_mark.line

            return ValidationResult(
                file_path,
                "pipeline",
                [
                    Diagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        location=Location(line, 0, 10),
                        message=f"YAML syntax error: {str(e).split(chr(10))[0]}",
                        code="yaml-parse-error",
                    )
                ],
            )
        except Exception as e:
            return ValidationResult(
                file_path,
                "pipeline",
                [
                    Diagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        location=Location(0, 0, 10),
                        message=f"Failed to read file: {e}",
                        code="file-read-error",
                    )
                ],
            )

        if not isinstance(pipeline_dict, dict):
            # During keystroke editing, YAML can become temporarily malformed
            if pipeline_dict is None:
                message = "Pipeline is empty or invalid YAML"
            elif isinstance(pipeline_dict, list):
                message = "Pipeline content starts with a list - should start with 'api:' or 'info:' section"
            else:
                message = f"Pipeline must be a YAML object (mapping), not {type(pipeline_dict).__name__}"

            return ValidationResult(
                file_path,
                "pipeline",
                [
                    Diagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        location=Location(0, 0, 10),
                        message=message,
                        code="invalid-pipeline-structure",
                    )
                ],
            )

        # 2. Validate info section
        diagnostics.extend(self._validate_info(pipeline_dict))

        # 3. Validate items or steps
        if "items" in pipeline_dict:
            diagnostics.extend(self._validate_items(pipeline_dict["items"]))
        elif "steps" in pipeline_dict:
            diagnostics.extend(self._validate_steps(pipeline_dict["steps"]))
        else:
            diagnostics.append(
                Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    location=Location(0, 0, 10),
                    message="Pipeline must have either 'items' (API 2.0.0) or 'steps' (API 2.1.0)",
                    code="missing-items-or-steps",
                )
            )

        # 4. Validate snippet references (cross-file)
        diagnostics.extend(self._validate_snippet_references(pipeline_dict))

        # 5. Runtime validation (Pipeline class handles item parsing with PipelineItem)
        diagnostics.extend(self._runtime_validation(file_path))

        is_valid = not any(d.severity == DiagnosticSeverity.ERROR for d in diagnostics)
        return ValidationResult(file_path, "pipeline", diagnostics, is_valid)

    def _validate_info(self, pipeline_dict: Dict[str, Any]) -> List[Diagnostic]:
        """Validate pipeline info section.

        Args:
            pipeline_dict: Parsed pipeline YAML

        Returns:
            List of diagnostics
        """
        diagnostics: List[Diagnostic] = []

        if "info" not in pipeline_dict:
            diagnostics.append(
                Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    location=Location(0, 0, 10),
                    message="Missing required 'info' section",
                    code="missing-info-section",
                )
            )
            return diagnostics

        info = pipeline_dict["info"]
        if not isinstance(info, dict):
            diagnostics.append(
                Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    location=Location(0, 0, 10),
                    message="'info' section must be a YAML object",
                    code="invalid-info-section",
                )
            )
            return diagnostics

        # Check for API version (optional, defaults to 2.0.0 if not specified)
        if "api" in info and info["api"] not in self.VALID_APIS:
            diagnostics.append(
                Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    location=Location(0, 0, 10),
                    message=f"Invalid API version '{info['api']}'. Must be one of: "
                    + ", ".join(self.VALID_APIS),
                    code="invalid-api-version",
                )
            )

        # Check for description
        if "description" not in info:
            diagnostics.append(
                Diagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    location=Location(0, 0, 10),
                    message="Missing 'info.description' field",
                    code="missing-description",
                )
            )

        return diagnostics

    def _validate_items(self, items: Any) -> List[Diagnostic]:
        """Validate pipeline items (API 2.0.0 nested structure).

        Args:
            items: Items list from pipeline

        Returns:
            List of diagnostics
        """
        diagnostics: List[Diagnostic] = []

        if not isinstance(items, list):
            diagnostics.append(
                Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    location=Location(0, 0, 10),
                    message="'items' must be a list",
                    code="invalid-items-format",
                )
            )
            return diagnostics

        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                diagnostics.append(
                    Diagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        location=Location(idx, 0, 10),
                        message=f"Item {idx} must be a YAML object",
                        code="invalid-item-format",
                    )
                )
                continue

            # Validate required item fields
            if "name" not in item:
                diagnostics.append(
                    Diagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        location=Location(idx, 0, 10),
                        message=f"Item {idx} missing 'name' field",
                        code="missing-item-name",
                    )
                )

            if "type" not in item:
                diagnostics.append(
                    Diagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        location=Location(idx, 0, 10),
                        message=f"Item {idx} missing 'type' field (must be 'snippet', 'batch_snippet', 'pipeline', or 'batch_pipeline')",
                        code="missing-item-type",
                    )
                )
            elif item["type"] not in {
                "snippet",
                "batch_snippet",
                "pipeline",
                "batch_pipeline",
            }:
                diagnostics.append(
                    Diagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        location=Location(idx, 0, 10),
                        message=f"Item {idx} has invalid type '{item['type']}' (must be 'snippet', 'batch_snippet', 'pipeline', or 'batch_pipeline')",
                        code="invalid-item-type",
                    )
                )

            # Recursively validate nested dependencies
            if "dependencies" in item and isinstance(item["dependencies"], dict):
                if "items" in item["dependencies"]:
                    diagnostics.extend(
                        self._validate_items(item["dependencies"]["items"])
                    )

        return diagnostics

    def _validate_steps(self, steps: Any) -> List[Diagnostic]:
        """Validate pipeline steps (API 2.1.0 flat structure).

        Args:
            steps: Steps list from pipeline

        Returns:
            List of diagnostics
        """
        diagnostics: List[Diagnostic] = []

        if not isinstance(steps, list):
            diagnostics.append(
                Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    location=Location(0, 0, 10),
                    message="'steps' must be a list",
                    code="invalid-steps-format",
                )
            )
            return diagnostics

        step_ids: Set[str] = set()

        for idx, step in enumerate(steps):
            if not isinstance(step, dict):
                diagnostics.append(
                    Diagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        location=Location(idx, 0, 10),
                        message=f"Step {idx} must be a YAML object",
                        code="invalid-step-format",
                    )
                )
                continue

            # Validate required step fields
            if "step_id" not in step:
                diagnostics.append(
                    Diagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        location=Location(idx, 0, 10),
                        message=f"Step {idx} missing 'step_id' field",
                        code="missing-step-id",
                    )
                )
            else:
                step_ids.add(step["step_id"])

            if "name" not in step:
                diagnostics.append(
                    Diagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        location=Location(idx, 0, 10),
                        message=f"Step {idx} missing 'name' field",
                        code="missing-step-name",
                    )
                )

            if "type" not in step:
                diagnostics.append(
                    Diagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        location=Location(idx, 0, 10),
                        message=f"Step {idx} missing 'type' field (must be 'snippet', 'batch_snippet', 'pipeline', or 'batch_pipeline')",
                        code="missing-step-type",
                    )
                )
            elif step["type"] not in {
                "snippet",
                "batch_snippet",
                "pipeline",
                "batch_pipeline",
            }:
                diagnostics.append(
                    Diagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        location=Location(idx, 0, 10),
                        message=f"Step {idx} has invalid type '{step['type']}' (must be 'snippet', 'batch_snippet', 'pipeline', or 'batch_pipeline')",
                        code="invalid-step-type",
                    )
                )

        return diagnostics

    def _validate_snippet_references(
        self, pipeline_dict: Dict[str, Any]
    ) -> List[Diagnostic]:
        """Validate that all referenced snippets/pipelines exist in workspace.

        Uses bio_pype's built-in snippet discovery which handles both
        Python snippet modules and Markdown snippets.

        Args:
            pipeline_dict: Parsed pipeline YAML

        Returns:
            List of diagnostics
        """
        diagnostics: List[Diagnostic] = []

        # Discover snippets (both markdown and Python modules)
        workspace_index = WorkspaceIndex(self.context)
        available_snippets = workspace_index.all_snippet_names()

        # Also discover Python snippet modules in the snippets directory
        if self.context.workspace_root:
            snippets_dir = self.context.workspace_root / "snippets"
            if snippets_dir.exists():
                # Find all .py files (snippet modules) in snippets directory
                for py_file in snippets_dir.glob("*.py"):
                    # Use filename without .py as snippet name
                    snippet_name = py_file.stem
                    if snippet_name != "__init__":
                        available_snippets.add(snippet_name)

        # Discover pipelines using WorkspaceIndex
        available_pipelines = workspace_index.all_pipeline_names()

        # Collect all items/steps from pipeline
        items_to_check = []
        if "items" in pipeline_dict and isinstance(pipeline_dict["items"], list):
            items_to_check.extend(pipeline_dict["items"])
        if "steps" in pipeline_dict and isinstance(pipeline_dict["steps"], list):
            items_to_check.extend(pipeline_dict["steps"])

        # Recursively check all items
        def check_items_recursive(items: List[Any]) -> None:
            for item in items:
                if not isinstance(item, dict):
                    continue

                item_type = item.get("type")
                if item_type in ("snippet", "batch_snippet"):
                    snippet_name = item.get("name")
                    if snippet_name and snippet_name not in available_snippets:
                        diagnostics.append(
                            Diagnostic(
                                severity=DiagnosticSeverity.ERROR,
                                location=Location(0, 0, 10),
                                message=f"Snippet '{snippet_name}' not found. Available: {', '.join(sorted(available_snippets))}",
                                code="missing-snippet-reference",
                            )
                        )

                elif item_type in ("pipeline", "batch_pipeline"):
                    pipeline_name = item.get("name")
                    if pipeline_name and pipeline_name not in available_pipelines:
                        diagnostics.append(
                            Diagnostic(
                                severity=DiagnosticSeverity.ERROR,
                                location=Location(0, 0, 10),
                                message=f"Pipeline '{pipeline_name}' not found. Available: {', '.join(sorted(available_pipelines))}",
                                code="missing-pipeline-reference",
                            )
                        )

                # Check nested dependencies
                if "dependencies" in item and isinstance(item["dependencies"], dict):
                    if "items" in item["dependencies"] and isinstance(
                        item["dependencies"]["items"], list
                    ):
                        check_items_recursive(item["dependencies"]["items"])

        check_items_recursive(items_to_check)

        return diagnostics

    def _runtime_validation(self, file_path: Path) -> List[Diagnostic]:
        """Try to load pipeline using bio_pype Pipeline class.

        Note: Runtime validation requires PYPE_SNIPPETS to be properly configured
        in the environment. If PYPE_SNIPPETS points to the default installed
        package snippets only, this validation may fail for local/custom snippets.

        Cross-file validation (snippet reference checking) is more important
        and is already done before this step.

        Args:
            file_path: Path to pipeline file

        Returns:
            List of diagnostics (usually empty since cross-file validation is sufficient)
        """
        diagnostics: List[Diagnostic] = []

        try:
            pipeline_name = file_path.stem
            pipeline = Pipeline(str(file_path), pipeline_name)

            # If we got here, the pipeline loaded successfully
            return diagnostics

        except Exception as e:
            # Runtime validation via Pipeline class validates:
            # - API version compatibility
            # - Item/step structure using PipelineItem (handles both 2.0.0 and 2.1.0)
            # - Argument parsing
            # - Dependency resolution (DAG)
            #
            # We skip reporting "snippet not found" errors since cross-file validation
            # already checks snippet references. Other parsing errors are important.
            error_msg = str(e)
            error_type = type(e).__name__

            # Skip snippet-not-found errors (already validated cross-file)
            if "not found" in error_msg.lower() or "SnippetNotFoundError" in error_type:
                pass
            else:
                # Report all other errors (API version, parsing, dependency, etc.)
                diagnostics.append(
                    Diagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        location=Location(0, 0, 10),
                        message=f"Failed to load pipeline: {error_msg}",
                        code="pipeline-load-error",
                    )
                )

        return diagnostics
