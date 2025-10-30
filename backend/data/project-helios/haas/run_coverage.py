#!/usr/bin/env python3
# HaaS Platform - Advanced Coverage Analysis Script
# Enhanced coverage reporting with multiple formats and tools
# Usage: python run_coverage.py [options]

import sys
import subprocess
import argparse
from pathlib import Path
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
import shutil

class CoverageAnalyzer:
    """Advanced coverage analysis with multiple reporting tools."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.coverage_dir = project_root / "htmlcov"
        self.coverage_xml = project_root / "coverage.xml"
        self.coverage_json = project_root / "coverage.json"

    def run_coverage(self, test_type: str = "all", fail_under: int = 80) -> bool:
        """Run coverage analysis with pytest-cov."""
        cmd = [
            "pytest",
            "--cov=app",
            "--cov=core",
            "--cov=validators",
            "--cov=schemas",
            f"--cov-fail-under={fail_under}",
            "--cov-report=term-missing",
            "--cov-report=html",
            "--cov-report=xml",
            "--cov-report=json",
            "-v"
        ]

        if test_type != "all":
            cmd.extend(["-m", test_type])

        print(f"🧪 Running coverage analysis for: {test_type}")
        print(f"Command: {' '.join(cmd)}")
        print("=" * 80)

        result = subprocess.run(cmd, cwd=self.project_root)
        return result.returncode == 0

    def generate_badge(self):
        """Generate coverage badge using python-genbadge."""
        try:
            cmd = ["genbadge", "coverage", "-i", str(self.coverage_xml), "-o", "coverage-badge.svg"]
            subprocess.run(cmd, cwd=self.project_root, check=True)
            print("✅ Coverage badge generated: coverage-badge.svg")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  python-genbadge not available. Install with: pip install python-genbadge")

    def run_diff_cover(self, compare_branch: str = "main"):
        """Run diff-cover for PR coverage analysis."""
        try:
            cmd = [
                "diff-cover",
                str(self.coverage_xml),
                f"--compare-branch={compare_branch}",
                "--html-report", "diff-cover-report.html"
            ]
            subprocess.run(cmd, cwd=self.project_root, check=True)
            print("✅ Diff coverage report generated: diff-cover-report.html")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  diff-cover not available. Install with: pip install diff-cover")

    def analyze_coverage_data(self) -> Dict:
        """Analyze coverage JSON data for insights."""
        if not self.coverage_json.exists():
            print("❌ Coverage JSON not found. Run tests first.")
            return {}

        try:
            with open(self.coverage_json, 'r') as f:
                data = json.load(f)

            # Extract key metrics
            totals = data.get('totals', {})
            coverage_pct = totals.get('percent_covered', 0)

            # Analyze files
            files = data.get('files', {})
            low_coverage_files = []
            uncovered_lines = []

            for file_path, file_data in files.items():
                file_coverage = file_data.get('summary', {}).get('percent_covered', 100)
                if file_coverage < 80:
                    low_coverage_files.append((file_path, file_coverage))

                # Collect uncovered lines
                missing_lines = file_data.get('missing_lines', [])
                if missing_lines:
                    uncovered_lines.extend([(file_path, line) for line in missing_lines])

            return {
                'overall_coverage': coverage_pct,
                'low_coverage_files': low_coverage_files[:10],  # Top 10
                'total_uncovered_lines': len(uncovered_lines),
                'files_analyzed': len(files)
            }

        except (json.JSONDecodeError, KeyError) as e:
            print(f"❌ Error parsing coverage data: {e}")
            return {}

    def generate_coverage_comment(self) -> str:
        """Generate a coverage comment for PRs (GitHub Actions style)."""
        analysis = self.analyze_coverage_data()

        if not analysis:
            return "❌ Unable to generate coverage comment - run tests first."

        coverage = analysis['overall_coverage']
        low_files = analysis['low_coverage_files']
        uncovered = analysis['total_uncovered_lines']

        comment = f"""## 📊 Coverage Report

**Overall Coverage: {coverage:.1f}%**

