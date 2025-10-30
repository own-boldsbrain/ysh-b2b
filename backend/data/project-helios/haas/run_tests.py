# HaaS Platform - Test Execution Script
# Run all tests with coverage reporting
# Usage: python run_tests.py [options]

import sys
import subprocess
from pathlib import Path

def run_tests(test_type="all", coverage=True, verbose=True, advanced_coverage=False):
    """
    Run test suite with specified options.

    Args:
        test_type: "all", "unit", "integration", "auth", "inmetro", etc.
        coverage: Whether to generate coverage report
        verbose: Verbose output
        advanced_coverage: Use advanced coverage analysis with multiple tools
    """
    if advanced_coverage:
        # Use the advanced coverage script
        cmd = [sys.executable, "run_coverage.py", "--type", test_type]

        if not verbose:
            cmd.append("--quiet")

        print(f"🧪 Running ADVANCED coverage analysis for {test_type} tests...")
    else:
        # Use standard pytest with coverage
        cmd = ["pytest"]

        # Add verbosity
        if verbose:
            cmd.append("-v")

        # Add coverage
        if coverage:
            cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])

        # Add test markers
        if test_type != "all":
            cmd.extend(["-m", test_type])

        print(f"🧪 Running {test_type} tests...")

    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)

    result = subprocess.run(cmd, cwd=Path(__file__).parent)

    if result.returncode == 0:
        print("\n✅ All tests passed!")
        if coverage and not advanced_coverage:
            print("\n📊 Coverage report: htmlcov/index.html")
        elif advanced_coverage:
            print("\n📊 Advanced coverage reports generated!")
            print("   - HTML: htmlcov/index.html")
            print("   - Badge: coverage-badge.svg (if available)")
            print("   - Comment: coverage-comment.md")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run HaaS Platform tests")
    parser.add_argument(
        "--type",
        default="all",
        choices=["all", "unit", "integration", "auth", "inmetro",
                 "monitoring", "documents"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Skip coverage reporting"
    )
    parser.add_argument(
        "--advanced-coverage",
        action="store_true",
        help="Use advanced coverage analysis with multiple reporting tools"
    )
    
    args = parser.parse_args()
    
    run_tests(
        test_type=args.type,
        coverage=not args.no_coverage,
        verbose=not args.quiet,
        advanced_coverage=args.advanced_coverage
    )
