
# 🎙️ Andrew's TTS (Pocket TTS Modern)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![React](https://img.shields.io/badge/react-19.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Docker-lightgrey.svg)

**Andrew's TTS** is a professional, industrial-grade text-to-speech application designed to run **100% offline** on your local machine. It wraps the powerful `pocket-tts` library in a stunning, modern Glassmorphism UI, offering high-quality speech synthesis without the need for cloud APIs or GPUs.

> **Zero Hosting Required.** Your privacy is guaranteed. No data leaves your device.

![Screenshot](G:\P Ltd\Text-to-Speech-WebPage\demo.png)
*(Replace this path with a real screenshot of your application interface if available)*

---

## ✨ Key Features

### 🎨 Modern User Experience
- **Glassmorphism UI**: A sleek, translucent interface with dynamic animated backgrounds.
- **Reactive Interactions**: Built with **React 19** and **Vite** for instant feedback.
- **Professional Desktop App**: Runs as a standalone Windows application with a branded splash screen, powered by `pywebview`.

### 🗣️ Advanced Speech Engine
- **High-Fidelity Audio**: Uses a 100M parameter flow-matching model for natural, human-like speech.
- **CPU Optimized**: heavily optimized to run smoothly on standard consumer CPUs (no NVIDIA GPU required).
- **Instant Voice Cloning**: Upload a 10-second `.wav` clip to clone any voice in seconds.
- **Predefined Personas**: One-click access to high-quality voices like Alba, Marius, Javert, and more.
- **Real-time Streaming**: Low-latency audio generation for immediate playback.

---

## 🚀 Installation & Usage

You can run Andrew's TTS as a desktop application or host it as a web service.

### 💿 Option 1: Desktop App (Windows) - *Recommended*
The easiest way to use the application.
1. Download the latest **Installer** (`AndrewTTS_Setup.exe`) from the Releases page.
2. Run the installer and follow the wizard.
3. Launch **Andrew's TTS** from your desktop.
   - *Note: On first run, the app will download the necessary AI models (~400MB). Audio generation is completely offline thereafter.*

### 🐳 Option 2: Docker (Web Deployment)
Ideal for hosting on a local server or cloud provider (e.g., Render, Railway).
```bash
# Build the image
docker build -t andrew-tts .

# Run the container
docker run -p 8000:8000 andrew-tts
```
Access the web interface at `http://localhost:8000`.

### 💻 Option 3: Manual Developer Setup
If you want to modify the code or contribute.

**Prerequisites:**
- Python 3.10+
- Node.js 18+

**1. Backend Setup:**
```bash
cd backend
# Create virtual environment (optional but recommended)
python -m venv venv
# Windows: venv\Scripts\activate | Mac/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

**2. Frontend Setup:**
```bash
cd frontend
npm install
npm run dev
```

---

## 🛠️ Building the Desktop App
To build the `.exe` and installer yourself:

1. **Build Frontend**:
   ```bash
   cd frontend
   npm run build
   ```
   This compiles the React app to `dist/`, which is copied to the backend static folder.

2. **Package with PyInstaller**:
   ```bash
   # From the project root
   pyinstaller pocket_tts_app.spec
   ```
   This creates a standalone executable in `dist/`.

3. **Create Installer (Inno Setup)**:
   - Open `installer.iss` with Inno Setup Compiler.
   - Compile the script to generate `AndrewTTS_Setup.exe`.

---

## 🏗️ Tech Stack

- **Frontend**: React 19, Vite, Axios, Lucide React, CSS Modules (Glassmorphism).
- **Backend**: Python, FastAPI, Uvicorn, Torch (CPU).
- **AI Core**: [Pocket TTS](https://github.com/danijar/pocket-tts) (Flow-matching architecture).
- **Desktop**: PyWebView (Chromium embedded), PyInstaller, Inno Setup.

---

## 🤝 Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any features, bug fixes, or documentation improvements.

## 📜 License
This project is an independent implementation wrapping the `pocket-tts` library.
- Application code: **MIT License**.
- AI Model Weights: Please refer to the original `pocket-tts` and HuggingFace repositories for model licensing terms.

---
**Created by Andrew
