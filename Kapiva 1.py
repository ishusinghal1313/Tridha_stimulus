import pandas as pd
import os
import re
import time
import requests
import instaloader
from yt_dlp import YoutubeDL

excel_file = r"C:\Users\Ayush\Desktop\tridha\Kapiva.xlsx"
main_folder = r"C:\Users\Ayush\Desktop\tridha\Kapiva_Media_ID_Wise"

os.makedirs(main_folder, exist_ok=True)

df = pd.read_excel(excel_file)

L = instaloader.Instaloader(
    download_pictures=True,
    download_videos=True,
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    compress_json=False,
    post_metadata_txt_pattern=""
)

def get_shortcode(url):
    match = re.search(r"instagram\.com/(?:p|reel|tv)/([^/?#]+)/?", str(url))
    return match.group(1) if match else None

def folder_has_files(folder):
    return len([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]) > 0

def download_direct(url, save_path):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=40)
        if r.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(r.content)
            print("Direct downloaded:", save_path)
            return True
    except Exception as e:
        print("Direct download failed:", e)

    return False

for index, row in df.iterrows():

    post_id = str(int(row["id"]))      # your 1-100 ID
    post_url = row["url"]
    post_type = str(row.get("type", "")).lower()
    product_type = str(row.get("productType", "")).lower()

    post_folder = os.path.join(main_folder, post_id)
    os.makedirs(post_folder, exist_ok=True)

    print(f"\nProcessing ID {post_id} | Type: {post_type} | URL: {post_url}")

    # 1. If Apify gave direct mp4 URL in audioUrl, download it first
    if "audioUrl" in df.columns and pd.notna(row.get("audioUrl")) and str(row.get("audioUrl")).startswith("http"):
        direct_url = row["audioUrl"]
        download_direct(direct_url, os.path.join(post_folder, f"{post_id}.mp4"))

    # 2. If still empty and it is video/reel, use yt-dlp
    if not folder_has_files(post_folder) and (post_type == "video" or product_type == "clips"):
        ydl_opts = {
            "outtmpl": os.path.join(post_folder, f"{post_id}.%(ext)s"),
            "format": "best",
            "ignoreerrors": True,
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([post_url])
        except Exception as e:
            print("yt-dlp failed:", e)

    # 3. If still empty, use Instaloader for static image / carousel / sidecar
    if not folder_has_files(post_folder):
        shortcode = get_shortcode(post_url)

        if shortcode:
            try:
                post = instaloader.Post.from_shortcode(L.context, shortcode)
                L.download_post(post, target=post_folder)
            except Exception as e:
                print("Instaloader failed:", e)

    # 4. Remove empty folders
    if not folder_has_files(post_folder):
        print(f"No media downloaded for ID {post_id}")
        try:
            os.rmdir(post_folder)
        except:
            pass

    time.sleep(3)

print("\nDone. Check folder:")
print(main_folder)
