import pandas as pd
import os
import requests
import ast
import re

excel_file = r"C:\Users\Ayush\Desktop\tridha\Fae Beauty.xlsx"
download_folder = r"C:\Users\Ayush\Desktop\tridha\Fae_Posts_Downloaded"

os.makedirs(download_folder, exist_ok=True)

df = pd.read_excel(excel_file)

def clean_name(text):
    text = str(text)
    text = re.sub(r'[\\/*?:"<>|]', "_", text)
    return text[:80]

def download_file(media_url, save_path):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(media_url, headers=headers, timeout=30)

        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            print("Downloaded:", save_path)
        else:
            print("Failed:", response.status_code, media_url)

    except Exception as e:
        print("Error:", e)

for index, row in df.iterrows():

    post_type = str(row.get("type", "")).lower()
    post_url = row.get("url", "")
    shortcode = post_url.rstrip("/").split("/")[-1] if pd.notna(post_url) else index + 1

    base_name = clean_name(f"{index+1}_{shortcode}")

    print(f"\nProcessing {index+1}/{len(df)} - {post_type}")

    # CASE 1: Reel / Video post
    if pd.notna(row.get("videoUrl")) and str(row.get("videoUrl")) != "nan":
        video_url = row["videoUrl"]
        save_path = os.path.join(download_folder, base_name + ".mp4")
        download_file(video_url, save_path)

    # CASE 2: Carousel / Sidecar post
    elif pd.notna(row.get("images")) and str(row.get("images")) not in ["nan", "[]"]:
        try:
            images = ast.literal_eval(row["images"])

            for i, img_url in enumerate(images):
                save_path = os.path.join(download_folder, f"{base_name}_image_{i+1}.jpg")
                download_file(img_url, save_path)

        except Exception as e:
            print("Could not read images column:", e)

            if pd.notna(row.get("displayUrl")):
                save_path = os.path.join(download_folder, base_name + ".jpg")
                download_file(row["displayUrl"], save_path)

    # CASE 3: Single static image post
    elif pd.notna(row.get("displayUrl")) and str(row.get("displayUrl")) != "nan":
        image_url = row["displayUrl"]
        save_path = os.path.join(download_folder, base_name + ".jpg")
        download_file(image_url, save_path)

    else:
        print("No downloadable media found for:", post_url)

print("\nDone. Check this folder:")
print(download_folder)
