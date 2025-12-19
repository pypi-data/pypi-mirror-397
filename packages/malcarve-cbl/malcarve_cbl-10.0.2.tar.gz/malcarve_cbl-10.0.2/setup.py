#!/usr/bin/env python3
"""Setup script."""
import os
import subprocess

from setuptools import setup
from setuptools.command.build import build


class CBuild(build):
    """Build class to build c dependencies on install."""

    def run(self):
        """Build the c-dependencies for malcarve to function."""
        ext_dir: str = os.path.join(os.path.dirname(__file__), "malcarve_cbl/ext")
        build_script_path: str = os.path.join(ext_dir, "build.sh")
        subprocess.run(build_script_path, check=True)
        build.run(self)


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def open_file(fname):
    """Open and return a file-like object for the relative filename."""
    return open(os.path.join(os.path.dirname(__file__), fname))


setup(
    name="malcarve-cbl",
    description="Detects and extracts obfuscated, embedded content from files.",
    author="Azul",
    author_email="azul@asd.gov.au",
    url="https://www.asd.gov.au/",
    packages=["malcarve_cbl"],
    package_data={"malcarve_cbl": ["ext/build/keyedDecrypt.so"]},
    include_package_data=True,
    python_requires=">=3.12",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
    ],
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    install_requires=[r.strip() for r in open_file("requirements.txt") if not r.startswith("#")],
    cmdclass={"build": CBuild},
)
