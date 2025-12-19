"""
Performance Benchmarking for lmapp Refactoring Service
Phase 2C: Performance Metrics & Optimization

Benchmarks:
- Analysis speed for various code sizes
- Memory usage patterns
- API response times
- Suggestion generation performance
"""

import sys
import time
import json
from pathlib import Path
from statistics import mean, stdev

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lmapp.server.refactoring_service import RefactoringService


class PerformanceBenchmark:
    """Performance benchmarking suite"""

    def __init__(self):
        self.service = RefactoringService()
        self.results = {}

    def benchmark_operation(self, name, operation, iterations=5):
        """Run operation and measure performance"""
        times = []

        for _ in range(iterations):
            start = time.perf_counter()
            result = operation()
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        avg_time = mean(times)
        max_time = max(times)
        min_time = min(times)
        std = stdev(times) if len(times) > 1 else 0

        self.results[name] = {
            "avg_ms": avg_time * 1000,
            "min_ms": min_time * 1000,
            "max_ms": max_time * 1000,
            "stdev_ms": std * 1000,
        }

        return avg_time

    def generate_python_code(self, size):
        """Generate Python code of specified size"""
        lines = []
        for i in range(size):
            lines.append(f"x{i} = {i}")
        lines.append("print(x0)")
        return "\n".join(lines)

    def generate_javascript_code(self, size):
        """Generate JavaScript code of specified size"""
        lines = []
        for i in range(size):
            lines.append(f"var x{i} = {i};")
        lines.append("console.log(x0);")
        return "\n".join(lines)

    # ========================================================================
    # CODE SIZE BENCHMARKS
    # ========================================================================

    def benchmark_small_python(self):
        """Benchmark: Small Python file (10 lines)"""
        code = self.generate_python_code(10)

        time_ms = self.benchmark_operation("Small Python (10 lines)", lambda: self.service.get_quick_fixes(code, "python"))

        assert time_ms < 0.05, f"Should be <50ms, took {time_ms*1000:.1f}ms"
        print(f"✅ Small Python: {time_ms*1000:.2f}ms avg")

    def benchmark_medium_python(self):
        """Benchmark: Medium Python file (100 lines)"""
        code = self.generate_python_code(100)

        time_ms = self.benchmark_operation("Medium Python (100 lines)", lambda: self.service.get_quick_fixes(code, "python"))

        assert time_ms < 0.1, f"Should be <100ms, took {time_ms*1000:.1f}ms"
        print(f"✅ Medium Python: {time_ms*1000:.2f}ms avg")

    def benchmark_large_python(self):
        """Benchmark: Large Python file (500 lines)"""
        code = self.generate_python_code(500)

        time_ms = self.benchmark_operation("Large Python (500 lines)", lambda: self.service.get_quick_fixes(code, "python"))

        assert time_ms < 0.5, f"Should be <500ms, took {time_ms*1000:.1f}ms"
        print(f"✅ Large Python: {time_ms*1000:.2f}ms avg")

    def benchmark_small_javascript(self):
        """Benchmark: Small JavaScript file (10 lines)"""
        code = self.generate_javascript_code(10)

        time_ms = self.benchmark_operation("Small JavaScript (10 lines)", lambda: self.service.get_quick_fixes(code, "javascript"))

        assert time_ms < 0.05, f"Should be <50ms, took {time_ms*1000:.1f}ms"
        print(f"✅ Small JavaScript: {time_ms*1000:.2f}ms avg")

    def benchmark_medium_javascript(self):
        """Benchmark: Medium JavaScript file (100 lines)"""
        code = self.generate_javascript_code(100)

        time_ms = self.benchmark_operation("Medium JavaScript (100 lines)", lambda: self.service.get_quick_fixes(code, "javascript"))

        assert time_ms < 0.1, f"Should be <100ms, took {time_ms*1000:.1f}ms"
        print(f"✅ Medium JavaScript: {time_ms*1000:.2f}ms avg")

    def benchmark_large_javascript(self):
        """Benchmark: Large JavaScript file (500 lines)"""
        code = self.generate_javascript_code(500)

        time_ms = self.benchmark_operation("Large JavaScript (500 lines)", lambda: self.service.get_quick_fixes(code, "javascript"))

        assert time_ms < 0.5, f"Should be <500ms, took {time_ms*1000:.1f}ms"
        print(f"✅ Large JavaScript: {time_ms*1000:.2f}ms avg")

    # ========================================================================
    # API RESPONSE BENCHMARKS
    # ========================================================================

    def benchmark_suggestions_api(self):
        """Benchmark: Refactoring suggestions API"""
        code = self.generate_python_code(50)

        time_ms = self.benchmark_operation("Suggestions API", lambda: self.service.get_refactoring_suggestions(code, "python", "medium"))

        assert time_ms < 0.2, f"Should be <200ms, took {time_ms*1000:.1f}ms"
        print(f"✅ Suggestions API: {time_ms*1000:.2f}ms avg")

    def benchmark_quick_fixes_api(self):
        """Benchmark: Quick fixes API"""
        code = self.generate_javascript_code(50)

        time_ms = self.benchmark_operation("Quick Fixes API", lambda: self.service.get_quick_fixes(code, "javascript"))

        assert time_ms < 0.1, f"Should be <100ms, took {time_ms*1000:.1f}ms"
        print(f"✅ Quick Fixes API: {time_ms*1000:.2f}ms avg")

    def benchmark_fix_application(self):
        """Benchmark: Applying a fix"""
        code = "var x = 10;\n"
        fixes = self.service.get_quick_fixes(code, "javascript")

        if fixes:
            fix = fixes[0]

            def apply():
                return self.service.apply_fix(code, fix)

            time_ms = self.benchmark_operation("Fix Application", apply, iterations=10)

            assert time_ms < 0.01, f"Should be <10ms, took {time_ms*1000:.2f}ms"
            print(f"✅ Fix Application: {time_ms*1000:.3f}ms avg")

    # ========================================================================
    # LANGUAGE COMPARISON
    # ========================================================================

    def benchmark_language_comparison(self):
        """Compare analysis speed across languages"""
        code_python = self.generate_python_code(100)
        code_javascript = self.generate_javascript_code(100)

        time_python = self.benchmark_operation("Python (100 lines) analysis", lambda: self.service.get_quick_fixes(code_python, "python"), iterations=10)

        time_javascript = self.benchmark_operation(
            "JavaScript (100 lines) analysis", lambda: self.service.get_quick_fixes(code_javascript, "javascript"), iterations=10
        )

        ratio = time_javascript / time_python if time_python > 0 else 1

        print(f"✅ Language Comparison:")
        print(f"   Python:     {time_python*1000:.2f}ms")
        print(f"   JavaScript: {time_javascript*1000:.2f}ms")
        print(f"   Ratio: {ratio:.2f}x")

    # ========================================================================
    # STRESS TESTS
    # ========================================================================

    def benchmark_stress_large_file(self):
        """Stress test: Very large file (1000 lines)"""
        code = self.generate_python_code(1000)

        start = time.perf_counter()
        result = self.service.get_quick_fixes(code, "python")
        elapsed = time.perf_counter() - start

        assert elapsed < 2.0, f"Should analyze 1000 lines in <2s, took {elapsed:.2f}s"
        assert result is not None

        print(f"✅ Stress test (1000 lines): {elapsed*1000:.1f}ms")

    def benchmark_stress_complex_code(self):
        """Stress test: Complex code patterns"""
        code = """
if x == True:
    if y == False:
        z = not not a
        if not not b == True:
            result = c == False
"""
        code = code * 50  # Repeat pattern 50 times

        start = time.perf_counter()
        result = self.service.get_quick_fixes(code, "python")
        elapsed = time.perf_counter() - start

        assert elapsed < 0.5, f"Should analyze in <500ms, took {elapsed*1000:.1f}ms"

        print(f"✅ Stress test (complex patterns): {elapsed*1000:.1f}ms, {len(result)} fixes found")

    def benchmark_stress_suggestions(self):
        """Stress test: Generate suggestions for large code"""
        code = self.generate_python_code(200)

        start = time.perf_counter()
        result = self.service.get_refactoring_suggestions(code, "python", "high")
        elapsed = time.perf_counter() - start

        assert elapsed < 0.5, f"Should generate suggestions in <500ms, took {elapsed*1000:.1f}ms"
        assert result["total_fixes"] >= 0

        print(f"✅ Stress test (suggestions): {elapsed*1000:.1f}ms, {result['total_fixes']} total fixes")

    # ========================================================================
    # CONSISTENCY & STABILITY
    # ========================================================================

    def benchmark_consistency(self):
        """Test consistency of results across runs"""
        code = self.generate_javascript_code(50)

        results = []
        for _ in range(5):
            result = self.service.get_quick_fixes(code, "javascript")
            results.append(len(result))

        # Should find same number of fixes each run
        assert len(set(results)) == 1, f"Inconsistent results: {results}"

        print(f"✅ Consistency test: {results[0]} fixes found consistently across 5 runs")


