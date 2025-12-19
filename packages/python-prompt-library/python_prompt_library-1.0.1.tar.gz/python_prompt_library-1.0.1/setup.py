from setuptools import setup, find_packages
import os

# Determine which version file to use
version_file = (
    "VERSION_TEST.txt"
    if os.getenv("UPLOAD_TARGET") == "testpypi"
    else "VERSION_PYPI.txt"
)

# Read the version from the selected file
with open(version_file, "r") as vf:
    version = vf.read().strip()

setup(
    name="python_prompt_library",
    version=version,  # Dynamically read version
    author="Ryan Gutkowski",
    author_email="ryan.gutkowski@lplfinancial.com",
    description="A Python prompy library to consolidate libraries and utility scripts",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
