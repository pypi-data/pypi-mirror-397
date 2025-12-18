"""Setup para publicar en PyPI."""

from setuptools import setup, find_packages
from pathlib import Path

# Leer el README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="artheon-sast",
    version="1.1",
    author="Dorian Tituaña, Ismael Toala",
    author_email="dorian.tituana@epn.edu.ec, ismael.toala@epn.edu.ec",
    description="Static Application Security Testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DorianTitu/Artheon-SAST-Slim",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.14",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires=">=3.8",
    keywords="sast security testing javascript vulnerability scanner",
    entry_points={
        "console_scripts": [
            "artheon-sast=language_analyzer.__main__:main",
        ],
    },
)
