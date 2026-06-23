"""
Test runner script for myrag
"""
import sys
import argparse
from pathlib import Path


def run_tests(test_type="all", verbose=True, coverage=False):
    """
    Run tests
    
    Args:
        test_type: Type of tests to run (all, unit, integration)
        verbose: Verbose output
        coverage: Show coverage report
    """
    import pytest
    
    args = []
    
    if verbose:
        args.append("-v")
    
    if test_type == "unit":
        args.extend(["-m", "unit"])
    elif test_type == "integration":
        args.extend(["-m", "integration"])
    
    if coverage:
        args.extend([
            "--cov=src",
            "--cov-report=term-missing",
            "--cov-report=html"
        ])
    
    args.append("tests/")
    
    print("=" * 60)
    print(f"Running {'unit' if test_type == 'unit' else 'integration' if test_type == 'integration' else 'all'} tests...")
    print("=" * 60)
    print()
    
    result = pytest.main(args)
    
    print()
    print("=" * 60)
    if result == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ Some tests failed (exit code: {result})")
    print("=" * 60)
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Run myrag tests")
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration"],
        default="all",
        help="Type of tests to run (default: all)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Less verbose output"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Show coverage report"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick test (skip integration)"
    )
    
    args = parser.parse_args()
    
    test_type = "unit" if args.quick else args.type
    verbose = not args.quiet
    
    return run_tests(test_type, verbose, args.coverage)


if __name__ == "__main__":
    sys.exit(main())
