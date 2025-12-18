import os
import shutil
import pandas as pd

def organize_dataset_by_emotion(base_path, excel_path):
    """
    Organiza un conjunto de datos moviendo archivos o carpetas según
    la emoción estimada indicada en un archivo Excel.

    La función lee un archivo Excel que contiene las columnas
    'subject', 'filename' y 'estimated emotion', y reubica cada
    archivo o carpeta dentro de un directorio con el nombre de la
    emoción correspondiente. El nuevo nombre del archivo o carpeta
    incluye el identificador del sujeto para evitar colisiones.

    base_path : str
        Ruta base donde se encuentra el dataset original.
    excel_path : str
        Ruta al archivo Excel que contiene la información de
        organización por emoción.
    """
    df = pd.read_excel(excel_path)
    df.columns = [c.strip().lower() for c in df.columns]

    for _, row in df.iterrows():
        subject = row["subject"]
        filename = row["filename"]
        emotion = row["estimated emotion"]

        src = os.path.join(base_path, subject, filename)
        dst = os.path.join(base_path, emotion, f"{subject}_{filename}")

        if os.path.isdir(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
