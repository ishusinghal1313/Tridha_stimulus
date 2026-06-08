import pandas as pd
import os
import requests
import ast
import re
from yt_dlp import YoutubeDL

excel_file = r"C:\Users\Ayush\Desktop\tridha\Fae Beauty.xlsx"
download_folder = r"C:\Users\Ayush\Desktop\tridha\Fae_All_Media"

os.makedirs(download_folder, exist_ok=True)

df = pd.read_excel(excel_file)

def clean_name(text):
    text = str(text)
    text = re.sub(r'[\\/*?:"<>|]', "_", text)
    return text[:80]

def download_image(media_url, save_path):
    try:
        r = requests.get(media_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        if r.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(r.content)
            print("Image downloaded:", save_path)
        else:
            print("Image failed:", r.status_code)
    except Exception as e:
        print("Image error:", e)

# yt-dlp settings for reels/videos
ydl_opts = {
    "outtmpl": os.path.join(download_folder, "%(id)s.%(ext)s"),
    "format": "best",
    "ignoreerrors": True,
}

with YoutubeDL(ydl_opts) as ydl:

    for index, row in df.iterrows():

        post_type = str(row.get("type", "")).lower()
        product_type = str(row.get("productType", "")).lower()
        post_url = row.get("url", "")

        shortcode = str(post_url).rstrip("/").split("/")[-1]
        base_name = clean_name(f"{index+1}_{shortcode}")

        print(f"\nProcessing {index+1}/{len(df)} | type: {post_type} | productType: {product_type}")

        # CASE 1: Reels / Videos
        if post_type == "video" or product_type == "clips":
            try:
                print("Downloading reel/video:", post_url)
                ydl.download([post_url])
            except Exception as e:
                print("Video failed:", post_url)
                print(e)

        # CASE 2: Carousel / Sidecar images
        elif post_type == "sidecar":
            try:
                images = row.get("images")

                if pd.notna(images) and str(images) not in ["[]", "nan"]:
                    images = ast.literal_eval(images)

                    for i, img_url in enumerate(images):
                        save_path = os.path.join(download_folder, f"{base_name}_image_{i+1}.jpg")
                        download_image(img_url, save_path)
                else:
                    save_path = os.path.join(download_folder, base_name + ".jpg")
                    download_image(row["displayUrl"], save_path)

            except Exception as e:
                print("Carousel failed:", e)

        # CASE 3: Single static image
        else:
            if pd.notna(row.get("displayUrl")):
                save_path = os.path.join(download_folder, base_name + ".jpg")
                download_image(row["displayUrl"], save_path)
            else:
                print("No media found for:", post_url)

print("\nDone. Check folder:")
print(download_folder)
