import os
import cv2

image_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
video_extensiones = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v')

def process_image(input_path, output_path, size=(224, 224)):
    """
    Lee una imagen, la convierte a escala de grises y la redimensiona usando 
    interpolación bicúbica. Luego la guarda con alta calidad.
    
    :param input_path : str
        Carpeta raíz.
    :param output_path : str
        Carpeta destino post procesamiento.
    :param size : (int, int)
        Dimensiones de las imagenes/frames.
    """
    try:
        img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            print(f"Could not read {input_path}")
            return

        resized = cv2.resize(img, size, interpolation=cv2.INTER_CUBIC)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        cv2.imwrite(output_path, resized, [cv2.IMWRITE_JPEG_QUALITY, 95])

    except Exception as e:
        print(f"{input_path}: {e}")


def resize_all_subfolders(input_root, output_root, size=(224, 224)):
    """
    Docstring for resize_all_subfolders
    
    :param input_root : str
        Ruta donde se encuentran las imágenes.
    :param output_root : srt
        Ruta destino post procesamiento.
    :param size: (int, int)
        Dimensiones de las imagenes (W, H)
    """
    for root, dirs, files in os.walk(input_root):
        relative_path = os.path.relpath(root, input_root)
        output_folder = os.path.join(output_root, relative_path)

        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png")):

                input_img_path = os.path.join(root, file)
                output_img_path = os.path.join(output_folder, file)

                process_image(input_img_path, output_img_path, size)

        print(f"Processed folder: {root}")