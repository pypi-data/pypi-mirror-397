"""Unit tests for workflow engine."""

import pytest
import asyncio
from pathlib import Path

from lmapp.workflows.engine import (
    CodeExecutionTool,
    FileOperationsTool,
    TaskStatus,
    WorkflowContext,
    WorkflowEngine,
    WorkflowStep,
)


class TestWorkflowContext:
    """Test workflow context."""

    def test_context_variables(self):
        """Test variable management."""
        context = WorkflowContext()

        context.set_var("key1", "value1")
        assert context.get_var("key1") == "value1"

        assert context.get_var("missing", "default") == "default"

    def test_context_audit_log(self):
        """Test audit logging."""
        context = WorkflowContext()

        context.log_action("action1")
        context.log_action("action2")

        assert len(context.audit_log) == 2
        assert "action1" in context.audit_log


class TestFileOperationsTool:
    """Test file operations tool."""

    def test_validate_args(self):
        """Test argument validation."""
        tool = FileOperationsTool()

        assert tool.validate_args({"operation": "read", "path": "/tmp/file"}) is True
        assert tool.validate_args({"operation": "read"}) is False

    def test_tool_name(self):
        """Test tool name."""
        tool = FileOperationsTool()
        assert tool.name == "file_ops"


class TestCodeExecutionTool:
    """Test code execution tool."""

    def test_validate_args(self):
        """Test argument validation."""
        tool = CodeExecutionTool()

        assert tool.validate_args({"code": "x = 1"}) is True
        assert tool.validate_args({"code": 123}) is False
        assert tool.validate_args({}) is False

    def test_tool_name(self):
        """Test tool name."""
        tool = CodeExecutionTool()
        assert tool.name == "code_exec"


class TestWorkflowEngine:
    """Test workflow execution engine."""

    def test_engine_initialization(self):
        """Test engine initializes with built-in tools."""
        engine = WorkflowEngine()

        assert "file_ops" in engine.tools
        assert "code_exec" in engine.tools

    def test_register_tool(self):
        """Test registering custom tools."""
        engine = WorkflowEngine()

        # Create mock tool
        from lmapp.workflows.engine import WorkflowTool

        class MockTool(WorkflowTool):
            @property
            def name(self) -> str:
                return "mock"

            async def execute(self, args, context):
                return "mock_result"

            def validate_args(self, args):
                return True

        engine.register_tool(MockTool())
        assert "mock" in engine.tools

    def test_execute_empty_workflow(self):
        """Test executing empty workflow."""
        engine = WorkflowEngine()
        context = asyncio.run(engine.execute_workflow([]))

        assert len(context.results) == 0
        assert "Workflow started" in context.audit_log
        assert "Workflow completed" in context.audit_log

    def test_execute_simple_step(self, tmp_path):
        """Test executing simple workflow step."""
        engine = WorkflowEngine()

        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        step = WorkflowStep(
            id="step1",
            name="Read file",
            tool="file_ops",
            args={"operation": "read", "path": str(test_file)},
        )

        context = asyncio.run(engine.execute_workflow([step]))

        assert "step1" in context.results
        assert context.results["step1"].status == TaskStatus.SUCCESS

    def test_workflow_with_condition(self):
        """Test workflow with conditional step."""
        engine = WorkflowEngine()
        context = WorkflowContext()
        context.set_var("should_run", True)

        step = WorkflowStep(
            id="step1",
            name="Conditional step",
            tool="code_exec",
            args={"code": "x = 1"},
            condition="${{should_run}}",
        )

        result_context = asyncio.run(engine.execute_workflow([step], context=context))

        # Step should execute (condition is true)
        assert "step1" in result_context.results

    def test_workflow_failure(self):
        """Test workflow step failure."""
        engine = WorkflowEngine()

        step = WorkflowStep(
            id="step1",
            name="Invalid operation",
            tool="file_ops",
            args={"operation": "invalid", "path": "/tmp"},
        )

        context = asyncio.run(engine.execute_workflow([step]))

        assert context.results["step1"].status == TaskStatus.FAILED
        assert context.results["step1"].error is not None


class TestWorkflowSteps:
    """Test workflow step definitions."""

    def test_step_creation(self):
        """Test creating workflow step."""
        step = WorkflowStep(
            id="test_step",
            name="Test",
            tool="file_ops",
            args={"operation": "read", "path": "/tmp/file"},
            retry_count=3,
            timeout_seconds=60,
        )

        assert step.id == "test_step"
        assert step.retry_count == 3
        assert step.timeout_seconds == 60


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
