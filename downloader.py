# downloader.py
import yt_dlp
import os
from urllib.parse import urlparse, parse_qs, urlencode

def clean_url(url):
    # parsing URL
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    # Only keep 'v' parameter in url
    cleaned_params = {'v': query_params.get('v', [])}
    new_query = urlencode(cleaned_params, doseq=True)
    
    # return parsed url
    return parsed_url._replace(query=new_query, fragment='').geturl()


def download_audio(url, select_number=0, ffmpeg_path="none" ):
    url = clean_url(url)
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if 'entries' in info:
            # If url means 'playlist'
            video_count = len(info['entries'])
            print(f"The number of tracks in the playlist is {video_count}")
        else:
            # If url means 'single track'
            video_count = 1
            print("This is a single track")

    for i in range(1, video_count + 1):
        if int(select_number) == i or int(select_number) == 0:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '0',
                }, {
                    'key': 'EmbedThumbnail',
                }, {
                    'key': 'FFmpegMetadata',
                }],
                'writethumbnail': True,
                'outtmpl': 'Downloads/%(title)s.%(ext)s',
                'playliststart': i,
                'playlistend': i,
                'postprocessor_args': [
                    '-metadata', f"track='{i}'"
                ],
                'ffmpeg_location': ffmpeg_path,  # Add path of ffmpeg
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

    return "Download completed successfully!"