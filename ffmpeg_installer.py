import os
import requests
import zipfile
import sys

def download_file(url, filename, progress_callback=None):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        block_size = 8096 
        downloaded = 0
        print(f"Start Download: {filename}")
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress = int(50 * downloaded/total_size)
                        progress_callback(progress)
    print("Download complete.")

def extract_with_progress(filename, extract_dir, progress_callback=None):
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        total_files = len(zip_ref.infolist())
        print(f"Start extraction: {filename}")
        for i, file in enumerate(zip_ref.infolist()):
            zip_ref.extract(file)
            if progress_callback:
                progress = 50 + int(50 * (i+1)/ total_files)
                progress_callback(progress)

    print("Extraction complete.")

def install_ffmpeg_from_github(progress_callback):
    install_dir = os.getcwd()
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zip_file = "ffmpeg.zip"

    download_file(ffmpeg_url, zip_file, progress_callback)
    extract_with_progress(zip_file, install_dir, progress_callback)

    os.rename(os.path.join(install_dir, "ffmpeg-master-latest-win64-gpl"), os.path.join(install_dir, "ffmpeg"))
    ffmpeg_bin = os.path.join(install_dir, "ffmpeg", "bin")

    print(f"ffmpeg is installed successfully: {ffmpeg_bin}")

    os.remove(zip_file)
    print("Temp file is removed.")



if __name__ == "__main__":
    install_ffmpeg_from_github()
