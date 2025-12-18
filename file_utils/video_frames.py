import os
import json
import shutil
import subprocess
from natsort import natsorted

image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.wmv')
video_extensiones = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v')

def count_frames(input_path):
    if not os.path.isdir(input_path):
        raise NotADirectoryError(f"La ruta no es una carpeta válida: {input_path}")

    image_count = sum(
        1 for file in os.listdir(input_path)
        if file.lower().endswith(image_extensions)
    )

    print(f"Carpeta: {os.path.basename(input_path)} | Total de imágenes: {image_count}")
    return image_count

def count_frames_in_folders(input_path):
    total = 0

    for folder_name in os.listdir(input_path):
        input_path = os.path.join(input_path, folder_name)

        if not os.path.isdir(input_path):
            continue

        # Count images inside the folder
        image_count = sum(
            1 for file in os.listdir(input_path)
            if file.lower().endswith(image_extensions)
        )
        total += image_count
        # Print the folder name and image count
        print(f"Folder: {folder_name} | Total images: {image_count}")

    print(f"Total {total}")

def count_subfolders(input_path):
    if not os.path.isdir(input_path):
        raise ValueError(f"The path '{input_path}' does not exist or is not a folder.")

    subfolders = [
        d for d in os.listdir(input_path)
        if os.path.isdir(os.path.join(input_path, d))
    ]

    return len(subfolders)

def count_subfolders_in_folders(input_path):
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

def move_folders_with_min_images(input_path, output_path, min_images=1800):
    os.makedirs(output_path, exist_ok=True)

    total_checked = 0
    total_moved = 0

    for folder_name in os.listdir(input_path):
        input_path = os.path.join(input_path, folder_name)

        if not os.path.isdir(input_path):
            continue

        total_checked += 1
        num_images = count_frames(input_path)

        if num_images >= min_images:
            dest_path = os.path.join(output_path, folder_name)
            print(f"✅ {folder_name}: {num_images} imágenes — moviendo a {dest_path}")
            try:
                shutil.move(input_path, dest_path)
                total_moved += 1
            except Exception as e:
                print(f"⚠️ Error al mover {folder_name}: {e}")
        else:
            print(f"⏩ {folder_name}: solo {num_images} imágenes, omitida.\n")

    print(f"\nProceso completado.")
    print(f"   Carpetas revisadas: {total_checked}")
    print(f"   Carpetas movidas: {total_moved}")

def rename_frames_recursively(input_path):
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

            # Si ya existe, agregar sufijo temporal
            if os.path.exists(new_path):
                temp_path = os.path.join(subinput_path, f"temp_{file}")
                os.rename(old_path, temp_path)
            else:
                os.rename(old_path, new_path)
                count += 1

        # --- Rename frames
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

def frames_2_video(input_path, output_path, fps=120, duracion=None):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"La carpeta {input_path} no existe.")

    frames = sorted([f for f in os.listdir(input_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))])
    if not frames:
        raise ValueError("No se encontraron imágenes en la carpeta especificada.")

    total_frames = len(frames)
    print(f"Total de frames encontrados: {total_frames}")

    # Si se especifica duración, ajustar fps real o velocidad
    vf_filter = []
    fps_real = fps

    if duracion:
        fps_real = total_frames / duracion
        print(f"Ajustando a {duracion:.2f}s → FPS efectivo: {fps_real:.2f}")
        vf_filter.append(f"setpts=PTS*1")

    input_pattern = os.path.join(input_path, "0000%04d.png")

    cmd_ffmpeg = [
        "ffmpeg",
        "-framerate", str(fps_real),  # FPS de entrada
        "-i", input_pattern,          # Patrón de frames
        "-vf", ",".join(vf_filter) if vf_filter else "null",  # Filtro de video
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",        # Compatibilidad amplia
        "-crf", "18",
        "-preset", "veryfast",
        output_path
    ]

    print(f"Creando video en: {output_path}")
    subprocess.run(cmd_ffmpeg)
    print("Video generado correctamente.")

def get_video_duration(input_path):
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
            print(f"[!] Error reading {filename}: {e}")

    return durations

def group_videos_into_batches(input_path, videos_per_batch=100):
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
