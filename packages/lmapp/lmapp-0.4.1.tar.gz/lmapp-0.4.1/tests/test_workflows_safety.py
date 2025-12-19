"""Unit tests for workflow safety and audit."""

import pytest

from lmapp.workflows.safety import AuditLogger, RiskLevel, SafetyGuardrail, SafetyRule


class TestSafetyGuardrail:
    """Test safety guardrail enforcement."""

    def test_guardrail_initialization(self):
        """Test guardrail initializes with default rules."""
        guardrail = SafetyGuardrail()

        assert len(guardrail.rules) > 0
        rule_names = [r.name for r in guardrail.rules]
        assert "no_system_paths" in rule_names

    def test_add_custom_rule(self):
        """Test adding custom safety rule."""
        guardrail = SafetyGuardrail()
        initial_count = len(guardrail.rules)

        def custom_check(tool, args):
            return True

        rule = SafetyRule(
            name="custom_rule",
            description="Custom test rule",
            risk_level=RiskLevel.MEDIUM,
            check_fn=custom_check,
        )
        guardrail.add_rule(rule)

        assert len(guardrail.rules) == initial_count + 1

    def test_validate_safe_operation(self):
        """Test validation of safe operation."""
        guardrail = SafetyGuardrail()

        result = guardrail.validate_operation(
            tool="file_ops",
            args={"operation": "read", "path": "/tmp/file.txt"},
        )

        assert result is True
        assert len(guardrail.get_violations()) == 0

    def test_validate_system_path_violation(self):
        """Test detection of system path access."""
        guardrail = SafetyGuardrail()

        result = guardrail.validate_operation(
            tool="file_ops",
            args={"operation": "read", "path": "/etc/passwd"},
        )

        assert result is False
        violations = guardrail.get_violations()
        assert any(v["rule"] == "no_system_paths" for v in violations)

    def test_validate_dangerous_imports(self):
        """Test detection of dangerous imports."""
        guardrail = SafetyGuardrail()

        result = guardrail.validate_operation(
            tool="code_exec",
            args={"code": "import subprocess; subprocess.call('ls')"},
        )

        assert result is False
        violations = guardrail.get_violations()
        assert len(violations) > 0

    def test_validate_shell_execution(self):
        """Test detection of shell execution."""
        guardrail = SafetyGuardrail()

        result = guardrail.validate_operation(
            tool="code_exec",
            args={"code": "os.system('rm -rf /')"},
        )

        assert result is False

    def test_critical_violation_stops_immediately(self):
        """Test critical violations stop validation immediately."""
        guardrail = SafetyGuardrail()

        # This should trigger critical violation
        result = guardrail.validate_operation(
            tool="code_exec",
            args={"code": "exec('malicious code')"},
        )

        assert result is False


class TestAuditLogger:
    """Test audit logging."""

    def test_logger_initialization(self):
        """Test logger initializes."""
        logger = AuditLogger()

        assert len(logger.get_audit_trail()) == 0

    def test_log_event(self):
        """Test logging events."""
        logger = AuditLogger()

        logger.log_event(
            event_type="access",
            tool="file_ops",
            action="read",
            status="success",
        )

        trail = logger.get_audit_trail()
        assert len(trail) == 1
        assert trail[0]["event_type"] == "access"
        assert trail[0]["action"] == "read"

    def test_log_access(self):
        """Test logging file access."""
        logger = AuditLogger()

        logger.log_access(resource="/tmp/file", operation="read", status="success")

        trail = logger.get_audit_trail()
        assert len(trail) == 1
        assert trail[0]["event_type"] == "access"

    def test_log_code_execution(self):
        """Test logging code execution."""
        logger = AuditLogger()

        logger.log_code_execution(status="success")
        logger.log_code_execution(status="failure", error="Division by zero")

        trail = logger.get_audit_trail()
        assert len(trail) == 2
        assert trail[0]["status"] == "success"
        assert trail[1]["status"] == "failure"
        assert "Division by zero" in str(trail[1]["details"])

    def test_clear_audit_trail(self):
        """Test clearing audit trail."""
        logger = AuditLogger()

        logger.log_event("test", "tool", "action", "success")
        assert len(logger.get_audit_trail()) > 0

        logger.clear_audit_trail()
        assert len(logger.get_audit_trail()) == 0

    def test_audit_trail_timestamps(self):
        """Test that events have timestamps."""
        logger = AuditLogger()

        logger.log_event("test", "tool", "action", "success")

        trail = logger.get_audit_trail()
        assert "timestamp" in trail[0]


class TestRiskLevels:
    """Test risk level enumeration."""

    def test_risk_level_values(self):
        """Test risk level values."""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
