import sys
from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtWidgets import (
    QApplication, QWidget, QTextEdit, QPushButton, QVBoxLayout,
    QFileDialog, QLabel, QHBoxLayout, QComboBox
)
from kokoro_onnx import Kokoro
import soundfile as sf


# --- Worker Thread for Background WAV Synthesis ---
class Worker(QObject):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, text, voice, wav_path):
        super().__init__()
        self.text = text
        self.voice = voice
        self.wav_path = wav_path
        self.kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")

    def run(self):
        try:
            samples, rate = self.kokoro.create(
                self.text,
                voice=self.voice,
                speed=1.0,
                lang="en-us"
            )
            sf.write(self.wav_path, samples, rate)
            self.finished.emit(f"Saved: {self.wav_path}")
        except Exception as e:
            self.error.emit(str(e))


# --- Main GUI ---
class TTSApp(QWidget):
    def __init__(self):
        super().__init__()
        self.kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
        self.voices = list(self.kokoro.voices.keys())
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Kokoro TTS (WAV Output)")
        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        self.voice_dropdown = QComboBox()
        self.voice_dropdown.addItems(self.voices)
        layout.addWidget(QLabel("Select Voice:"))
        layout.addWidget(self.voice_dropdown)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.btn_process = QPushButton("Convert to WAV")
        self.btn_process.clicked.connect(self.convert_text)
        layout.addWidget(self.btn_process)

        self.setLayout(layout)

    def convert_text(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            self.status_label.setText("Enter some text.")
            return

        wav_path, _ = QFileDialog.getSaveFileName(self, "Save WAV", "", "WAV Files (*.wav)")
        if not wav_path:
            return

        self.status_label.setText("Processing...")

        voice = self.voice_dropdown.currentText()

        self.thread = QThread()
        self.worker = Worker(text, voice, wav_path)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_finished(self, message):
        self.status_label.setText(message)

    def on_error(self, error_msg):
        self.status_label.setText(f"Error: {error_msg}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TTSApp()
    window.resize(600, 500)
    window.show()
    sys.exit(app.exec())
