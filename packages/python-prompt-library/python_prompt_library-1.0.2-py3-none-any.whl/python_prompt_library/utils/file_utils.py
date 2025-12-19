import os


def read_file(file_path):
    """Reads the content of a file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} does not exist.")
    with open(file_path, "r") as file:
        return file.read()


def write_file(file_path, content):
    """Writes content to a file."""

    with open(file_path, "w") as file:
        file.write(content)
