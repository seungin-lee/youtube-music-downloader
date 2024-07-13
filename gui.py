# gui.py
import sys
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QTextEdit, QMessageBox, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import QObject, pyqtSignal, QThread, pyqtSlot, Qt
from PyQt6.QtGui import QIcon, QPixmap
from PIL.ImageQt import ImageQt
from downloader import download_audio
import platform

class Stream(QObject):
    newText = pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))

    def flush(self):
        pass

class DownloadThread(QThread):
    finished = pyqtSignal(bool, str)
    metadata_ready = pyqtSignal(str, str, QPixmap)
    progress = pyqtSignal(int) # Show download progress

    def __init__(self, url, track_number, ffmpeg_path):
        QThread.__init__(self)
        self.url = url
        self.track_number = track_number
        self.ffmpeg_path = ffmpeg_path

    @pyqtSlot()
    def run(self):
        try:
            # # Generating Virtual Metadata
            # title = "Sample Song"
            # artist = "Sample Artist"
            # # temp image
            # pixmap = QPixmap(100, 100)
            # pixmap.fill(Qt.GlobalColor.red)  # Temp image. Red
            
            # # signal generating about metadata
            # self.metadata_ready.emit(title, artist, pixmap)
            
            result = download_audio(self.url, self.track_number, self.ffmpeg_path, self.get_metadata, self.update_progress)
            self.finished.emit(True, result)
        except Exception as e:
            self.finished.emit(False, str(e))

    def update_progress(self, value):
        self.progress.emit(value)

    def get_metadata(self, title, artist, thumbnail):
        if thumbnail:
            pixmap = QPixmap.fromImage(ImageQt(thumbnail))
        else:
            pixmap = QPixmap(100, 100)
            pixmap.fill(Qt.GlobalColor.red)  # Temp image. Red
        self.metadata_ready.emit(title, artist, pixmap)

class YouTubeDownloaderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('YouTube Music Downloader')
        self.setGeometry(300, 300, 700, 300)

        main_layout = QHBoxLayout()
        left_layout = QGridLayout()
        right_layout = QVBoxLayout()

        # Left layout
        url_label = QLabel('Enter YouTube URL\t')
        self.url_entry = QLineEdit()
        left_layout.addWidget(url_label, 0, 0)
        left_layout.addWidget(self.url_entry, 0, 1, 1, 2)

        track_label = QLabel('Track Number (optional)')
        self.track_entry = QLineEdit()
        self.track_entry.setFixedWidth(50)
        left_layout.addWidget(track_label, 1, 0)
        left_layout.addWidget(self.track_entry, 1, 1)

        self.download_button = QPushButton('Download')
        self.download_button.clicked.connect(self.download)
        left_layout.addWidget(self.download_button, 2, 0, 1, 3)

        install_ffmpeg_button = QPushButton('Install FFmpeg')
        install_ffmpeg_button.clicked.connect(self.install_ffmpeg)
        left_layout.addWidget(install_ffmpeg_button, 3, 0, 1, 3)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        left_layout.addWidget(self.output_text, 4, 0, 1, 3)

        # Right Layout (Metadata of the song)
        self.album_art_label = QLabel("Album Art. Download not started")
        self.album_art_label.setFixedSize(200, 200)
        self.album_art_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.album_art_label.setStyleSheet("border: 1px solid black;")

        self.title_label = QLabel("Title  : ")
        self.artist_label = QLabel("Artist : ")

        right_layout.addWidget(self.album_art_label)
        right_layout.addWidget(self.title_label)
        right_layout.addWidget(self.artist_label)
        right_layout.addStretch()

        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)
        # Redirect the console output
        sys.stdout = Stream(newText=self.onUpdateText)
        sys.stderr = Stream(newText=self.onUpdateText)

    def onUpdateText(self, text):
        cursor = self.output_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(text)
        self.output_text.setTextCursor(cursor)
        self.output_text.ensureCursorVisible()
        QApplication.processEvents()

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

        self.download_button.setEnabled(False) # disable the download button until complete 
        self.download_thread = DownloadThread(url, track_number, ffmpeg_path)
        self.download_thread.finished.connect(self.onDownloadComplete)
        self.download_thread.metadata_ready.connect(self.update_metadata_display)
        self.download_thread.progress.connect(self.update_button_progress)  # Connect progress signal to update_button_progress
        self.download_thread.start()

    @pyqtSlot(int)
    def update_button_progress(self, value):
        self.download_button.setText(f"Downloading... {value}%")  # Update button text with progress

    def update_metadata_display(self, title, artist, album_art):
        self.title_label.setText(f"Title  : {title}")
        self.artist_label.setText(f"Artist : {artist}")
        self.album_art_label.clear()
        self.album_art_label.setPixmap(album_art.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))

    def onDownloadComplete(self, success, message):
        self.download_button.setEnabled(True) # enable the download button
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)
        self.download_button.setText("Download")

    # Not Implemented Yet!
    def install_ffmpeg(self):
        print("Installing FFmpeg...")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YouTubeDownloaderGUI()
    ex.show()
    sys.exit(app.exec())
