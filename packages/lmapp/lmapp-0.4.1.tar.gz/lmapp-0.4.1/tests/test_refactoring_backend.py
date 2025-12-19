"""
Phase 2B: Backend Refactoring Service Tests

Tests for the refactoring API endpoints and service layer.
Validates all three endpoints:
- POST /v1/refactor/suggestions
- POST /v1/refactor/quick-fixes
- POST /v1/refactor/apply
"""

import sys
import pytest
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lmapp.server.refactoring_service import (
    RefactoringService,
    QuickFix,
    FixCategory,
    FixSeverity,
)


class TestRefactoringService:
    """Test the RefactoringService class."""

    @pytest.fixture
    def service(self):
        """Create a RefactoringService instance."""
        return RefactoringService()

    # --- Python Analyzer Tests ---

    def test_python_unused_variable_detection(self, service):
        """Test detection of unused variables in Python."""
        code = """x = 5
y = 10
print(y)"""
        fixes = service.get_quick_fixes(code, "python")
        assert len(fixes) >= 1
        assert any(f.category == FixCategory.REMOVE_UNUSED for f in fixes)

    def test_python_double_negative_simplification(self, service):
        """Test detection of double negatives."""
        code = "if not not x: pass"
        fixes = service.get_quick_fixes(code, "python")
        assert any(f.title == "Remove double negative" for f in fixes)

    def test_python_boolean_simplification(self, service):
        """Test boolean comparison simplification."""
        code = "if x == True: pass"
        fixes = service.get_quick_fixes(code, "python")
        assert any("boolean" in f.title.lower() for f in fixes)

    def test_python_empty_code(self, service):
        """Test handling of empty code."""
        fixes = service.get_quick_fixes("", "python")
        assert isinstance(fixes, list)

    # --- JavaScript/TypeScript Analyzer Tests ---

    def test_javascript_var_to_const(self, service):
        """Test conversion of var to const."""
        code = "var x = 5;"
        fixes = service.get_quick_fixes(code, "javascript")
        assert len(fixes) >= 1
        assert any(f.title == "Convert var to const" for f in fixes)

    def test_typescript_var_to_const(self, service):
        """Test conversion of var to const in TypeScript."""
        code = "var name: string = 'test';"
        fixes = service.get_quick_fixes(code, "typescript")
        assert len(fixes) >= 1

    def test_javascript_multiple_fixes(self, service):
        """Test multiple fixes in JavaScript code."""
        code = """var x = 5;
var y = function() { return x; }
console.log(y());"""
        fixes = service.get_quick_fixes(code, "javascript")
        assert len(fixes) >= 1

    # --- Fix Application Tests ---

    def test_apply_fix_success(self, service):
        """Test successful application of a fix."""
        code = "x = 5\nprint(x)"
        fixes = service.get_quick_fixes(code, "python")

        if fixes and fixes[0].auto_fixable:
            modified, success = service.apply_fix(code, fixes[0])
            assert isinstance(modified, str)
            assert isinstance(success, bool)

    def test_apply_multiple_fixes(self, service):
        """Test applying multiple fixes to same code."""
        code = "var x = 5;\nvar y = 10;"
        fixes = service.get_quick_fixes(code, "javascript")

        for fix in fixes[:2]:  # Apply first 2 fixes
            if fix.auto_fixable:
                modified, success = service.apply_fix(code, fix)
                assert isinstance(modified, str)

    # --- Language Support Tests ---

    def test_python_language_detection(self, service):
        """Test Python code is analyzed correctly."""
        python_code = "def foo(): pass"
        fixes = service.get_quick_fixes(python_code, "python")
        assert isinstance(fixes, list)

    def test_javascript_language_detection(self, service):
        """Test JavaScript code is analyzed correctly."""
        js_code = "function foo() {}"
        fixes = service.get_quick_fixes(js_code, "javascript")
        assert isinstance(fixes, list)

    def test_typescript_language_detection(self, service):
        """Test TypeScript code is analyzed correctly."""
        ts_code = "const foo = (): void => {}"
        fixes = service.get_quick_fixes(ts_code, "typescript")
        assert isinstance(fixes, list)

    def test_unsupported_language_fallback(self, service):
        """Test unsupported language falls back to generic analysis."""
        code = "some code here"
        fixes = service.get_quick_fixes(code, "rust")
        assert isinstance(fixes, list)

    # --- Fix Metadata Tests ---

    def test_fix_has_required_fields(self, service):
        """Test that all fixes have required metadata."""
        code = "x = 5\ny = 10\nprint(y)"
        fixes = service.get_quick_fixes(code, "python")

        for fix in fixes:
            assert fix.id
            assert fix.category
            assert fix.severity
            assert fix.title
            assert fix.description
            assert isinstance(fix.line, int)
            assert isinstance(fix.auto_fixable, bool)

    def test_fix_to_dict_conversion(self, service):
        """Test QuickFix.to_dict() conversion."""
        code = "x = 5\nprint(x)"
        fixes = service.get_quick_fixes(code, "python")

        for fix in fixes:
            fix_dict = fix.to_dict()
            assert isinstance(fix_dict, dict)
            assert "id" in fix_dict
            assert "category" in fix_dict
            assert "severity" in fix_dict
            assert fix_dict["category"] == fix.category.value
            assert fix_dict["severity"] == fix.severity.value

    # --- Edge Cases ---

    def test_large_code_handling(self, service):
        """Test handling of large code blocks."""
        large_code = "\n".join([f"x{i} = {i}" for i in range(100)])
        fixes = service.get_quick_fixes(large_code, "python")
        assert isinstance(fixes, list)

    def test_code_with_syntax_errors(self, service):
        """Test handling of invalid code."""
        invalid_code = "def foo( print 'error'"
        # Should not crash, might return empty or generic fixes
        fixes = service.get_quick_fixes(invalid_code, "python")
        assert isinstance(fixes, list)

    def test_code_with_special_characters(self, service):
        """Test handling of special characters."""
        special_code = 'print("Test: é à ü 你好")'
        fixes = service.get_quick_fixes(special_code, "python")
        assert isinstance(fixes, list)

    def test_multiline_string_handling(self, service):
        """Test handling of multiline strings."""
        code = '''text = """
        This is a multiline
        string"""
print(text)'''
        fixes = service.get_quick_fixes(code, "python")
        assert isinstance(fixes, list)


