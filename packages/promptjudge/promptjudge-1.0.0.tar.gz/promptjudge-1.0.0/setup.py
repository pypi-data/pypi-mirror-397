"""
Setup configuration for PromptJudge Python SDK.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="promptjudge",
    version="1.0.0",
    author="PromptJudge",
    author_email="support@promptjudge.com",
    description="Python SDK for the PromptJudge AI Security API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/promptjudge/promptjudge-python",
    project_urls={
        "Bug Tracker": "https://github.com/promptjudge/promptjudge-python/issues",
        "Documentation": "https://docs.promptjudge.com",
        "Source Code": "https://github.com/promptjudge/promptjudge-python",
    },
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="promptjudge, ai, security, prompt injection, llm, api, sdk",
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "responses>=0.23.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
