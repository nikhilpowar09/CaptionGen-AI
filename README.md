# 🎬 AI-Powered Video Caption Generator

An **Agentic AI pipeline** that autonomously transcribes, cleans, and formats captions for any video file. Powered by **Grok Grok-sonnet-4-20250514** (tool use / function calling) and **OpenAI Whisper**.

---

## ✨ Features

| Feature | Detail |
|---|---|
| 🤖 Agentic AI | Grok autonomously orchestrates all steps with tool use |
| 🎙️ Speech Recognition | OpenAI Whisper (multilingual, offline) |
| 🧠 AI Enhancement | Grok cleans grammar, fixes filler words, formats SRT |
| 🎨 4 Caption Styles | Standard, Educational, Cinematic, Accessible |
| 🔥 Burn to Video | Embed captions permanently into a new video |
| 🌍 40+ Languages | Auto-detect or specify language |
| 🖥️ Web UI | Beautiful dark-theme browser interface |
| ⌨️ CLI | Full command-line support |

---

## 📁 Project Structure

```
ai-caption-generator/
├── src/
│   ├── caption_generator.py   ← Core agentic pipeline + CLI
│   └── app.py                 ← Flask web UI
├── captions_output/           ← Generated SRT files + captioned videos
├── uploads/                   ← Uploaded videos (web UI)
├── .vscode/
│   ├── launch.json            ← Debug configurations
│   └── settings.json          ← VS Code Python settings
├── requirements.txt
└── README.md
```

---

## 🚀 Step-by-Step Setup in VS Code

### Step 1 — Prerequisites

Install these before starting:

**ffmpeg** (required for audio extraction + video burning):
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows — download from https://ffmpeg.org/download.html
# Then add to PATH
```

**Python 3.9+** — check with: `python --version`

---

### Step 2 — Open in VS Code

```bash
# Clone or download the project, then:
cd ai-caption-generator
code .
```

---

### Step 3 — Create Virtual Environment

Open the VS Code **Terminal** (`Ctrl+`` ` or `Cmd+`` `) and run:

```bash
# Create venv
python -m venv venv

# Activate it:
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

VS Code will detect the venv automatically. If prompted, click **"Yes"** to use it as the workspace interpreter.

---

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

> ⚠️ **Note on PyTorch/Whisper**: The first install downloads ~500MB for PyTorch. This is normal.

---

### Step 5 — Set Your API Key

**macOS/Linux** (add to `~/.zshrc` or `~/.bashrc` for persistence):
```bash
export GROK_API_KEY=sk-ant-your-key-here
```

**Windows** (PowerShell):
```powershell
$env:GROK_API_KEY = "sk-ant-your-key-here"
```

Or create a `.env` file in the project root:
```
GROK_API_KEY=sk-ant-your-key-here
```

Get your key at: https://console.GROK.com

---

### Step 6 — Run the Project

#### Option A: Web UI (recommended)

```bash
cd src
python app.py
```

Then open **http://localhost:5000** in your browser.

#### Option B: Command Line

```bash
cd src

# Basic usage
python caption_generator.py ../my_video.mp4

# With options
python caption_generator.py ../my_video.mp4 --style educational
python caption_generator.py ../my_video.mp4 --style cinematic --burn
python caption_generator.py ../my_video.mp4 --language hi --style accessible
```

#### Option C: VS Code Debugger

1. Press `F5` or go to **Run → Start Debugging**
2. Select **"CLI: Generate Captions"** or **"Web UI: Caption Generator"**
3. Enter your video path when prompted

---

## 🤖 How the Agentic Pipeline Works

Grok uses **tool use** to autonomously plan and execute the caption workflow:

```
User Request
     │
     ▼
┌─────────────────────────────────────────┐
│          Grok Agent (Grok-sonnet-4-20250514)            │
│                                         │
│  Thinks: "I need to:                   │
│   1. Extract audio from video"          │
│        │                                │
│        ▼                                │
│  [Tool Call: extract_audio]            │
│        │ result: audio.wav              │
│        ▼                                │
│  [Tool Call: transcribe_audio]         │
│        │ result: raw transcript         │
│        ▼                                │
│  [Tool Call: generate_captions]        │
│        │ result: polished SRT           │
│        ▼                                │
│  [Tool Call: save_captions]            │
│        │ result: file saved             │
│        ▼                                │
│  (optional) [Tool Call: burn_captions] │
└─────────────────────────────────────────┘
     │
     ▼
  Output: .srt file + (optionally) captioned .mp4
```

The agent loop continues until `stop_reason == "end_turn"` with no pending tool calls.

---

## 🎨 Caption Styles

| Style | Best For | What Grok Does |
|---|---|---|
| **Standard** | General videos | Cleans grammar, formats cleanly |
| **Educational** | Lectures, tutorials | Precise punctuation, defines terms |
| **Cinematic** | Films, short films | Artistic phrasing, dramatic pauses |
| **Accessible** | Public content | Simple words, [MUSIC] markers, spell out numbers |

---

## 📤 Output Files

All outputs go to `captions_output/`:

- `{video_name}_captions.srt` — subtitle file
- `{video_name}_captioned.mp4` — video with burned-in captions (if `--burn` used)

---

## 🛠️ Troubleshooting

| Error | Fix |
|---|---|
| `GROK_API_KEY not set` | Set the env variable (Step 5) |
| `ffmpeg not found` | Install ffmpeg and ensure it's in PATH |
| `whisper not installed` | `pip install openai-whisper` |
| `CUDA out of memory` | Whisper will auto-fall back to CPU |
| Port 5000 in use | `python app.py --port 5001` |
| Video too large | Compress video first or use CLI |

---

## 📝 SRT Format Example

```
1
00:00:01,000 --> 00:00:04,200
Welcome to this tutorial on machine learning.

2
00:00:04,500 --> 00:00:08,300
Today we'll cover neural networks
and how they learn from data.
```

---

## 🔧 Customization

To add a new caption style, edit `generate_captions()` in `caption_generator.py`:

```python
style_prompts = {
    "my_style": "Your custom instructions for Grok here.",
    ...
}
```

To add a new tool, add it to the `tools` list and implement the function, then add it to the `handlers` dict in `run_tool()`.
