#! /usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="Margos",
    version="0.0.1",
    python_requires=">=3.6",
    packages=find_packages(exclude=["tests"]),
    package_data={"": ["resources/*"]},
    entry_points={"console_scripts": ["margos = margos.main:main"]},
    extras_require={"dev": ["mypy", "pyflakes", "black"]},
    license="MIT",
    author="Simon Alfassa",
    author_email="simon@sa-web.fr",
    description="Customize your Mate applets from your scripts' output",
    long_description=open("./README.md").read(),
    keywords="margos mate applet desktop argos bitbar linux",
    url="https://github.com/ssimono/margos",
)