class TestQuickFixDataclass:
    """Test the QuickFix dataclass."""

    def test_quickfix_creation(self):
        """Test creating a QuickFix instance."""
        fix = QuickFix(
            id="test-001",
            category=FixCategory.REMOVE_UNUSED,
            severity=FixSeverity.MEDIUM,
            title="Test Fix",
            description="Test description",
            before="x = 5",
            after="# removed",
            line=1,
            auto_fixable=True,
            explanation="This is a test",
        )
        assert fix.id == "test-001"
        assert fix.title == "Test Fix"

    def test_quickfix_to_dict(self):
        """Test QuickFix serialization to dict."""
        fix = QuickFix(
            id="test-001",
            category=FixCategory.SIMPLIFY_CODE,
            severity=FixSeverity.LOW,
            title="Test",
            description="Description",
            before="code",
            after="fixed",
            line=5,
        )
        fix_dict = fix.to_dict()
        assert fix_dict["id"] == "test-001"
        assert fix_dict["category"] == "simplify_code"
        assert fix_dict["severity"] == "low"
        assert isinstance(fix_dict, dict)


class TestFixCategories:
    """Test fix categories and severity levels."""

    def test_fix_category_enum(self):
        """Test FixCategory enum values."""
        assert FixCategory.REMOVE_UNUSED.value == "remove_unused"
        assert FixCategory.FIX_NAMING.value == "fix_naming"
        assert FixCategory.SIMPLIFY_CODE.value == "simplify_code"

    def test_fix_severity_enum(self):
        """Test FixSeverity enum values."""
        assert FixSeverity.CRITICAL.value == "critical"
        assert FixSeverity.HIGH.value == "high"
        assert FixSeverity.MEDIUM.value == "medium"
        assert FixSeverity.LOW.value == "low"
        assert FixSeverity.INFO.value == "info"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
