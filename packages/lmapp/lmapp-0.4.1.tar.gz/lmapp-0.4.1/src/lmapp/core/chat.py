#!/usr/bin/env python3
"""
Chat Session Management
Handles single conversation session with an LLM backend
"""

from typing import List, Optional, Dict
from datetime import datetime
import re
from lmapp.backend.base import LLMBackend
from lmapp.utils.logging import logger
from lmapp.core.cache import ResponseCache
from lmapp.plugins.terminal import TerminalPlugin
from lmapp.plugins.editor import EditorPlugin


class ChatMessage:
    """Represents a single message in the conversation"""

    def __init__(self, role: str, content: str):
        """
        Initialize a chat message

        Args:
            role: "user" or "assistant"
            content: Message text
        """
        self.role = role
        self.content = content
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
        }


class ChatSession:
    """Manages a single conversation session"""

    def __init__(self, backend: LLMBackend, model: str = "tinyllama"):
        """
        Initialize a chat session

        Args:
            backend: LLMBackend instance to use for chat
            model: Model name to use (default: tinyllama)

        Raises:
            ValueError: If backend is not running
        """
        logger.debug(f"Creating ChatSession with backend={backend.backend_name()}, model={model}")

        if not backend.is_running():
            logger.error(f"Backend '{backend.backend_display_name()}' is not running")
            raise ValueError(
                f"❌ Backend '{backend.backend_display_name()}' is not running.\n" "Please run 'lmapp install' first, or start the backend manually."
            )

        self.backend = backend
        self.model = model
        self.history: List[ChatMessage] = []
        self.created_at = datetime.now()
        self.cache = ResponseCache()

        # Agent capabilities
        self.agent_mode = False
        self.terminal_plugin = TerminalPlugin()
        self.editor_plugin = EditorPlugin()
        self.system_prompt = ""

        logger.debug("ChatSession initialized successfully")

    def enable_agent_mode(self):
        """Enable agent capabilities (tools and loop)."""
        self.agent_mode = True
        self.system_prompt = """
You are an advanced AI assistant with access to the following tools:

1. Terminal: Execute shell commands.
   Usage: [TOOL: terminal command="ls -la"]

2. Editor: Read and write files.
   Usage: [TOOL: editor action="read" file_path="src/main.py"]
   Usage: [TOOL: editor action="write" file_path="src/main.py" content="..."]

When you need to perform an action, output the tool command.
The system will execute it and provide the result.
You can chain multiple actions.
"""
        logger.info("Agent mode enabled")

    def _build_prompt(self) -> str:
        """Construct full prompt from history."""
        full_prompt = ""
        if self.system_prompt:
            full_prompt += f"System: {self.system_prompt}\n\n"

        for msg in self.history:
            role = "User" if msg.role == "user" else "Assistant"
            full_prompt += f"{role}: {msg.content}\n\n"

        return full_prompt.strip()

    def _has_tool_call(self, text: str) -> bool:
        """Check if text contains a tool call."""
        return "[TOOL:" in text

    def _execute_tool(self, text: str) -> str:
        """Parse and execute tool call."""
        try:
            match = re.search(r"\[TOOL:\s*(\w+)\s+(.*?)\]", text, re.DOTALL)
            if not match:
                return "Error: Invalid tool format"

            tool_name = match.group(1).lower()
            args_str = match.group(2)

            # Parse args (simple key="value" parser)
            args = {}
            # Handle escaped quotes if possible, but simple regex for now
            for arg_match in re.finditer(r'(\w+)="(.*?)"', args_str, re.DOTALL):
                args[arg_match.group(1)] = arg_match.group(2)

            if tool_name == "terminal":
                cmd = args.get("command")
                if not cmd:
                    return "Error: Missing command argument"
                return self.terminal_plugin.execute(cmd)

            elif tool_name == "editor":
                action = args.get("action")
                path = args.get("file_path")
                content = args.get("content")
                if not action or not path:
                    return "Error: Missing action or file_path"
                return self.editor_plugin.execute(action, path, content)

            else:
                return f"Error: Unknown tool {tool_name}"

        except Exception as e:
            return f"Error executing tool: {str(e)}"

    def send_prompt(self, prompt: str, temperature: float = 0.7, on_tool_start=None, on_tool_end=None) -> str:
        """
        Send a prompt and get a response

        Args:
            prompt: User prompt
            temperature: LLM temperature (0.0-1.0)
            on_tool_start: Callback(tool_name, args)
            on_tool_end: Callback(output)

        Returns:
            Response text

        Raises:
            ValueError: If prompt is empty
            RuntimeError: If backend fails to respond
        """
        logger.debug(f"send_prompt: model={self.model}, temp={temperature}, prompt_len={len(prompt)}")

        if not prompt or not prompt.strip():
            logger.warning("Empty prompt attempted")
            raise ValueError("❌ Prompt cannot be empty")

        # Check cache for existing response
        # Note: Cache might be tricky with agents/history, but keeping for now
        cached_response = self.cache.get(prompt, self.model, self.backend.backend_name(), temperature)
        if cached_response and not self.agent_mode:
            logger.debug(f"Cache hit for prompt (model={self.model}, temperature={temperature})")
            self.history.append(ChatMessage("user", prompt))
            self.history.append(ChatMessage("assistant", cached_response))
            return cached_response

        # Add user message to history
        self.history.append(ChatMessage("user", prompt))

        try:
            # Loop for Agent Mode
            max_turns = 10
            current_turn = 0

            while current_turn < max_turns:
                # Build full prompt with history
                full_prompt = self._build_prompt()

                # Get response from backend
                logger.debug("Requesting response from backend")
                response = self.backend.chat(prompt=full_prompt, model=self.model, temperature=temperature)

                if not response:
                    logger.error("Backend returned empty response")
                    raise RuntimeError("Backend returned empty response")

                # Add assistant message to history
                self.history.append(ChatMessage("assistant", response))

                # Check for tools if in agent mode
                if self.agent_mode and self._has_tool_call(response):
                    logger.info("Tool call detected")

                    # Notify start
                    if on_tool_start:
                        # Extract tool name for display
                        match = re.search(r"\[TOOL:\s*(\w+)\s+(.*?)\]", response, re.DOTALL)
                        if match:
                            on_tool_start(match.group(1), match.group(2))

                    tool_output = self._execute_tool(response)

                    # Notify end
                    if on_tool_end:
                        on_tool_end(tool_output)

                    # Add tool output as user message (simulating system feedback)
                    self.history.append(ChatMessage("user", f"Tool Output:\n{tool_output}"))
                    current_turn += 1
                    continue

                # If no tool call or not agent mode, we are done
                # Cache the response (only the final one)
                self.cache.set(prompt, response, self.model, self.backend.backend_name(), temperature)
                return response

            return response  # Return last response if max turns reached

        except Exception as e:
            # Remove the user message if we failed to get response
            self.history.pop()
            logger.error(f"Backend error: {str(e)}", exc_info=True)

            # Provide actionable error message
            error_msg = str(e)
            if "connection" in error_msg.lower() or "refused" in error_msg.lower():
                raise RuntimeError(f"❌ Cannot connect to {self.backend.backend_display_name()}.\n" "Try restarting: lmapp install") from e
            elif "model" in error_msg.lower():
                models = self.backend.list_models()
                raise RuntimeError(f"❌ Model '{self.model}' not found.\n" f"Available models: {', '.join(models)}") from e
            else:
                raise RuntimeError(f"❌ Backend error: {error_msg}") from e

    def get_history(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get conversation history

        Args:
            limit: Maximum number of messages to return (None = all)

        Returns:
            List of messages as dictionaries
        """
        messages = [msg.to_dict() for msg in self.history]

        if limit:
            messages = messages[-limit:]

        return messages

    def get_history_text(self, limit: Optional[int] = None) -> str:
        """
        Get conversation history as formatted text

        Args:
            limit: Maximum number of messages to return (None = all)

        Returns:
            Formatted conversation text
        """
        messages = self.history
        if limit:
            messages = messages[-limit:]

        if not messages:
            return "(No messages yet)"

        text = []
        for msg in messages:
            timestamp = msg.timestamp.strftime("%H:%M:%S")
            role_label = "You" if msg.role == "user" else "AI"
            text.append(f"[{timestamp}] {role_label}: {msg.content}")

        return "\n".join(text)

    def clear_history(self) -> int:
        """
        Clear conversation history

        Returns:
            Number of messages cleared
        """
        count = len(self.history)
        self.history.clear()
        return count

    def get_stats(self) -> Dict:
        """
        Get session statistics

        Returns:
            Dictionary with session stats
        """
        return {
            "backend": self.backend.backend_name(),
            "model": self.model,
            "messages": len(self.history),
            "user_messages": sum(1 for m in self.history if m.role == "user"),
            "assistant_messages": sum(1 for m in self.history if m.role == "assistant"),
            "created_at": self.created_at.isoformat(),
            "duration_seconds": (datetime.now() - self.created_at).total_seconds(),
        }
