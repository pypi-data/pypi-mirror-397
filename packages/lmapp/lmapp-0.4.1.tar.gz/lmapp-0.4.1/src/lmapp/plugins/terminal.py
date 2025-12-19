import subprocess
from typing import Any, Dict, Optional
from lmapp.plugins.plugin_manager import BasePlugin, PluginMetadata


class TerminalPlugin(BasePlugin):
    """
    Plugin for executing terminal commands.
    """

    def __init__(self):
        self._metadata = PluginMetadata(
            name="terminal", version="0.1.0", description="Execute terminal commands safely", author="LMAPP Team", tags=["system", "terminal", "shell"]
        )

    @property
    def metadata(self) -> PluginMetadata:
        return self._metadata

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        pass

    def execute(self, command: str, *args, **kwargs) -> str:
        """
        Execute a shell command.

        Args:
            command: The command string to execute

        Returns:
            Output of the command (stdout + stderr)
        """
        try:
            # Security warning: This allows arbitrary command execution
            # In a real scenario, we might want to sandbox this or ask for confirmation
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
            output = result.stdout
            if result.stderr:
                output += "\nSTDERR:\n" + result.stderr
            return output
        except Exception as e:
            return f"Error executing command: {str(e)}"
