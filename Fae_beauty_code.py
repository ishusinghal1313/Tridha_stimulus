
import pandas as pd
import os
from yt_dlp import YoutubeDL

# Excel file
excel_file = r"C:\Users\Ayush\Desktop\tridha\Fae Beauty.xlsx"

# Output folder
download_folder = r"C:\Users\Ayush\Desktop\tridha\Fae_Downloads"
os.makedirs(download_folder, exist_ok=True)

# Read Excel
df = pd.read_excel(excel_file)

# Instagram URL column
url_column = "url"

# Download settings
ydl_opts = {
    "outtmpl": os.path.join(download_folder, "%(id)s.%(ext)s"),
    "format": "best",
    "ignoreerrors": True,
    "cookiesfrombrowser": ("chrome",),
}

with YoutubeDL(ydl_opts) as ydl:
    for index, row in df.iterrows():

        post_url = row[url_column]

        if pd.isna(post_url):
            continue

        print(f"Downloading {index+1}/{len(df)}")

        try:
            ydl.download([post_url])
        except Exception as e:
            print(f"Failed: {post_url}")
            print(e)

print("Finished!")