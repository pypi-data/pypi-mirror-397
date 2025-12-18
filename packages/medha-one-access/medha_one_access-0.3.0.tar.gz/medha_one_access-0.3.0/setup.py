"""
Setup script for MedhaOne Access Control Library
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "MedhaOne Access Control Library - Enterprise access control system with BODMAS resolution"

# Read requirements
def read_requirements(filename):
    req_path = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="medha-one-access",
    version="0.1.1",
    author="MedhaOne Analytics",
    author_email="contactmedhaanalytics@gmail.com",
    description="Enterprise access control system with BODMAS resolution",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/medhaone-analytics/medha-one-access",
    project_urls={
        "Bug Reports": "https://github.com/medhaone-analytics/medha-one-access/issues",
        "Source": "https://github.com/medhaone-analytics/medha-one-access",
        "Documentation": "https://medha-one-access.readthedocs.io/",
    },
    packages=find_packages(exclude=["examples", "examples.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
    ],
    python_requires=">=3.8",
    install_requires=[
        "sqlalchemy",
        "pydantic", 
        "psycopg2-binary",
        "cryptography",
        "alembic",
        "python-dateutil",
    ],
    extras_require={
        "api": [
            "fastapi",
            "uvicorn",
            "python-multipart",
        ],
        "cli": [
            "click",
            "rich",
            "typer",
        ],
        "dev": [
            "black",
            "flake8",
            "mypy", 
            "sphinx",
            "sphinx-rtd-theme",
        ],
    },
    entry_points={
        "console_scripts": [
            "medha-access=medha_one_access.cli.main:app",
        ],
    },
    package_data={
        "medha_one_access": [
            "migrations/alembic.ini",
            "migrations/script.py.mako",
            "migrations/versions/*.py",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "access-control", 
        "authorization", 
        "permissions", 
        "rbac", 
        "abac",
        "bodmas",
        "expressions",
        "security",
        "fastapi",
        "sqlalchemy",
    ],
)