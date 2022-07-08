#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from os.path import dirname, join

from setuptools import find_packages, setup


def get_version(package):
    init_py = open(os.path.join(package, "__init__.py"), encoding="utf-8").read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


setup(
    name="dagster-hashicorp",
    version=get_version("dagster_hashicorp"),
    url="https://github.com/silentsokolov/dagster-hashicorp",
    license="MIT",
    description="Package for integrating Hashicorp Vault with Dagster.",
    long_description_content_type="text/markdown",
    long_description=open(join(dirname(__file__), "README.md"), encoding="utf-8").read(),
    author="Dmitriy Sokolov",
    author_email="silentsokolov@gmail.com",
    packages=find_packages(exclude=["dagster_hashicorp_tests*"]),
    include_package_data=True,
    install_requires=[
        "hvac",
    ],
    python_requires=">=3.6",
    zip_safe=False,
    platforms="any",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords=[
        "dagster",
        "hashicorp",
        "vault",
    ],
)
