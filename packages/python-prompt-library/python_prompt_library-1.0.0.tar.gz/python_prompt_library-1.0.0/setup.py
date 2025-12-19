from setuptools import setup, find_packages

setup(
    name="python_prompt_library",  # Name of the package
    version="1.0.0",  # Version of the package
    author="Ryan Gutkowski",  # Author name
    author_email="ryan.gutkowski@lplfinancial.com",  # Author email
    description="A utility library for file operations",  # Short description
    long_description=open("README.md").read(),  # Long description (e.g., from README)
    long_description_content_type="text/markdown",  # Format of the long description
    url="",  # Project URL (e.g., GitHub repo)
    packages=find_packages(),  # Automatically find all packages in the project
    install_requires=[
        # List of dependencies
        # Example: "numpy>=1.21.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Minimum Python version required
)
