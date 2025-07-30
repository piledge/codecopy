#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 30.07.2025 at 08:54

@author: piledge
"""

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="codecopy",
    version="0.1.0",
    packages=find_packages(),
    install_requires=requirements,
    author="piledge",
    author_email="",
    description="A Modul to create Prompts for coding with LLMs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/piledge/codecopy",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
