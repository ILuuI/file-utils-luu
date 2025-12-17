import os
import shutil
import pandas as pd

def organize_dataset_by_emotion(base_path, excel_path):
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
