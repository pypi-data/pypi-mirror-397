#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setup script for GitLab PR Analyzer.

MIT License
"""

from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
readme_path = this_directory / "README.md"
long_description = "GitLab Merge Request Analyzer"
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

setup(
    name="gitlab-pr-analyzer",
    version="0.9.1",
    author="GitLab PR Analyzer Team",
    description="Intelligent tool for collecting, analyzing, and summarizing GitLab Merge Requests and commits",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://example.com/gitlab-pr-analyzer",
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "click>=8.1.0",
        "rich>=13.0.0",
        "requests>=2.31.0",
        "python-gitlab>=3.15.0",
        "gitpython>=3.1.40",
        "python-dateutil>=2.8.2",
        "fuzzywuzzy>=0.18.0",
        "python-levenshtein>=0.21.0",
    ],
    entry_points={
        "console_scripts": [
            # short name for daily usage
            "glpa=gitlab_pr_analyzer.cli:cli",
            # keep legacy entrypoint for backward compatibility
            "gl-pr-ai=gitlab_pr_analyzer.cli:cli",
            # new entrypoint aligned with github analyzer naming
            "gl-pr-analyzer=gitlab_pr_analyzer.cli:cli",
        ],
    },
)
