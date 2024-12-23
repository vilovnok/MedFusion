import os

def ensure_directory_exists(directory_path: str):
    """
    Checks the existence of the directory and creates it if necessary.

    :param directory_path: Путь к директории.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Директория '{directory_path}' была создана.")
    else:
        print(f"Директория '{directory_path}' уже существует.")