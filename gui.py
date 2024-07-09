# gui.py
import sys
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtGui import QIcon
from downloader import download_audio
import platform

class YouTubeDownloaderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('YouTube Downloader')
        self.setGeometry(300, 300, 400, 200)

        layout = QVBoxLayout()

        url_layout = QHBoxLayout()
        url_label = QLabel('Enter YouTube URL:')
        self.url_entry = QLineEdit()
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_entry)
        layout.addLayout(url_layout)

        track_layout = QHBoxLayout()
        track_label = QLabel('Track Number (optional):')
        self.track_entry = QLineEdit()
        self.track_entry.setFixedWidth(50)
        track_layout.addWidget(track_label)
        track_layout.addWidget(self.track_entry)
        track_layout.addStretch()
        layout.addLayout(track_layout)

        download_button = QPushButton('Download')
        download_button.clicked.connect(self.download)
        layout.addWidget(download_button)

        install_ffmpeg_button = QPushButton('Install FFmpeg')
        install_ffmpeg_button.clicked.connect(self.install_ffmpeg)
        layout.addWidget(install_ffmpeg_button)

        self.setLayout(layout)

    def download(self):
        url = self.url_entry.text()
        track_number = self.track_entry.text() or "0"
        if platform.system() == 'Windows':
            ffmpeg_path = os.path.join(os.environ['ProgramFiles'], 'ffmpeg', 'bin')
            if not os.path.isfile(ffmpeg_path+"/ffmpeg.exe"):
                QMessageBox.critical(self, "Error", "[Windows] ffmpeg is not installed")
                return None
        else:
            try:
                ffmpeg_full_path = subprocess.check_output(['which', 'ffmpeg'], universal_newlines=True).strip()
                if not ffmpeg_full_path:
                    QMessageBox.critical(self, "Error", "[Linux] ffmpeg is not installed")
                    return None
                ffmpeg_path = os.path.dirname(ffmpeg_full_path)
            except subprocess.CalledProcessError:
                QMessageBox.critical(self, "Error", "[Linux] ffmpeg is not installed")
                return None
        
        try:
            result = download_audio(url, track_number, ffmpeg_path)
            QMessageBox.information(self, "Success", result)
            return None
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return None

    # Not Implemented Yet!
    def install_ffmpeg(self):
        pass
    #     try:
    #         subprocess.run(["install_ffmpeg.bat"], check=True, shell=True)
    #         QMessageBox.information(self, "Success", "FFmpeg installed successfully!")
    #     except subprocess.CalledProcessError:
    #         QMessageBox.critical(self, "Error", "Failed to install FFmpeg.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YouTubeDownloaderGUI()
    ex.show()
    sys.exit(app.exec())
