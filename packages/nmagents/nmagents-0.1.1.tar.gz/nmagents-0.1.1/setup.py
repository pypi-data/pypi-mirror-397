from pathlib import Path
import re

from setuptools import find_packages, setup


BASE_DIR = Path(__file__).parent


def read_version() -> str:
    """Extract the version string from nmagents/__init__.py."""
    init_py = BASE_DIR / "nmagents" / "__init__.py"
    match = re.search(r'__version__\s*=\s*"([^"]+)"', init_py.read_text())
    if not match:
        raise RuntimeError("Unable to find version string in __init__.py")
    return match.group(1)


setup(
    name="nmagents",
    version=read_version(),
    description="Minimal agentic AI helpers without a heavy framework",
    long_description=(BASE_DIR / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Alex Punnen",
    license="MIT",
    # Disable automatic License-File metadata to stay compatible with older twine/pkginfo
    license_files=(),
    packages=find_packages(exclude=("tests", "examples", "docs")),
    python_requires=">=3.10",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
    ],
)
