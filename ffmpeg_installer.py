import os
import requests
import zipfile
import sys

def download_file(url, filename, progress_callback=None):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        block_size = 1024  # 1 KB
        downloaded = 0
        print(f"다운로드 시작: {filename}")
        with open(filename, 'wb') as f:
            for data in r.iter_content(block_size):
                size = f.write(data)
                downloaded += size
                if progress_callback:
                    progress_callback(downloaded, total_size)
                percentage = int(50 * downloaded / total_size)
                # sys.stdout.write(f"\r[{'█' * percentage}{' ' * (50 - percentage)}] {downloaded}/{total_size} bytes")
                # sys.stdout.flush()
    print("\n다운로드 완료")

def extract_with_progress(zip_file, extract_dir, progress_callback=None):
    with zipfile.ZipFile(zip_file, 'r') as zf:
        total = len(zf.infolist())
        print(f"압축 해제 시작: {zip_file}")
        for i, member in enumerate(zf.infolist(), 1):
            zf.extract(member, extract_dir)
            percentage = int(50 * i / total)
            if progress_callback:
                progress_callback(i, total)
            # sys.stdout.write(f"\r[{'█' * percentage}{' ' * (50 - percentage)}] {i}/{total} files")
            # sys.stdout.flush()
    print("\n압축 해제 완료")

def install_ffmpeg_from_github(download_progress_callback=None, extraction_progress_callback=None):
    install_dir = os.getcwd()
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zip_file = "ffmpeg.zip"

    download_file(ffmpeg_url, zip_file, download_progress_callback)
    extract_with_progress(zip_file, install_dir, extraction_progress_callback)

    #ffmpeg_dir = next(os.walk(install_dir))[1][0]  # 압축 해제된 첫 번째 폴더
    os.rename(os.path.join(install_dir, "ffmpeg-master-latest-win64-gpl"), os.path.join(install_dir, "ffmpeg"))
    ffmpeg_bin = os.path.join(install_dir, "ffmpeg", "bin")

    print(f"FFmpeg가 성공적으로 설치되었습니다: {ffmpeg_bin}")
    print("FFmpeg를 시스템 전체에서 사용하려면 위 경로를 시스템 환경 변수 PATH에 추가하세요.")

    os.remove(zip_file)
    print("임시 파일이 삭제되었습니다.")



if __name__ == "__main__":
    install_ffmpeg_from_github()
