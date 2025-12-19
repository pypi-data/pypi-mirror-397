"""
Code Analysis Service for lmapp API Server.

Provides integration between the CodeAnalyzerPlugin and the FastAPI server.
Handles real-time code analysis for completions with caching and error handling.

Usage:
    service = CodeAnalysisService()
    result = service.analyze_context("def foo():\\n  x = None", "python")
    # Returns: {"language": "python", "issues": [...], "summary": {...}}
"""

from typing import Dict, List, Optional, Any
import logging
from functools import lru_cache
import hashlib

try:
    from lmapp.plugins.example_code_analyzer import (
        CodeAnalyzerPlugin,
        CodeIssue,
        AnalysisResult,
    )
except ImportError:
    CodeAnalyzerPlugin = None
    CodeIssue = None
    AnalysisResult = None


logger = logging.getLogger(__name__)


class CodeAnalysisService:
    """Service for analyzing code and providing issue suggestions."""

    # Supported languages and their configurations
    LANGUAGE_CONFIG = {
        "python": {"strict": True, "detect_type_issues": True},
        "javascript": {"strict": True, "detect_type_issues": False},
        "typescript": {"strict": True, "detect_type_issues": True},
        "java": {"strict": True, "detect_type_issues": True},
        "cpp": {"strict": True, "detect_type_issues": True},
        "c": {"strict": False, "detect_type_issues": False},
        "generic": {"strict": False, "detect_type_issues": False},
    }

    def __init__(self, cache_size: int = 128):
        """
        Initialize the Code Analysis Service.

        Args:
            cache_size: Maximum number of cached analyses
        """
        self.cache_size = cache_size
        self.analyzers: Dict[str, CodeAnalyzerPlugin] = {}
        self._analysis_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_hits = 0
        self._cache_misses = 0

        # Try to initialize analyzers
        if CodeAnalyzerPlugin:
            self._initialize_analyzers()
        else:
            logger.warning("CodeAnalyzerPlugin not available")

    def _initialize_analyzers(self) -> None:
        """Initialize analyzer instances for supported languages."""
        for language, config in self.LANGUAGE_CONFIG.items():
            try:
                analyzer = CodeAnalyzerPlugin()
                analyzer.initialize({"language": language, **config})
                self.analyzers[language] = analyzer
                logger.info(f"Initialized analyzer for {language}")
            except Exception as e:
                logger.error(f"Failed to initialize analyzer for {language}: {e}")

    def _get_cache_key(self, code: str, language: str) -> str:
        """Generate cache key for code analysis."""
        content = f"{language}:{code}".encode()
        return hashlib.md5(content).hexdigest()

    def analyze_context(self, code: str, language: str = "python", use_cache: bool = True) -> Dict[str, Any]:
        """
        Analyze code context for issues.

        Args:
            code: Code to analyze
            language: Programming language (python, javascript, java, cpp, etc.)
            use_cache: Whether to use cached results

        Returns:
            Dictionary with analysis results containing:
                - language: str
                - issues: List[Dict] - detected issues
                - summary: Dict - aggregated metrics
                - complexity: int - estimated cyclomatic complexity
                - cache_hit: bool - whether result was cached
        """
        # Validate language
        if language not in self.LANGUAGE_CONFIG:
            language = "generic"
            logger.debug(f"Unknown language, falling back to generic analyzer")

        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(code, language)
            if cache_key in self._analysis_cache:
                self._cache_hits += 1
                result = self._analysis_cache[cache_key]
                result["cache_hit"] = True
                return result

            self._cache_misses += 1

        # Get analyzer
        analyzer = self.analyzers.get(language)
        if not analyzer:
            logger.warning(f"No analyzer for language: {language}")
            return self._empty_analysis(language)

        try:
            # Run analysis
            result = analyzer.execute(code)

            # Handle both dict and object responses
            if isinstance(result, dict):
                # Already a dictionary from execute()
                analysis_result = {
                    "language": language,
                    "issues": result.get("issues", []),
                    "summary": result.get("summary", {}),
                    "complexity": result.get("complexity", 0),
                    "lines_analyzed": result.get("lines_analyzed", 0),
                    "cache_hit": False,
                }
            else:
                # Format response from AnalysisResult object
                analysis_result = {
                    "language": language,
                    "issues": [self._issue_to_dict(issue) for issue in result.issues],
                    "summary": result.summary,
                    "complexity": result.complexity_estimate,
                    "lines_analyzed": result.lines_analyzed,
                    "cache_hit": False,
                }

            # Cache result (with size limit)
            if use_cache:
                if len(self._analysis_cache) >= self.cache_size:
                    # Remove oldest (simple FIFO)
                    self._analysis_cache.pop(next(iter(self._analysis_cache)))

                cache_key = self._get_cache_key(code, language)
                self._analysis_cache[cache_key] = analysis_result

            return analysis_result

        except Exception as e:
            logger.error(f"Analysis failed for {language}: {e}")
            return self._error_analysis(language, str(e))

    def analyze_with_suggestions(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Analyze code and generate AI suggestions for fixes.

        Args:
            code: Code to analyze
            language: Programming language

        Returns:
            Analysis result with suggested fixes
        """
        analysis = self.analyze_context(code, language)

        # Add suggestions for critical issues
        if analysis.get("issues"):
            for issue in analysis["issues"]:
                if issue["severity"] in ["critical", "high"]:
                    issue["suggested_fix"] = self._generate_suggestion(issue, code, language)

        return analysis

    def _generate_suggestion(self, issue: Dict[str, Any], code: str, language: str) -> Optional[str]:
        """Generate a suggestion for fixing an issue."""
        suggestions = {
            "null_reference": "Check for null/None before accessing attributes",
            "type_mismatch": "Ensure variable types match expected values",
            "undefined_variable": "Declare variable before use",
            "unused_variable": "Remove unused variables to improve code clarity",
            "import_unused": "Remove unused imports",
        }

        issue_key = issue.get("type", "").lower()
        return suggestions.get(issue_key)

    def get_complexity_rating(self, complexity: int) -> str:
        """Get human-readable complexity rating."""
        if complexity < 5:
            return "Low"
        elif complexity < 10:
            return "Medium"
        elif complexity < 15:
            return "High"
        else:
            return "Very High"

    def get_severity_color(self, severity: str) -> str:
        """Map severity level to VS Code decoration color."""
        colors = {
            "critical": "#FF6B6B",  # Red
            "high": "#FFA500",  # Orange
            "medium": "#FFD700",  # Gold
            "low": "#87CEEB",  # Sky Blue
            "info": "#90EE90",  # Light Green
        }
        return colors.get(severity, "#CCCCCC")  # Default gray

    def get_severity_icon(self, severity: str) -> str:
        """Get emoji icon for severity level."""
        icons = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🔵",
            "info": "🟢",
        }
        return icons.get(severity, "⚪")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        total = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total * 100) if total > 0 else 0

        return {
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate_percent": hit_rate,
            "cached_items": len(self._analysis_cache),
            "max_cache_size": self.cache_size,
        }

    def clear_cache(self) -> None:
        """Clear the analysis cache."""
        self._analysis_cache.clear()
        logger.info("Analysis cache cleared")

    def _issue_to_dict(self, issue: Any) -> Dict[str, Any]:
        """Convert CodeIssue to dictionary."""
        try:
            return issue.to_dict()
        except AttributeError:
            # Fallback if to_dict() not available
            return {
                "severity": getattr(issue, "severity", "info"),
                "type": getattr(issue, "issue_type", "unknown"),
                "message": getattr(issue, "message", "Unknown issue"),
                "line": getattr(issue, "line", 0),
                "column": getattr(issue, "column", 0),
                "suggestion": getattr(issue, "suggestion", None),
            }

    def _empty_analysis(self, language: str) -> Dict[str, Any]:
        """Return empty analysis result."""
        return {
            "language": language,
            "issues": [],
            "summary": {
                "total_issues": 0,
                "by_severity": {
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                    "info": 0,
                },
                "by_type": {},
                "complexity_estimate": 0,
                "pass": True,
            },
            "complexity": 0,
            "lines_analyzed": 0,
            "cache_hit": False,
        }

    def _error_analysis(self, language: str, error: str) -> Dict[str, Any]:
        """Return error analysis result."""
        return {
            "language": language,
            "error": error,
            "issues": [],
            "summary": {"total_issues": 0, "pass": False},
            "complexity": 0,
            "cache_hit": False,
        }


# Singleton instance
_analysis_service: Optional[CodeAnalysisService] = None


def get_analysis_service() -> CodeAnalysisService:
    """Get or create the analysis service singleton."""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = CodeAnalysisService()
    return _analysis_service