### 📈 Coverage Summary
- **Files Analyzed**: {analysis['files_analyzed']}
- **Uncovered Lines**: {uncovered}

### ⚠️ Files with Low Coverage (< 80%)
"""

        if low_files:
            for file_path, file_cov in low_files:
                comment += f"- `{file_path}`: {file_cov:.1f}%\n"
        else:
            comment += "🎉 All files meet the 80% coverage threshold!\n"

        comment += f"""
### 📋 Details
- Full report: [HTML Report](htmlcov/index.html)
- Coverage XML: `coverage.xml`
- Coverage Badge: `coverage-badge.svg`

---
*Generated by HaaS Platform Coverage Analyzer*
"""

        return comment

    def run_cuvner_analysis(self):
        """Run cuvner for alternate coverage visualizations."""
        try:
            # Generate terminal visualization
            cmd = ["cuvner", "--input", str(self.coverage_xml), "--format", "terminal"]
            subprocess.run(cmd, cwd=self.project_root)

            # Generate other formats if available
            for fmt in ["html", "svg"]:
                try:
                    cmd = ["cuvner", "--input", str(self.coverage_xml), "--format", fmt, f"--output", f"cuvner-report.{fmt}"]
                    subprocess.run(cmd, cwd=self.project_root, check=True)
                    print(f"✅ Cuvner {fmt.upper()} report: cuvner-report.{fmt}")
                except subprocess.CalledProcessError:
                    continue

        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  cuvner not available. Install with: pip install cuvner")

def main():
    parser = argparse.ArgumentParser(description="Advanced Coverage Analysis for HaaS Platform")
    parser.add_argument(
        "--type",
        default="all",
        choices=["all", "unit", "integration", "auth", "inmetro", "monitoring", "documents"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--fail-under",
        type=int,
        default=80,
        help="Fail if coverage is below this percentage"
    )
    parser.add_argument(
        "--badge",
        action="store_true",
        help="Generate coverage badge"
    )
    parser.add_argument(
        "--diff-cover",
        help="Run diff-cover analysis against specified branch"
    )
    parser.add_argument(
        "--comment",
        action="store_true",
        help="Generate PR comment"
    )
    parser.add_argument(
        "--cuvner",
        action="store_true",
        help="Run cuvner visualization"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze coverage data and show insights"
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent
    analyzer = CoverageAnalyzer(project_root)

    # Run coverage analysis
    success = analyzer.run_coverage(args.type, args.fail_under)

    if not success:
        print("❌ Coverage analysis failed!")
        sys.exit(1)

    # Run additional tools
    if args.badge:
        analyzer.generate_badge()

    if args.diff_cover:
        analyzer.run_diff_cover(args.diff_cover)

    if args.cuvner:
        analyzer.run_cuvner_analysis()

    if args.analyze:
        analysis = analyzer.analyze_coverage_data()
        if analysis:
            print("\n📊 Coverage Analysis Results:")
            print(f"Overall Coverage: {analysis['overall_coverage']:.1f}%")
            print(f"Files Analyzed: {analysis['files_analyzed']}")
            print(f"Uncovered Lines: {analysis['total_uncovered_lines']}")

            if analysis['low_coverage_files']:
                print("\n⚠️ Files with Low Coverage (< 80%):")
                for file_path, cov in analysis['low_coverage_files']:
                    print(f"  - {file_path}: {cov:.1f}%")

    if args.comment:
        comment = analyzer.generate_coverage_comment()
        print("\n📝 PR Comment:")
        print(comment)

        # Save to file
        with open(project_root / "coverage-comment.md", "w") as f:
            f.write(comment)
        print("💾 Comment saved to: coverage-comment.md")

    print("\n✅ Coverage analysis completed!")
    print(f"📊 HTML Report: {analyzer.coverage_dir}/index.html")
    print(f"📄 XML Report: {analyzer.coverage_xml}")
    print(f"📋 JSON Report: {analyzer.coverage_json}")

if __name__ == "__main__":
    main()