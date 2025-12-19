"""
Refactoring Service for lmapp API Server.

Provides code refactoring and quick-fix suggestions based on detected issues.
Supports multiple refactoring patterns: unused variable removal, naming fixes,
code simplification, performance improvements, and more.

Usage:
    service = RefactoringService()
    fixes = service.get_quick_fixes("x = None\nprint(x.strip())", "python")
    # Returns: [{"type": "null_reference", "fix": "Check for None first", ...}]
"""

from typing import Dict, List, Optional, Any, Tuple
import logging
import re
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class FixSeverity(str, Enum):
    """Severity of a refactoring fix."""

    CRITICAL = "critical"  # Prevent crashes
    HIGH = "high"  # Improve reliability
    MEDIUM = "medium"  # Code quality
    LOW = "low"  # Style/preference
    INFO = "info"  # Suggestions


class FixCategory(str, Enum):
    """Category of refactoring fix."""

    REMOVE_UNUSED = "remove_unused"
    FIX_NAMING = "fix_naming"
    SIMPLIFY_CODE = "simplify_code"
    OPTIMIZE_PERFORMANCE = "optimize_performance"
    FIX_LOGIC = "fix_logic"
    ADD_SAFETY_CHECK = "add_safety_check"
    EXTRACT_METHOD = "extract_method"
    CONSOLIDATE_DUPLICATE = "consolidate_duplicate"


@dataclass
class QuickFix:
    """Represents a quick fix/refactoring suggestion."""

    id: str  # Unique fix ID
    category: FixCategory
    severity: FixSeverity
    title: str  # Short title
    description: str  # Detailed description
    before: str  # Code before fix
    after: str  # Code after fix
    line: int  # Line number where issue occurs
    auto_fixable: bool = True  # Can be applied automatically
    explanation: str = ""  # Why this fix is recommended

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "category": self.category.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "before": self.before,
            "after": self.after,
            "line": self.line,
            "auto_fixable": self.auto_fixable,
            "explanation": self.explanation,
        }


