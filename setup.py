#!/usr/bin/env python
from setuptools import setup

VERSION = "0.2.7"

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="getschema",
    version=VERSION,
    description="Get jsonschema from sample records",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Daigo Tanaka, Anelen Co., LLC",
    url="https://github.com/anelendata/getschema",

    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",

        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",

        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],

    install_requires=[
        "setuptools>=40.3.0",
        "jsonpath-ng>=1.5.2",
        "python-dateutil>=2.8.1",
        "simplejson==3.11.1",
        "pyyaml>=5.1",
    ],
    entry_points="""
    [console_scripts]
    getschema=getschema:main
    """,
    packages=["getschema"],
    package_data={
        # Use MANIFEST.ini
    },
    include_package_data=True
)
