import os


def cleanup_file(dir_path: str, file_name: str) -> None:
    file_path = os.path.join(dir_path, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