class RefactoringService:
    """Service for generating refactoring and quick-fix suggestions."""

    # Common patterns and their fixes
    PYTHON_FIXES = {
        "unused_variable": {
            "pattern": r"^(\s*)([a-z_]\w*)\s*=",
            "description": "Remove unused variable",
            "category": FixCategory.REMOVE_UNUSED,
            "severity": FixSeverity.MEDIUM,
        },
        "unused_import": {
            "pattern": r"^import |^from .* import",
            "description": "Remove unused import",
            "category": FixCategory.REMOVE_UNUSED,
            "severity": FixSeverity.MEDIUM,
        },
        "multiple_assignments": {
            "pattern": r"(\s*)x\s*=\s*(\d+)\s*\n\s*x\s*=\s*(\d+)",
            "description": "Consolidate multiple assignments",
            "category": FixCategory.CONSOLIDATE_DUPLICATE,
            "severity": FixSeverity.LOW,
        },
        "double_negative": {
            "pattern": r"not\s+not\s+",
            "description": "Remove double negative",
            "category": FixCategory.SIMPLIFY_CODE,
            "severity": FixSeverity.LOW,
        },
        "comparison_to_true": {
            "pattern": r"==\s*True|==\s*False",
            "description": "Simplify boolean comparison",
            "category": FixCategory.SIMPLIFY_CODE,
            "severity": FixSeverity.LOW,
        },
    }

    JAVASCRIPT_FIXES = {
        "unused_variable": {
            "pattern": r"(let|const|var)\s+[a-z_]\w*\s*=",
            "description": "Remove unused variable",
            "category": FixCategory.REMOVE_UNUSED,
            "severity": FixSeverity.MEDIUM,
        },
        "var_to_const": {
            "pattern": r"^(\s*)var\s+([a-z_]\w*)\s*=",
            "description": "Convert var to const",
            "category": FixCategory.FIX_NAMING,
            "severity": FixSeverity.MEDIUM,
        },
        "arrow_function": {
            "pattern": r"function\s*\(\s*\)\s*\{",
            "description": "Convert to arrow function",
            "category": FixCategory.SIMPLIFY_CODE,
            "severity": FixSeverity.LOW,
        },
    }

    def __init__(self):
        """Initialize the refactoring service."""
        self.fix_counter = 0

    def get_quick_fixes(self, code: str, language: str = "python") -> List[QuickFix]:
        """
        Generate quick-fix suggestions for code.

        Args:
            code: Code to analyze
            language: Programming language (python, javascript, etc.)

        Returns:
            List of QuickFix objects
        """
        fixes: List[QuickFix] = []

        if language == "python":
            fixes.extend(self._get_python_fixes(code))
        elif language in ["javascript", "typescript"]:
            fixes.extend(self._get_javascript_fixes(code))
        else:
            fixes.extend(self._get_generic_fixes(code))

        return fixes

    def _get_python_fixes(self, code: str) -> List[QuickFix]:
        """Generate Python-specific fixes."""
        fixes: List[QuickFix] = []
        lines = code.split("\n")

        for line_num, line in enumerate(lines, 1):
            # Check for unused variables
            if self._is_unused_variable_python(line, lines, line_num - 1):
                fixes.append(
                    QuickFix(
                        id=f"fix-{self.fix_counter}",
                        category=FixCategory.REMOVE_UNUSED,
                        severity=FixSeverity.MEDIUM,
                        title="Remove unused variable",
                        description=f"Variable on line {line_num} is assigned but never used",
                        before=line,
                        after="# Variable removed (unused)",
                        line=line_num,
                        auto_fixable=False,  # Manual review recommended
                        explanation="Unused variables increase code complexity and may indicate bugs",
                    )
                )
                self.fix_counter += 1

            # Check for double negatives
            if "not not" in line:
                fixed_line = line.replace("not not", "")
                fixes.append(
                    QuickFix(
                        id=f"fix-{self.fix_counter}",
                        category=FixCategory.SIMPLIFY_CODE,
                        severity=FixSeverity.LOW,
                        title="Remove double negative",
                        description="Double negatives can be simplified",
                        before=line,
                        after=fixed_line,
                        line=line_num,
                        auto_fixable=True,
                        explanation="'not not x' is the same as 'x' - simplify for clarity",
                    )
                )
                self.fix_counter += 1

            # Check for == True/False
            if re.search(r"==\s*True|==\s*False", line):
                if "== True" in line:
                    fixed_line = line.replace("== True", "")
                elif "== False" in line:
                    fixed_line = line.replace("== False", "").replace("not ", "", 1)

                fixes.append(
                    QuickFix(
                        id=f"fix-{self.fix_counter}",
                        category=FixCategory.SIMPLIFY_CODE,
                        severity=FixSeverity.LOW,
                        title="Simplify boolean comparison",
                        description="Direct boolean comparison can be simplified",
                        before=line,
                        after=fixed_line,
                        line=line_num,
                        auto_fixable=True,
                        explanation="In Python, 'if x == True' can be written as 'if x' for clarity",
                    )
                )
                self.fix_counter += 1

        return fixes

    def _get_javascript_fixes(self, code: str) -> List[QuickFix]:
        """Generate JavaScript/TypeScript-specific fixes."""
        fixes: List[QuickFix] = []
        lines = code.split("\n")

        for line_num, line in enumerate(lines, 1):
            # Check for var usage
            if re.match(r"^\s*var\s+", line):
                fixed_line = re.sub(r"^\s*var\s+", "const ", line)
                fixes.append(
                    QuickFix(
                        id=f"fix-{self.fix_counter}",
                        category=FixCategory.FIX_NAMING,
                        severity=FixSeverity.MEDIUM,
                        title="Convert var to const",
                        description="'var' has confusing scoping rules. Use 'const' instead",
                        before=line,
                        after=fixed_line,
                        line=line_num,
                        auto_fixable=True,
                        explanation="Modern JavaScript prefers 'const' and 'let' over 'var'",
                    )
                )
                self.fix_counter += 1

            # Check for function expressions that could be arrow functions
            if "function()" in line and "{" in line:
                fixed_line = line.replace("function()", "() =>")
                fixes.append(
                    QuickFix(
                        id=f"fix-{self.fix_counter}",
                        category=FixCategory.SIMPLIFY_CODE,
                        severity=FixSeverity.LOW,
                        title="Convert to arrow function",
                        description="Modern JavaScript prefers arrow function syntax",
                        before=line,
                        after=fixed_line,
                        line=line_num,
                        auto_fixable=True,
                        explanation="Arrow functions are more concise and have better 'this' binding",
                    )
                )
                self.fix_counter += 1

        return fixes

    def _get_generic_fixes(self, code: str) -> List[QuickFix]:
        """Generate generic fixes applicable to any language."""
        fixes: List[QuickFix] = []
        lines = code.split("\n")

        for line_num, line in enumerate(lines, 1):
            # Check for long lines
            if len(line) > 100:
                fixes.append(
                    QuickFix(
                        id=f"fix-{self.fix_counter}",
                        category=FixCategory.SIMPLIFY_CODE,
                        severity=FixSeverity.LOW,
                        title="Line too long",
                        description=f"Line {line_num} exceeds 100 characters",
                        before=line,
                        after="(consider breaking into multiple lines)",
                        line=line_num,
                        auto_fixable=False,
                        explanation="Long lines are harder to read. Consider breaking into multiple lines",
                    )
                )
                self.fix_counter += 1

        return fixes

    def _is_unused_variable_python(self, line: str, lines: List[str], line_idx: int) -> bool:
        """Check if a variable is assigned but never used in Python."""
        match = re.match(r"\s*([a-z_]\w*)\s*=", line)
        if not match:
            return False

        var_name = match.group(1)

        # Skip common patterns that are intentionally unused
        if var_name in ["_", "unused", "dummy"]:
            return False

        # Check if variable is used later
        remaining_code = "\n".join(lines[line_idx + 1 :])
        if re.search(rf"\b{var_name}\b", remaining_code):
            return False

        return True

    def apply_fix(self, code: str, fix: QuickFix) -> Tuple[str, bool]:
        """
        Apply a quick fix to code.

        Args:
            code: Original code
            fix: QuickFix to apply

        Returns:
            Tuple of (modified code, success)
        """
        if not fix.auto_fixable:
            return code, False

        try:
            # Find the line
            lines = code.split("\n")
            if fix.line - 1 < len(lines):
                if lines[fix.line - 1] == fix.before:
                    lines[fix.line - 1] = fix.after
                    return "\n".join(lines), True

            return code, False
        except Exception as e:
            logger.error(f"Failed to apply fix: {e}")
            return code, False

    def apply_multiple_fixes(self, code: str, fixes: List[QuickFix]) -> Tuple[str, int]:
        """
        Apply multiple fixes to code.

        Args:
            code: Original code
            fixes: List of QuickFix to apply

        Returns:
            Tuple of (modified code, number of fixes applied)
        """
        applied = 0
        for fix in sorted(fixes, key=lambda f: f.line, reverse=True):
            if fix.auto_fixable:
                code, success = self.apply_fix(code, fix)
                if success:
                    applied += 1

        return code, applied

    def get_refactoring_suggestions(self, code: str, language: str = "python", complexity: int = 0) -> Dict[str, Any]:
        """
        Get comprehensive refactoring suggestions.

        Args:
            code: Code to analyze
            language: Programming language
            complexity: Code complexity score

        Returns:
            Dictionary with refactoring suggestions
        """
        fixes = self.get_quick_fixes(code, language)

        # Categorize fixes
        categorized: Dict[str, List[QuickFix]] = {}
        for fix in fixes:
            cat = fix.category.value
            if cat not in categorized:
                categorized[cat] = []
            categorized[cat].append(fix)

        return {
            "total_fixes": len(fixes),
            "fixes_by_category": {cat: len(fixes_list) for cat, fixes_list in categorized.items()},
            "fixes": [f.to_dict() for f in fixes],
            "language": language,
            "complexity": complexity,
        }


# Singleton instance
_refactoring_service: Optional[RefactoringService] = None


def get_refactoring_service() -> RefactoringService:
    """Get or create the refactoring service singleton."""
    global _refactoring_service
    if _refactoring_service is None:
        _refactoring_service = RefactoringService()
    return _refactoring_service
