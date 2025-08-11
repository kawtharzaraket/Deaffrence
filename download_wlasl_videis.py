import json
import os
import yt_dlp
import requests

GLOSSES = ['hello', 'eat', 'thank you']
ANNOTATION_PATH = 'datasets/WLASL_v0.3.json'
VIDEOS_DIR = 'datasets/WLASL_videos/'

os.makedirs(VIDEOS_DIR, exist_ok=True)

with open(ANNOTATION_PATH, 'r') as f:
    annotations = json.load(f)

def download_youtube(url, out_path):
    ydl_opts = {
        'outtmpl': out_path,
        'quiet': True,
        'format': 'mp4/bestaudio/best',
        'merge_output_format': 'mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def download_direct(url, out_path):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(out_path, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)

for entry in annotations:
    gloss = entry['gloss'].lower()
    if gloss in [g.lower() for g in GLOSSES]:
        for idx, instance in enumerate(entry.get('instances', [])):
            url = instance.get('url')
            video_id = instance.get('video_id')
            if not url or not video_id:
                continue
            # Name as gloss_idx.mp4 (e.g., hello_0.mp4, hello_1.mp4)
            out_path = os.path.join(VIDEOS_DIR, f"{gloss}_{idx}.mp4")
            if os.path.exists(out_path):
                continue
            try:
                if 'youtube.com' in url or 'youtu.be' in url:
                    download_youtube(url, out_path)
                elif url.endswith('.mp4'):
                    download_direct(url, out_path)
                else:
                    print(f"Unknown video source: {url}")
            except Exception as e:
                print(f"Failed to download {url}: {e}")

print("Download complete.")