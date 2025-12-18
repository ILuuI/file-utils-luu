import os
import json
import shutil
import subprocess
from natsort import natsorted

image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.wmv')
video_extensiones = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v')

def count_frames(input_path):
    """
    Imprime la cantidad de frames existentes en una carpeta.
    
    :param input_path: str
        Ruta donde se encuentran los frames.
    """
    if not os.path.isdir(input_path):
        raise NotADirectoryError(f"The route is not a valid folder: {input_path}")

    image_count = sum(
        1 for file in os.listdir(input_path)
        if file.lower().endswith(image_extensions)
    )

    print(f"Folder: {os.path.basename(input_path)} | Total images: {image_count}")
    return image_count

def count_frames_in_folders(input_path):
    """
    Imprime la cantidad de frames en todas las subcarpetas de una ruta.
    
    :param input_path : str
        Ruta de la carpeta raíz.
    """
    total = 0
    for folder_name in os.listdir(input_path):
        input_path = os.path.join(input_path, folder_name)

        if not os.path.isdir(input_path):
            continue

        image_count = sum(
            1 for file in os.listdir(input_path)
            if file.lower().endswith(image_extensions)
        )
        total += image_count
        # Print the folder name and image count
        print(f"Folder: {folder_name} | Total images: {image_count}")

    print(f"Total {total}")

def count_subfolders(input_path):
    """
    Retorna la cantidad de subcarpetas de una ruta.
    
    :param input_path : str
        Ruta de la carpeta raíz.
    """

    if not os.path.isdir(input_path):
        raise ValueError(f"The path '{input_path}' does not exist or is not a folder.")

    subfolders = [
        d for d in os.listdir(input_path)
        if os.path.isdir(os.path.join(input_path, d))
    ]

    return len(subfolders)

def count_subfolders_in_folders(input_path):
    """
    Retorna la cantidad de carpetas existentes dentro de cada subcarpeta de una ruta.
    
    :param input_path : str
        Ruta de la carpeta raíz.
    """
    if not os.path.isdir(input_path):
        raise ValueError(f"The path '{input_path}' does not exist or is not a folder.")

    result = {}

    for folder in os.listdir(input_path):
        input_path = os.path.join(input_path, folder)

        if os.path.isdir(input_path):
            subfolders = [
                d for d in os.listdir(input_path)
                if os.path.isdir(os.path.join(input_path, d))
            ]
            result[folder] = len(subfolders)

    return result

def move_folders_with_min_frames(input_path, output_path, min_frames=1800):
    """
    Docstring for move_folders_with_min_frames
    
    :param input_path : str
        Ruta de la capeta raiz que contiene las subcarpetas.
    :param output_path : str
        Ruta destino post procesamiento.
    :param min_frames : str
        Cantidad mínima de frames para mover cada carpeta hacia 'output_path'
    """
    
    os.makedirs(output_path, exist_ok=True)

    total_checked = 0
    total_moved = 0

    for folder_name in os.listdir(input_path):
        input_path = os.path.join(input_path, folder_name)

        if not os.path.isdir(input_path):
            continue

        total_checked += 1
        num_images = count_frames(input_path)

        if num_images >= min_frames:
            dest_path = os.path.join(output_path, folder_name)
            print(f"✅ {folder_name}: {num_images} images — moving to {dest_path}")
            try:
                shutil.move(input_path, dest_path)
                total_moved += 1
            except Exception as e:
                print(f"Error trying to move {folder_name}: {e}")
        else:
            print(f"{folder_name}: just {num_images} images, omitted folder.\n")

    print(f"\nProcess completed.")
    print(f"Folders reviewed: {total_checked}")
    print(f"Folders moved: {total_moved}")

def rename_frames_recursively(input_path):
    """
    Organiza y renombra frames con el formato 'frame_XXXX'.
    
    :param input_path : str
        Carpeta raíz.
    """
    for subfolder in os.listdir(input_path):
        subinput_path = os.path.join(input_path, subfolder)
        if not os.path.isdir(subinput_path):
            continue

        files = [f for f in os.listdir(subinput_path) if f.lower().endswith(image_extensions)]
        if not files:
            continue

        files = natsorted(files)  # (frame_0001.png, frame_0001_1.png, frame_0002.png, etc.)

        print(f"Processing folder: {subfolder}")
        count = 1

        for file in files:
            old_path = os.path.join(subinput_path, file)
            new_name = f"frame_{count:04d}{os.path.splitext(file)[1]}"
            new_path = os.path.join(subinput_path, new_name)

            if os.path.exists(new_path):
                temp_path = os.path.join(subinput_path, f"temp_{file}")
                os.rename(old_path, temp_path)
            else:
                os.rename(old_path, new_path)
                count += 1

        temp_files = [f for f in os.listdir(subinput_path) if f.startswith("temp_")]
        temp_files = natsorted(temp_files)
        for temp_file in temp_files:
            old_path = os.path.join(subinput_path, temp_file)
            ext = os.path.splitext(temp_file.replace("temp_", ""))[1]
            new_name = f"frame_{count:04d}{ext}"
            new_path = os.path.join(subinput_path, new_name)
            os.rename(old_path, new_path)
            count += 1

        print(f"{count - 1} frames renamed sequentially as 'frame_XXXX'.")

