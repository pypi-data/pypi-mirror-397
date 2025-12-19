"""
Setup para el paquete felicidad
"""

from setuptools import setup, find_packages
import os

# Leer el README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="felicidad",
    version="1.0.0",
    author="XzLuizem",
    author_email=" luism.jim7@gmail.com",
    description="Tu dosis diaria de felicidad programática 💖",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/XzLuizem/felicidad",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "felicidad=felicidad.cli:main",
        ],
    },
    keywords="happiness, wellbeing, mental-health, developer-tools, fun",
    project_urls={
        "Bug Reports": "https://github.com/XzLuizem/felicidad/issues",
        "Source": "https://github.com/XzLuizem/felicidad",
    },
)
