# downloader.py
import yt_dlp
import os
from PIL import Image
from io import BytesIO
from urllib.parse import urlparse, parse_qs, urlencode
import requests
import mutagen
from mutagen.id3 import ID3, APIC



def clean_url(url):
    # parsing URL
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    if 'playlist?' in parsed_url.path:
        return url

    # Only keep 'v' parameter in url
    cleaned_params = {}
    if 'v' in query_params:
        cleaned_params['v'] = query_params['v']

    new_query = urlencode(cleaned_params, doseq=True)
    
    # return parsed url
    return parsed_url._replace(query=new_query, fragment='').geturl()

def resize_image(album_art):
    width, height = album_art.size
    if width > height:
        left = (width - height) / 2
        right = (width + height) / 2
        album_art = album_art.crop((left, 0 , right, height))
    else:
        top = (height - width) / 2
        bottom = (height + width) /2
        album_art = album_art.crop((0, top, width, bottom))
    return album_art

def set_album_art(mp3_path, img_path):
    audio = mutagen.File(mp3_path)
    if audio.tags is None:
        audio.add_tags()
    
    with open(img_path, 'rb') as albumart:
        audio.tags.add( 
            APIC(
                encoding=3, #UTF-8
                mime='image/jpeg',
                type=3, # 3 means album cover
                desc='Cover',
                data=albumart.read()
            )
        )
    audio.save()


def download_audio(url, select_number=0, ffmpeg_path="none", metadata_callback=None, progress_callback=None):
    url = clean_url(url)
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

        # Extract metadata
        title = info.get('title', 'Unknown Title')
        artist = info.get('uploader', 'Unknown Artist')
        thumbnail_url = info.get('thumbnail')

        # Download thumbnail_url for sending to gui via callback
        if thumbnail_url:
            response = requests.get(thumbnail_url)
            thumbnail = Image.open(BytesIO(response.content))
            thumbnail = resize_image(thumbnail)

            # Save the thumbnail to a temporary file
            thumbnail_path = "thumbnail.jpg"
            thumbnail.save(thumbnail_path)
        else:
            thumbnail = None

        if metadata_callback:
            metadata_callback(title, artist, thumbnail)


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
            download_file_path = None
            def progress_hook(d):
                if d['status'] == 'downloading':
                    percent = d['_percent_str'].strip('%')
                    if progress_callback:
                        progress_callback(int(float(percent)))
            def postprocessor_hook(d):
                nonlocal download_file_path
                if d['status'] == 'finished':
                    download_file_path = d['info_dict']['filepath']

            ydl_opts = {
                'format': 'bestaudio/best',
                'progress_hooks': [progress_hook],
                'postprocessor_hooks': [postprocessor_hook],
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
                set_album_art(download_file_path, thumbnail_path)

    if thumbnail_path and os.path.exists(thumbnail_path):
        os.remove(thumbnail_path)

    return "Download completed successfully!"
