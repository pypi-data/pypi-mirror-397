"""Safety guardrails and audit logging for workflows."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class RiskLevel(Enum):
    """Risk level for operations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SafetyRule:
    """Rule for safety validation."""

    name: str
    description: str
    risk_level: RiskLevel
    check_fn: callable


class SafetyGuardrail:
    """Enforces safety rules for workflows."""

    def __init__(self):
        """Initialize guardrail."""
        self.rules: List[SafetyRule] = []
        self._violations = []
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        """Register default safety rules."""
        # File system access rules
        self.add_rule(
            SafetyRule(
                name="no_system_paths",
                description="Prevent access to system paths",
                risk_level=RiskLevel.HIGH,
                check_fn=self._check_no_system_paths,
            )
        )

        # Code execution rules
        self.add_rule(
            SafetyRule(
                name="no_dangerous_imports",
                description="Prevent dangerous module imports",
                risk_level=RiskLevel.CRITICAL,
                check_fn=self._check_no_dangerous_imports,
            )
        )

        self.add_rule(
            SafetyRule(
                name="no_shell_execution",
                description="Prevent shell command execution",
                risk_level=RiskLevel.CRITICAL,
                check_fn=self._check_no_shell_execution,
            )
        )

    def add_rule(self, rule: SafetyRule) -> None:
        """Add safety rule.

        Args:
            rule: Rule to add
        """
        self.rules.append(rule)

    def validate_operation(self, tool: str, args: dict) -> bool:
        """Validate operation against safety rules.

        Args:
            tool: Tool name
            args: Tool arguments

        Returns:
            True if operation is safe
        """
        self._violations.clear()

        for rule in self.rules:
            try:
                if not rule.check_fn(tool, args):
                    self._violations.append(
                        {
                            "rule": rule.name,
                            "risk_level": rule.risk_level.value,
                            "description": rule.description,
                        }
                    )

                    # Fail fast on critical violations
                    if rule.risk_level == RiskLevel.CRITICAL:
                        return False
            except Exception as e:
                print(f"Error checking rule {rule.name}: {e}")

        return len(self._violations) == 0

    def get_violations(self) -> List[dict]:
        """Get list of safety violations.

        Returns:
            List of violation dicts
        """
        return self._violations

    def _check_no_system_paths(self, tool: str, args: dict) -> bool:
        """Check for system path access."""
        if tool != "file_ops":
            return True

        path = args.get("path", "").lower()
        dangerous_paths = ["/etc", "/sys", "/proc", "/dev", "/root", "/boot"]

        for danger_path in dangerous_paths:
            if path.startswith(danger_path):
                return False

        return True

    def _check_no_dangerous_imports(self, tool: str, args: dict) -> bool:
        """Check for dangerous imports."""
        if tool != "code_exec":
            return True

        code = args.get("code", "")
        dangerous_imports = [
            "os.system",
            "subprocess",
            "eval",
            "exec",
            "__import__",
        ]

        for danger in dangerous_imports:
            if danger in code:
                return False

        return True

    def _check_no_shell_execution(self, tool: str, args: dict) -> bool:
        """Check for shell execution."""
        if tool != "code_exec":
            return True

        code = args.get("code", "")
        shell_keywords = ["bash", "sh -c", "system(", "popen("]

        for keyword in shell_keywords:
            if keyword in code:
                return False

        return True


class AuditLogger:
    """Logs workflow operations for audit."""

    def __init__(self):
        """Initialize audit logger."""
        self.events: List[dict] = []

    def log_event(
        self,
        event_type: str,
        tool: str,
        action: str,
        status: str,
        details: Optional[dict] = None,
    ) -> None:
        """Log audit event.

        Args:
            event_type: Type of event
            tool: Tool involved
            action: Action performed
            status: Status (success/failure)
            details: Additional details
        """
        from datetime import datetime, timezone

        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "tool": tool,
            "action": action,
            "status": status,
            "details": details or {},
        }
        self.events.append(event)

    def log_access(self, resource: str, operation: str, status: str) -> None:
        """Log resource access.

        Args:
            resource: Resource accessed
            operation: Operation performed
            status: Success/failure
        """
        self.log_event(event_type="access", tool="file_ops", action=operation, status=status)

    def log_code_execution(self, status: str, error: Optional[str] = None) -> None:
        """Log code execution.

        Args:
            status: Execution status
            error: Optional error message
        """
        self.log_event(
            event_type="code_execution",
            tool="code_exec",
            action="execute",
            status=status,
            details={"error": error} if error else None,
        )

    def get_audit_trail(self) -> List[dict]:
        """Get complete audit trail.

        Returns:
            List of audit events
        """
        return self.events

    def clear_audit_trail(self) -> None:
        """Clear audit trail."""
        self.events.clear()
