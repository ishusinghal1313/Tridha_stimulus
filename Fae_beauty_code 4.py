import pandas as pd
import os
import requests
import ast
from yt_dlp import YoutubeDL

excel_file = r"C:\Users\Ayush\Desktop\tridha\Fae Beauty.xlsx"
main_folder = r"C:\Users\Ayush\Desktop\tridha\Fae_Media_ID_Wise"

os.makedirs(main_folder, exist_ok=True)

df = pd.read_excel(excel_file)

def download_image(url, save_path):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        if r.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(r.content)
            print("Downloaded image:", save_path)
        else:
            print("Image failed:", r.status_code)
    except Exception as e:
        print("Image error:", e)

for index, row in df.iterrows():

    post_id = str(int(row["id"]))   # your 1-100 ID column
    post_folder = os.path.join(main_folder, post_id)
    os.makedirs(post_folder, exist_ok=True)

    post_type = str(row.get("type", "")).lower()
    post_url = row.get("url", "")

    print(f"\nProcessing ID {post_id} | Type: {post_type}")

    # SIDE CAR: download full carousel from Instagram URL
    if post_type == "sidecar":

        ydl_opts = {
            "outtmpl": os.path.join(post_folder, f"{post_id}_%(playlist_index)s.%(ext)s"),
            "format": "best",
            "ignoreerrors": True,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([post_url])
        except Exception as e:
            print("Sidecar download failed:", e)

    # VIDEO / REEL
    elif post_type == "video":

        ydl_opts = {
            "outtmpl": os.path.join(post_folder, f"{post_id}.%(ext)s"),
            "format": "best",
            "ignoreerrors": True,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([post_url])
        except Exception as e:
            print("Video failed:", e)

    # SINGLE IMAGE
    elif pd.notna(row.get("displayUrl")):

        save_path = os.path.join(post_folder, f"{post_id}.jpg")
        download_image(row["displayUrl"], save_path)

    else:
        print("No media found for ID:", post_id)

print("\nDone. Check folder:")
print(main_folder)