def run_benchmarks():
    """Run all performance benchmarks"""
    print("\n" + "=" * 70)
    print("PERFORMANCE BENCHMARKING SUITE")
    print("=" * 70 + "\n")

    bench = PerformanceBenchmark()

    benchmarks = [
        # Code size benchmarks
        ("Small Python (10 lines)", bench.benchmark_small_python),
        ("Medium Python (100 lines)", bench.benchmark_medium_python),
        ("Large Python (500 lines)", bench.benchmark_large_python),
        ("Small JavaScript (10 lines)", bench.benchmark_small_javascript),
        ("Medium JavaScript (100 lines)", bench.benchmark_medium_javascript),
        ("Large JavaScript (500 lines)", bench.benchmark_large_javascript),
        # API benchmarks
        ("Suggestions API", bench.benchmark_suggestions_api),
        ("Quick Fixes API", bench.benchmark_quick_fixes_api),
        ("Fix Application", bench.benchmark_fix_application),
        # Comparisons
        ("Language Comparison", bench.benchmark_language_comparison),
        # Stress tests
        ("Stress: Large file (1000 lines)", bench.benchmark_stress_large_file),
        ("Stress: Complex patterns", bench.benchmark_stress_complex_code),
        ("Stress: Suggestions", bench.benchmark_stress_suggestions),
        # Stability
        ("Consistency Test", bench.benchmark_consistency),
    ]

    passed = 0
    failed = 0

    for name, benchmark_func in benchmarks:
        try:
            benchmark_func()
            passed += 1
        except AssertionError as e:
            print(f"❌ {name}: FAILED - {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {name}: ERROR - {type(e).__name__}: {e}")
            failed += 1

    # Summary
    print("\n" + "=" * 70)
    print("PERFORMANCE RESULTS SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}/{len(benchmarks)}")
    print(f"❌ Failed: {failed}/{len(benchmarks)}")
    print(f"📊 Success Rate: {(passed/len(benchmarks)*100):.1f}%")
    print("=" * 70)

    # Detailed results
    print("\nDetailed Timing Results (milliseconds):")
    print("-" * 70)
    for name, timing in bench.results.items():
        print(f"{name:40} {timing['avg_ms']:8.3f} ms avg")
        if timing["stdev_ms"] > 0:
            print(f"{'':40} ±{timing['stdev_ms']:8.3f} ms stdev")
    print("=" * 70 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = run_benchmarks()
    sys.exit(0 if success else 1)
