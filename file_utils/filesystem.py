import os
import shutil

def move_folder(input_folder, output_folder):
    if not os.path.isdir(input_folder):
        raise FileNotFoundError(f"Source folder not found: {input_folder}")

    os.makedirs(output_folder, exist_ok=True)
    dest_path = os.path.join(output_folder, os.path.basename(input_folder))
    shutil.move(input_folder, dest_path)
    return dest_path

def move_folder_contents(input_folder, output_folder):
    if not os.path.isdir(input_folder):
        raise FileNotFoundError(input_folder)

    os.makedirs(output_folder, exist_ok=True)

    for item in os.listdir(input_folder):
        shutil.move(
            os.path.join(input_folder, item),
            os.path.join(output_folder, item)
        )

def delete_folder(folder_path):
    if not os.path.isdir(folder_path):
        return False
    shutil.rmtree(folder_path)
    return True

def clear_folder(folder_path):
    if not os.path.isdir(folder_path):
        return False

    for item in os.listdir(folder_path):
        path = os.path.join(folder_path, item)
        if os.path.isfile(path):
            os.unlink(path)
        else:
            shutil.rmtree(path)
    return True

