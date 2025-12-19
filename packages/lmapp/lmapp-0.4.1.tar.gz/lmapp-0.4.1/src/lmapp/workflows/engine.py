"""Workflow engine for agentic multi-step tasks."""

import aiofiles
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TaskResult:
    """Result of task execution."""

    task_id: str
    status: TaskStatus
    output: Any
    error: Optional[str] = None
    duration_ms: float = 0.0


@dataclass
class WorkflowStep:
    """Single step in a workflow."""

    id: str
    name: str
    tool: str
    args: Dict[str, Any]
    condition: Optional[str] = None  # Optional condition to run step
    retry_count: int = 0
    timeout_seconds: int = 300


@dataclass
class WorkflowContext:
    """Context passed through workflow execution."""

    variables: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, TaskResult] = field(default_factory=dict)
    audit_log: List[str] = field(default_factory=list)

    def set_var(self, key: str, value: Any) -> None:
        """Set workflow variable."""
        self.variables[key] = value

    def get_var(self, key: str, default: Any = None) -> Any:
        """Get workflow variable."""
        return self.variables.get(key, default)

    def log_action(self, action: str) -> None:
        """Log action in audit trail."""
        self.audit_log.append(action)


class WorkflowTool(ABC):
    """Abstract base for workflow tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass

    @abstractmethod
    async def execute(self, args: Dict[str, Any], context: WorkflowContext) -> Any:
        """Execute tool.

        Args:
            args: Tool arguments
            context: Workflow context

        Returns:
            Tool output
        """
        pass

    @abstractmethod
    def validate_args(self, args: Dict[str, Any]) -> bool:
        """Validate tool arguments.

        Args:
            args: Arguments to validate

        Returns:
            True if valid
        """
        pass


class FileOperationsTool(WorkflowTool):
    """Tool for file operations."""

    @property
    def name(self) -> str:
        return "file_ops"

    async def execute(self, args: Dict[str, Any], context: WorkflowContext) -> Any:
        """Execute file operation.

        Args:
            args: Must contain 'operation' (read/write/list) and 'path'
            context: Workflow context

        Returns:
            File operation result
        """
        operation = args.get("operation", "").lower()
        path = args.get("path", "")

        context.log_action(f"file_ops:{operation}:{path}")

        if operation == "read":
            try:
                async with aiofiles.open(path, "r") as f:
                    return await f.read()
            except Exception as e:
                raise ValueError(f"Failed to read {path}: {e}")

        elif operation == "write":
            content = args.get("content", "")
            try:
                async with aiofiles.open(path, "w") as f:
                    await f.write(content)
                return f"Wrote {len(content)} bytes to {path}"
            except Exception as e:
                raise ValueError(f"Failed to write {path}: {e}")

        elif operation == "list":
            try:
                from pathlib import Path

                p = Path(path)
                # iterdir is sync, but usually fast enough. 
                # For strict async, we'd use run_in_executor, but let's keep it simple for now.
                items = list(p.iterdir())
                return [str(item) for item in items]
            except Exception as e:
                raise ValueError(f"Failed to list {path}: {e}")

        raise ValueError(f"Unknown operation: {operation}")

    def validate_args(self, args: Dict[str, Any]) -> bool:
        """Validate file operation args."""
        required = {"operation", "path"}
        return required.issubset(args.keys())


class CodeExecutionTool(WorkflowTool):
    """Tool for executing Python code."""

    @property
    def name(self) -> str:
        return "code_exec"

    async def execute(self, args: Dict[str, Any], context: WorkflowContext) -> Any:
        """Execute Python code.

        Args:
            args: Must contain 'code' string
            context: Workflow context

        Returns:
            Code execution result
        """
        code = args.get("code", "")
        context.log_action(f"code_exec:{len(code)} chars")

        try:
            # Create safe execution environment
            exec_globals = {
                "__builtins__": {
                    "len": len,
                    "str": str,
                    "int": int,
                    "float": float,
                    "list": list,
                    "dict": dict,
                    "print": print,
                    "range": range,
                },
                "context": context,
            }

            # Execute code
            # exec is blocking. For true async, we should use run_in_executor.
            # But for now, we just match the async signature.
            exec(code, exec_globals)

            return "Code executed successfully"
        except Exception as e:
            raise ValueError(f"Code execution failed: {e}")

    def validate_args(self, args: Dict[str, Any]) -> bool:
        """Validate code execution args."""
        return "code" in args and isinstance(args["code"], str)


class WorkflowEngine:
    """Executes multi-step workflows with tools."""

    def __init__(self):
        """Initialize workflow engine."""
        self.tools: Dict[str, WorkflowTool] = {}
        self._register_builtin_tools()

    def _register_builtin_tools(self) -> None:
        """Register built-in tools."""
        self.register_tool(FileOperationsTool())
        self.register_tool(CodeExecutionTool())

    def register_tool(self, tool: WorkflowTool) -> None:
        """Register a workflow tool.

        Args:
            tool: Tool to register
        """
        self.tools[tool.name] = tool

    async def execute_workflow(self, steps: List[WorkflowStep], context: Optional[WorkflowContext] = None) -> WorkflowContext:
        """Execute a workflow.

        Args:
            steps: List of workflow steps
            context: Optional initial context

        Returns:
            Final workflow context with results
        """
        if context is None:
            context = WorkflowContext()
        context.log_action("Workflow started")

        for step in steps:
            # Check condition
            if step.condition and not self._eval_condition(step.condition, context):
                context.results[step.id] = TaskResult(
                    task_id=step.id,
                    status=TaskStatus.SKIPPED,
                    output=None,
                )
                context.log_action(f"Step {step.id} skipped (condition false)")
                continue

            # Execute step
            try:
                result = await self._execute_step(step, context)
                context.results[step.id] = result
                context.log_action(f"Step {step.id} completed: {result.status.value}")
            except Exception as e:
                error_result = TaskResult(
                    task_id=step.id,
                    status=TaskStatus.FAILED,
                    output=None,
                    error=str(e),
                )
                context.results[step.id] = error_result
                context.log_action(f"Step {step.id} failed: {str(e)}")

                # Stop workflow on failure
                break

        context.log_action("Workflow completed")
        return context

    async def _execute_step(self, step: WorkflowStep, context: WorkflowContext) -> TaskResult:
        """Execute a single step.

        Args:
            step: Step to execute
            context: Workflow context

        Returns:
            Task result
        """
        if step.tool not in self.tools:
            raise ValueError(f"Unknown tool: {step.tool}")

        tool = self.tools[step.tool]

        # Validate args
        if not tool.validate_args(step.args):
            raise ValueError(f"Invalid args for {step.tool}")

        # Execute with retry
        last_error = None
        for attempt in range(step.retry_count + 1):
            try:
                output = await tool.execute(step.args, context)
                return TaskResult(
                    task_id=step.id,
                    status=TaskStatus.SUCCESS,
                    output=output,
                )
            except Exception as e:
                last_error = e
                if attempt < step.retry_count:
                    context.log_action(f"Step {step.id} retry {attempt + 1}")
                if attempt < step.retry_count:
                    context.log_action(f"Step {step.id} retry {attempt + 1}")

        raise last_error or ValueError("Execution failed")

    def _eval_condition(self, condition: str, context: WorkflowContext) -> bool:
        """Evaluate conditional expression.

        Args:
            condition: Condition string
            context: Workflow context

        Returns:
            Condition result
        """
        try:
            # Simple variable substitution
            expr = condition
            for key, value in context.variables.items():
                expr = expr.replace(f"${{{key}}}", str(value))

            # Evaluate as Python boolean
            return bool(eval(expr, {"__builtins__": {}}, context.variables))
        except Exception as e:
            print(f"Condition evaluation failed: {e}")
            return False
