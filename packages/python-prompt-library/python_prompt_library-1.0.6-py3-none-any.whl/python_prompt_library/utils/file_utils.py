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


def create_file(file_path):
    """
    Creates an empty file at the specified path.

    Args:
        file_path (str): The path of the file to create.
    """
    try:
        with open(file_path, "x") as file:  # Open the file in exclusive creation mode
            pass  # Create the file without writing any content
        print(f"File created successfully: {file_path}")
    except FileExistsError:
        print(f"File already exists: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
