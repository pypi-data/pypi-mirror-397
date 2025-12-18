"""Hover information handler for LSP server.

Provides contextual information when hovering over elements in code.
Handles snippet descriptions, section headers, variables, and YAML keys.
"""

import logging
import re
from pathlib import Path
from typing import Optional

from lsprotocol import types

from pype.utils.snippets import SnippetMd

logger = logging.getLogger("bio_pype_lsp.hover")


class HoverHandler:
    """Manages hover information for different file types."""

    def __init__(self, server):
        """Initialize hover handler.

        Args:
            server: BioPypeLspServer instance
        """
        self.server = server

    def get_hover_info(
        self, uri: str, position: types.Position
    ) -> Optional[types.Hover]:
        """Get hover information at a specific position.

        Args:
            uri: Document URI (file:// format)
            position: Position in document (line, character)

        Returns:
            Hover information or None if not available
        """
        try:
            file_path = Path(uri.replace("file://", ""))

            if not self.server.validation_context:
                return None

            # Get document content from workspace
            try:
                text_document = self.server.workspace.get_text_document(uri)
                content = text_document.source
                logger.debug(f"Using workspace content for hover: {file_path.name}")
            except Exception as e:
                logger.debug(f"Could not get text document from workspace: {e}")
                # Fall back to disk
                if file_path.exists():
                    content = file_path.read_text()
                    logger.debug(f"Reading hover content from disk: {file_path.name}")
                else:
                    logger.debug(f"No content available for hover: {file_path.name}")
                    return None

            # Get appropriate handler based on file type
            if file_path.suffix == ".md":
                return self._get_snippet_hover(file_path, position, content)
            elif file_path.suffix in [".yaml", ".yml"]:
                return self._get_yaml_hover(file_path, position, content)

        except Exception as e:
            logger.error(f"Error getting hover info for {uri}: {e}", exc_info=True)

        return None

    def _get_snippet_hover(
        self, file_path: Path, position: types.Position, content: str
    ) -> Optional[types.Hover]:
        """Get hover information for snippet (.md) files.

        Args:
            file_path: Path to snippet file
            position: Position in document
            content: File content

        Returns:
            Hover information with basic details
        """
        try:
            lines = content.split("\n")
            if position.line >= len(lines):
                return None

            line = lines[position.line]
            char_pos = position.character

            # Check if hovering over a section header
            if line.strip().startswith("##"):
                section = line.strip().replace("##", "").strip()
                hover_text = f"**Section:** `{section}`"
                return types.Hover(
                    contents=types.MarkupContent(
                        kind=types.MarkupKind.Markdown, value=hover_text
                    )
                )

            # Check if hovering over a variable reference
            if "%" in line and "(" in line:
                # Extract variable name at cursor
                var_match = self._extract_variable_at_position(line, char_pos)
                if var_match:
                    var_name = var_match
                    hover_text = f"**Variable:** `{var_name}`"
                    return types.Hover(
                        contents=types.MarkupContent(
                            kind=types.MarkupKind.Markdown, value=hover_text
                        )
                    )

            # Default: show snippet info
            try:
                snippet = SnippetMd(file_path.parent, file_path.stem, str(file_path))
                if hasattr(snippet, "mod") and snippet.mod:
                    description = snippet.mod.get("description", "").strip()
                    if description:
                        hover_text = f"**{file_path.stem}**\n\n{description}"
                        return types.Hover(
                            contents=types.MarkupContent(
                                kind=types.MarkupKind.Markdown, value=hover_text
                            )
                        )
            except Exception as e:
                logger.debug(f"Could not load snippet metadata: {e}")
                # Return basic filename if can't load snippet
                hover_text = f"**File:** `{file_path.name}`"
                return types.Hover(
                    contents=types.MarkupContent(
                        kind=types.MarkupKind.Markdown, value=hover_text
                    )
                )

        except Exception as e:
            logger.debug(f"Error getting snippet hover: {e}")

        return None

    def _extract_variable_at_position(self, line: str, char_pos: int) -> Optional[str]:
        """Extract variable name at cursor position.

        Handles patterns like %(variable_name)s

        Args:
            line: Current line text
            char_pos: Character position in line

        Returns:
            Variable name or None
        """
        # Find all variables in the line
        for match in re.finditer(r"%\(([a-zA-Z_][a-zA-Z0-9_]*)\)s", line):
            start, end = match.span()
            if start <= char_pos <= end:
                return match.group(1)

        return None

    def _get_yaml_hover(
        self, file_path: Path, position: types.Position, content: str
    ) -> Optional[types.Hover]:
        """Get hover information for YAML files (profiles/pipelines).

        Args:
            file_path: Path to YAML file
            position: Position in document
            content: File content

        Returns:
            Hover information with context
        """
        try:
            # Determine if profile or pipeline based on content or directory
            if "programs:" in content:
                # Likely a profile
                return self._get_profile_hover(file_path, position, content)
            else:
                # Likely a pipeline
                return self._get_pipeline_hover(file_path, position, content)

        except Exception as e:
            logger.debug(f"Error getting YAML hover: {e}")

        return None

    def _get_profile_hover(
        self, file_path: Path, position: types.Position, content: str
    ) -> Optional[types.Hover]:
        """Get hover information for profile YAML files.

        Args:
            file_path: Path to profile file
            position: Position in document
            content: File content

        Returns:
            Hover information with basic key details
        """
        try:
            lines = content.split("\n")
            line_num = position.line

            if line_num >= len(lines):
                return None

            line = lines[line_num]

            # Extract the key being hovered over
            if ":" in line:
                key = line.split(":")[0].strip()
                if key and not key.startswith("#"):
                    hover_text = f"**Key:** `{key}`"
                    return types.Hover(
                        contents=types.MarkupContent(
                            kind=types.MarkupKind.Markdown,
                            value=hover_text,
                        )
                    )

        except Exception as e:
            logger.debug(f"Error getting profile hover: {e}")

        return None

    def _get_pipeline_hover(
        self, file_path: Path, position: types.Position, content: str
    ) -> Optional[types.Hover]:
        """Get hover information for pipeline YAML files.

        Args:
            file_path: Path to pipeline file
            position: Position in document
            content: File content

        Returns:
            Hover information with basic key details
        """
        try:
            lines = content.split("\n")
            line_num = position.line

            if line_num >= len(lines):
                return None

            line = lines[line_num]

            # Extract the key being hovered over
            if ":" in line:
                key = line.split(":")[0].strip()
                if key and not key.startswith("#"):
                    hover_text = f"**Key:** `{key}`"
                    return types.Hover(
                        contents=types.MarkupContent(
                            kind=types.MarkupKind.Markdown,
                            value=hover_text,
                        )
                    )

        except Exception as e:
            logger.debug(f"Error getting pipeline hover: {e}")

        return None
