#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from setuptools import setup, find_packages

with open("requirements.txt", encoding="utf-8") as r:
    requires = [i.strip() for i in r]

with open("VkDynamicCover/__init__.py", encoding="utf-8") as f:
    version = re.findall(r"__version__ = \"(.+)\"", f.read())[0]

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="VkDynamicCover",
    version=version,

    author="KlukaCross",

    description="Program for dynamic updating cover of a group or a public in VK",
    long_description=long_description,
    long_description_content_type='text/markdown',

    url="https://github.com/KlukaCross/VkDynamicCover",
    download_url="https://github.com/KlukaCross/VkDynamicCover/releases/latest",

    license="MIT License",
    platforms=["OS Independent"],

    packages=find_packages(),
    install_requires=requires,

    python_requires=">=3.7, <4"
)