def video2frames(input_path, output_path, quality=2):
    """
    Exporta los frames de un video.
    
    :param input_path : str
        Carpeta raíz.
    :param output_path : str
        Carpeta destino.
    :param quality : int, (1,2)
        Calidad de las imágenes.
    """
    if not os.path.isdir(input_path):
        print(f"Invalid path: {input_path}")
        return

    os.makedirs(output_path, exist_ok=True)

    files = natsorted(os.listdir(input_path))
    total_processed = 0

    for file_name in files:
        if not file_name.lower().endswith(video_extensiones):
            continue

        input_path = os.path.join(input_path, file_name)
        video_name = os.path.splitext(file_name)[0]

        frame_folder = os.path.join(output_path, video_name)
        os.makedirs(frame_folder, exist_ok=True)

        output_pattern = os.path.join(frame_folder, "frame_%04d.jpg")

        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-q:v", str(quality),
            "-vsync", "0",
            output_pattern,
            "-hide_banner",
            "-loglevel", "error"
        ]

        print(f"--- Extracting frames from: {file_name}")
        subprocess.run(cmd)
        print(f"--- Frames saved in: {frame_folder}\n")

        total_processed += 1
        print(f"Videos processed: {total_processed}")

    print(f"\nProcess completed: {total_processed} videos processed.")
    print(f"Frames created in: {output_path}")

def frames_2_video(input_path, output_path, fps=120, duration=None):
    """
    Conversión de conjunto de frames a video.

    :param input_path : str
        Carpeta raíz.
    :param output_path : str
        Carpeta destino post procesamiento.
    :param fps : int, optional
        Cantidad de fps (Opcional si se indica el argumento 'duration')
    :param duration : int, float
        Duración del video en segundos (Opcional si se indica el argumento 'fps')
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"The folder {input_path} doesn't exist.")

    frames = sorted([f for f in os.listdir(input_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))])
    if not frames:
        raise ValueError("No images were found in the specified folder.")

    total_frames = len(frames)
    print(f"Total frames found: {total_frames}")

    vf_filter = []
    fps_real = fps

    if duration:
        fps_real = total_frames / duration
        print(f"Adjusting to {duration:.2f}s - FPS: {fps_real:.2f}")
        vf_filter.append(f"setpts=PTS*1")

    input_pattern = os.path.join(input_path, "0000%04d.png")

    cmd_ffmpeg = [
        "ffmpeg",
        "-framerate", str(fps_real),
        "-i", input_pattern,
        "-vf", ",".join(vf_filter) if vf_filter else "null",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        "-preset", "veryfast",
        output_path
    ]

    print(f"Creating video in: {output_path}")
    subprocess.run(cmd_ffmpeg)
    print("Correct video generation.")

def get_video_duration(input_path):
    """
    Retorna la duración exacta (float) de un video.
    
    :param input_path : str
        Ruta del video.
    """
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                input_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return float(result.stdout.strip())
    except Exception:
        return None

def get_video_durations_in_folders(input_path):
    """
    Retorna la duración de videos en una carpeta raíz.
    
    :param input_path : str
        Carpeta raíz.
    """

    durations = {}

    for filename in os.listdir(input_path):
        if not filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv')):
            continue

        input_path = os.path.join(input_path, filename)
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
                 "-of", "json", input_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            data = json.loads(result.stdout)
            duration = float(data["format"]["duration"])
            durations[filename] = duration
            print(f"{filename}: {duration:.2f} seconds")
        except Exception as e:
            print(f"Error reading {filename}: {e}")

    return durations

def batch_videos_into_folders(input_path, videos_per_batch=100):
    """
    Agrupa los archivos de vídeo de un directorio en subcarpetas (batches), moviendo un número fijo de vídeos a cada carpeta.

    Cada lote se crea dentro del directorio de entrada y se nombra secuencialmente (p. ej., lote_1, lote_2, etc.).

    :input_path : str
        Path to the directory containing the video files.
    :videos_per_batch : int, optional
        Number of videos per batch folder (default is 100).
    """
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')

    videos = [
        f for f in os.listdir(input_path)
        if f.lower().endswith(video_extensions)
    ]

    for i in range(0, len(videos), videos_per_batch):
        batch = videos[i:i + videos_per_batch]
        batch_folder = os.path.join(input_path, f"batch_{i//videos_per_batch + 1}")
        os.makedirs(batch_folder, exist_ok=True)

        for v in batch:
            shutil.move(
                os.path.join(input_path, v),
                os.path.join(batch_folder, v)
            )
