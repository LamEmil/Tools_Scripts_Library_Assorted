# Kokoro TTS WAV Converter

A lightweight GUI to convert text into `.wav` audio using Kokoro TTS (ONNX) and PySide6. No internet required after setup.

---

## 🔧 Requirements

- Python 3.10–3.12
- Windows (recommended)

---

## 📦 Installation

Install dependencies via pip:

```bash
pip install kokoro-onnx PySide6 soundfile
```

---

## 📁 Required Files

Place the following files in the same directory as `main.py`:

- `main.py` → the GUI script
- `kokoro-v1.0.onnx` → Kokoro model
- `voices-v1.0.bin` → Voice definitions
  
# Download either voices.json or voices.bin (bin is preferred)
https://github.com/nazdridoy/kokoro-tts/releases/download/v1.0.0/voices-v1.0.bin

# Download the model
https://github.com/nazdridoy/kokoro-tts/releases/download/v1.0.0/kokoro-v1.0.onnx

---

## ▶️ Usage

```bash
python main.py
```

Steps:

1. Enter or paste text into the input box.
2. Select a voice from the dropdown.
3. Click **"Convert to WAV"**.
4. Choose where to save the `.wav` file.

The app will generate a `.wav` file using the selected voice and save it to the chosen location.

---

## ✅ Features

- Local, fast, high-quality TTS
- Voice selection via dropdown
- Simple PySide6 GUI
- Non-blocking UI (threaded audio generation)
- Direct `.wav` export — no ffmpeg or mp3 tools needed
- Great for converting book chapters, notes, or scripts into audio

---
