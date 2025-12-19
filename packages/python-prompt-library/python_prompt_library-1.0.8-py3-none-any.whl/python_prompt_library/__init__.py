import os

path = r"C:\Users\rgutkows\KTLO_Support\Python_Prompt_Library"

# Determine which version file to use
version_file = (
    "\VERSION_TEST.txt"
    if os.getenv("UPLOAD_TARGET") == "testpypi"
    else "\VERSION_PYPI.txt"
)

fpath = path + version_file

# Read the version from the selected file
with open(fpath, "r") as vf:
    version = vf.read().strip()

# Check the target repository
target_repo = os.getenv("TARGET_REPO", "pypi")  # Default to PyPI

# Append a suffix for TestPyPI
if target_repo == "testpypi":
    __version__ = f"{version}-test"
else:
    __version__ = version
