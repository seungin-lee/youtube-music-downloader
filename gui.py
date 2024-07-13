# gui.py
import sys
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QTextEdit, QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QIcon
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

    def __init__(self, url, track_number, ffmpeg_path):
        QThread.__init__(self)
        self.url = url
        self.track_number = track_number
        self.ffmpeg_path = ffmpeg_path

    @pyqtSlot()
    def run(self):
        try:
            result = download_audio(self.url, self.track_number, self.ffmpeg_path)
            self.finished.emit(True, result)
        except Exception as e:
            self.finished.emit(False, str(e))

class YouTubeDownloaderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('YouTube Downloader')
        self.setGeometry(300, 300, 500, 300)
        grid = QGridLayout()

        url_label = QLabel('Enter YouTube URL:')
        self.url_entry = QLineEdit()
        grid.addWidget(url_label, 0, 0)
        grid.addWidget(self.url_entry, 0, 1, 1, 2)

        track_label = QLabel('Track Number (optional):')
        self.track_entry = QLineEdit()
        self.track_entry.setFixedWidth(50)
        grid.addWidget(track_label, 1, 0)
        grid.addWidget(self.track_entry, 1, 1)

        download_button = QPushButton('Download')
        download_button.clicked.connect(self.download)
        grid.addWidget(download_button, 2, 0, 1, 3)

        install_ffmpeg_button = QPushButton('Install FFmpeg')
        install_ffmpeg_button.clicked.connect(self.install_ffmpeg)
        grid.addWidget(install_ffmpeg_button, 3, 0, 1, 3)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        grid.addWidget(self.output_text, 4, 0, 1, 3)

        self.setLayout(grid)

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
        
        self.download_thread = DownloadThread(url, track_number, ffmpeg_path)
        self.download_thread.finished.connect(self.onDownloadComplete)
        self.download_thread.start()

    def onDownloadComplete(self, success, message):
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)

    # Not Implemented Yet!
    def install_ffmpeg(self):
        print("Installing FFmpeg...")
        # 여기에 FFmpeg 설치 로직을 구현하세요.

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YouTubeDownloaderGUI()
    ex.show()
    sys.exit(app.exec())
