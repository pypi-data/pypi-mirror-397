"""Setup configuration for Anzo MCP Server package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements_v2.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="ags-mcp-server",
    version="1.0.0",
    author="Paresh Khandelwal",
    author_email="khandelwal.paresh@siemens.com",
    description="Model Context Protocol (MCP) server for Anzo Graph Database with 45+ tools and 10 comprehensive prompts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cambridgesemantics/anzo-mcp-server",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database :: Front-Ends",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            'ags-mcp-stdio=ags_mcp.stdio_server:main',
            'ags-mcp-http=ags_mcp.http_server:main',
        ],
    },
    include_package_data=True,
    package_data={
        "ags_mcp": ["*.md", "*.yaml"],
    },
    keywords="anzo mcp model-context-protocol graph-database sparql rdf knowledge-graph",
    project_urls={
        "Bug Reports": "https://github.com/cambridgesemantics/anzo-mcp-server/issues",
        "Documentation": "https://docs.cambridgesemantics.com/anzo/",
        "Source": "https://github.com/cambridgesemantics/anzo-mcp-server",
    },
)
