# 🎬 CaptionGen AI – AI Powered Video Caption Generator

CaptionGen AI is an **AI-powered video caption generator** that automatically converts video speech into accurate subtitles.
It uses **speech recognition, AI text processing, and video tools** to generate professional subtitle files and optionally burn captions directly into the video.

This project is designed for **developers, content creators, educators, and accessibility use cases**.

---

# 🚀 Features

| Feature                   | Description                                        |
| ------------------------- | -------------------------------------------------- |
| 🎙️ Speech Recognition    | Uses AI speech-to-text to transcribe video audio   |
| 🤖 AI Caption Processing  | Cleans grammar and formats captions automatically  |
| 🌍 Multi-language Support | Supports 40+ languages                             |
| 🎨 Caption Styles         | Standard, Educational, Cinematic, Accessible       |
| 🔥 Burn Captions          | Embed captions permanently into the video          |
| 🖥️ Web Interface         | Upload video and generate captions through browser |
| ⌨️ CLI Support            | Run caption generation from terminal               |
| 📁 Subtitle Export        | Generates `.srt` subtitle files                    |

---

# 🧠 Technologies Used

* Python
* Flask
* OpenAI Whisper
* FFmpeg
* PyTorch
* HTML / CSS
* JavaScript

---

# 📂 Project Structure

```
CaptionGen-AI/
│
├── src/
│   ├── app.py                  # Flask Web Application
│   └── caption_generator.py    # Core caption generation logic
│
├── uploads/                    # Uploaded videos
├── captions_output/            # Generated captions
│
├── requirements.txt            # Python dependencies
├── README.md
└── .env                        # Environment variables (optional)
```

---

# ⚙️ Installation Guide

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/nikhilpowar09/CaptionGen-AI.git
cd CaptionGen-AI
```

---

# 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

# 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 4️⃣ Install FFmpeg

FFmpeg is required for **audio extraction and caption burning**.

### Windows

Download from:

https://ffmpeg.org/download.html

Add FFmpeg to **system PATH**.

### Ubuntu / Debian

```bash
sudo apt install ffmpeg
```

### macOS

```bash
brew install ffmpeg
```

---

# ▶️ Running the Project

## Option 1 — Run Web Application

```bash
cd src
python app.py
```

Open browser:

```
http://localhost:5000
```

Upload a video and generate captions.

---

# Option 2 — Run via Command Line

```bash
cd src
python caption_generator.py video.mp4
```

Example with options:

```bash
python caption_generator.py video.mp4 --style educational
python caption_generator.py video.mp4 --style cinematic --burn
python caption_generator.py video.mp4 --language hi
```

---

# 🎨 Caption Styles

| Style       | Description                           |
| ----------- | ------------------------------------- |
| Standard    | Clean subtitles for general videos    |
| Educational | Precise formatting for lectures       |
| Cinematic   | Dramatic caption formatting           |
| Accessible  | Simplified captions for accessibility |

---

# 📤 Output Files

Generated files are stored in:

```
captions_output/
```

Example outputs:

```
video_captions.srt
video_captioned.mp4
```

---

# 📜 Example SRT Format

```
1
00:00:01,000 --> 00:00:04,000
Welcome to this tutorial on Artificial Intelligence.

2
00:00:04,500 --> 00:00:08,200
Today we will learn how machine learning works.
```

---

# 🛠 Troubleshooting

| Issue                      | Solution                         |
| -------------------------- | -------------------------------- |
| FFmpeg not found           | Install FFmpeg and add to PATH   |
| Whisper installation error | Run `pip install openai-whisper` |
| Torch installation slow    | This is normal for first install |
| Port already in use        | Run `python app.py --port 5001`  |

---

# 🌐 Deployment

This project can be deployed on:

* Render
* PythonAnywhere
* Replit
* Fly.io
* AWS / DigitalOcean

Example live deployment:

```
https://captiongen-ai.onrender.com
```

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a new branch
3. Make changes
4. Submit a pull request

---

# 📄 License

This project is open-source and available under the **MIT License**.

---

# 👨‍💻 Author

**Nikhil Powar**

GitHub
https://github.com/nikhilpowar09

---

# ⭐ Support

If you like this project, please **star the repository** on GitHub.
