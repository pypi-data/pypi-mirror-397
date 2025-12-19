from pathlib import Path
from typing import Any, Dict, Optional
from lmapp.plugins.plugin_manager import BasePlugin, PluginMetadata


class EditorPlugin(BasePlugin):
    """
    Plugin for reading and writing files.
    """

    def __init__(self):
        self._metadata = PluginMetadata(
            name="editor", version="0.1.0", description="Read and write files in the workspace", author="LMAPP Team", tags=["system", "file", "editor"]
        )

    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        pass

    def execute(self, action: str, file_path: str, content: Optional[str] = None, *args, **kwargs) -> str:
        """
        Execute file operations.

        Args:
            action: 'read' or 'write'
            file_path: Path to the file
            content: Content to write (required for 'write')

        Returns:
            File content or status message
        """
        path = Path(file_path)

        try:
            if action == "read":
                if not path.exists():
                    return f"Error: File {file_path} does not exist."
                return path.read_text()

            elif action == "write":
                if content is None:
                    return "Error: Content required for write operation."

                # Ensure directory exists
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
                return f"Successfully wrote to {file_path}"

            else:
                return f"Unknown action: {action}"

        except Exception as e:
            return f"Error performing {action} on {file_path}: {str(e)}"
