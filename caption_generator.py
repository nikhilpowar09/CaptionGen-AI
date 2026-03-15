"""
AI-Powered Video Caption Generator
Groq (llama-3.3-70b-versatile) + OpenAI Whisper
"""
import os, subprocess, shutil
from pathlib import Path
from groq import Groq

MODEL        = "llama-3.3-70b-versatile"
CAPTIONS_DIR = Path("captions_output")
CAPTIONS_DIR.mkdir(exist_ok=True)


def _ffmpeg():
    if shutil.which("ffmpeg"): return "ffmpeg"
    for p in [r"C:\ffmpeg\bin\ffmpeg.exe",
              r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
              r"C:\ProgramData\chocolatey\bin\ffmpeg.exe"]:
        if Path(p).exists(): return p
    return None


def _fmt(s):
    ms=int((s%1)*1000)
    return f"{int(s)//3600:02d}:{(int(s)//60)%60:02d}:{int(s)%60:02d},{ms:03d}"


def step_extract_audio(video_path, log):
    video = Path(video_path)
    if not video.exists():
        return {"error": f"Video not found: {video_path}"}
    ff = _ffmpeg()
    if not ff:
        return {"error": "ffmpeg not found. Install from https://ffmpeg.org and add to PATH."}

    out = CAPTIONS_DIR / f"{video.stem}_audio.wav"
    log(f"  [ffmpeg] Starting audio extraction from: {video.name}")
    log(f"  [ffmpeg] Output: {out}")

    cmd = [ff, "-nostdin", "-y", "-i", str(video),
           "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", str(out)]

    try:
        # Use Popen with pipes so we can read stderr live and detect hangs
        flags = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,   # ← key: no stdin so ffmpeg never waits
            **flags
        )
        # Wait with timeout, reading stderr
        try:
            stdout, stderr = proc.communicate(timeout=300)
        except subprocess.TimeoutExpired:
            proc.kill()
            return {"error": "ffmpeg timed out after 5 min. Try a shorter video."}

        if proc.returncode != 0:
            err_msg = stderr.decode("utf-8", errors="replace")[-600:]
            log(f"  [ffmpeg] ERROR output: {err_msg}")
            return {"error": f"ffmpeg failed (code {proc.returncode}). See log above."}

        if not out.exists() or out.stat().st_size < 1000:
            return {"error": "ffmpeg ran but produced no audio file. Check video has an audio track."}

        size_mb = out.stat().st_size / 1024 / 1024
        log(f"  [ffmpeg] Done! Audio saved → {out.name} ({size_mb:.1f} MB)")
        return {"success": True, "audio_path": str(out)}

    except FileNotFoundError:
        return {"error": f"ffmpeg not found at: {ff}"}


def step_transcribe(audio_path, language, log, whisper_model="base"):
    try:
        import whisper
    except ImportError:
        return {"error": "Run: pip install openai-whisper"}

    audio = Path(audio_path)
    if not audio.exists():
        return {"error": f"Audio file missing: {audio_path}"}

    log(f"  [Whisper] Loading {whisper_model} model...")
    model = whisper.load_model(whisper_model)
    log("  [Whisper] Transcribing — this may take a few minutes for long videos...")

    opts = {"verbose": False, "word_timestamps": True}
    if language: opts["language"] = language

    result = model.transcribe(str(audio), **opts)

    segs = [f"[{_fmt(s['start'])} --> {_fmt(s['end'])}] {s['text'].strip()}"
            for s in result["segments"]]
    lang = result.get("language", "?")
    log(f"  [Whisper] Done — language: {lang}, segments: {len(result['segments'])}")
    return {"success": True, "transcript": "\n".join(segs),
            "language": lang, "segment_count": len(result["segments"])}


def step_generate_srt(transcript, style, log):
    hints = {
        "standard":    "Clean grammar, max 42 chars per line, natural reading speed.",
        "educational": "Precise, define terms, proper punctuation.",
        "cinematic":   "Artistic, preserve pauses, minimal punctuation.",
        "accessible":  "Simple words, short sentences, spell numbers, mark [MUSIC] etc.",
    }
    prompt = (
        "You are a professional caption editor. Convert the raw transcript into a valid SRT file.\n\n"
        f"STYLE: {style.upper()} — {hints.get(style, hints['standard'])}\n\n"
        f"TRANSCRIPT:\n{transcript}\n\n"
        "RULES: Output ONLY valid SRT. No markdown, no code fences.\n"
        "Format: index\\nHH:MM:SS,mmm --> HH:MM:SS,mmm\\ntext (max 2 lines ~42 chars)\\nblank line\n"
        "Fix grammar, remove filler words.\n\nSRT:"
    )

    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        return {"error": "GROQ_API_KEY not set in environment."}

    log("  [Groq] Calling Llama 3.3 to format captions...")
    client = Groq(api_key=key)
    resp = client.chat.completions.create(
        model=MODEL, max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    srt = resp.choices[0].message.content.strip()
    if srt.startswith("```"):
        srt = "\n".join(l for l in srt.splitlines() if not l.startswith("```")).strip()

    count = srt.count("\n\n") + 1
    log(f"  [Groq] Done — {count} caption blocks.")
    return {"success": True, "srt_content": srt, "caption_count": count}


def step_save(srt_content, stem, log):
    name = "".join(c for c in f"{stem}_captions" if c.isalnum() or c in "._- ")
    path = CAPTIONS_DIR / f"{name}.srt"
    path.write_text(srt_content, encoding="utf-8")
    size = f"{path.stat().st_size/1024:.1f} KB"
    log(f"  [Save] SRT written → {path.name} ({size})")
    return {"success": True, "srt_path": str(path), "file_size": size}


def step_burn(video_path, srt_path, stem, log):
    ff  = _ffmpeg()
    vid = Path(video_path)
    srt = Path(srt_path)
    out = CAPTIONS_DIR / f"{stem}_captioned{vid.suffix}"
    srt_esc = str(srt.resolve()).replace("\\", "/").replace(":", "\\:")
    log("  [ffmpeg] Burning captions into video...")
    flags = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {}
    try:
        proc = subprocess.Popen(
            [ff, "-nostdin", "-y", "-i", str(vid),
             "-vf", f"subtitles='{srt_esc}':force_style='FontName=Arial,FontSize=22,"
                    "PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Shadow=1'",
             "-c:a", "copy", str(out)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL, **flags
        )
        _, stderr = proc.communicate(timeout=600)
        if proc.returncode != 0:
            return {"error": stderr.decode("utf-8", errors="replace")[-400:]}
        log(f"  [ffmpeg] Captioned video → {out.name}")
        return {"success": True, "output_video": str(out)}
    except subprocess.TimeoutExpired:
        proc.kill()
        return {"error": "Burn timed out."}


def generate_captions_agent(video_path, style="standard",
                             burn=False, language="", whisper_model="base", log_callback=None):
    def log(msg):
        print(msg, flush=True)
        if log_callback: log_callback(msg)

    video = Path(video_path)
    log("=" * 56)
    log("  AI Caption Agent Starting...")
    log("=" * 56)

    log("\n  ► Tool: extract_audio")
    r1 = step_extract_audio(str(video), log)
    if "error" in r1:
        log(f"  ERROR: {r1['error']}")
        return f"FAILED at extract_audio: {r1['error']}"

    log("\n  ► Tool: transcribe_audio")
    r2 = step_transcribe(r1["audio_path"], language, log, whisper_model=whisper_model)
    if "error" in r2:
        log(f"  ERROR: {r2['error']}")
        return f"FAILED at transcribe_audio: {r2['error']}"

    log("\n  ► Tool: generate_captions")
    r3 = step_generate_srt(r2["transcript"], style, log)
    if "error" in r3:
        log(f"  ERROR: {r3['error']}")
        return f"FAILED at generate_captions: {r3['error']}"

    log("\n  ► Tool: save_captions")
    r4 = step_save(r3["srt_content"], video.stem, log)
    if "error" in r4:
        log(f"  ERROR: {r4['error']}")
        return f"FAILED at save_captions: {r4['error']}"

    burned = ""
    if burn:
        log("\n  ► Tool: burn_captions")
        r5 = step_burn(str(video), r4["srt_path"], video.stem, log)
        burned = r5.get("output_video", "")
        if "error" in r5: log(f"  Burn FAILED: {r5['error']}")

    log("\n" + "=" * 56)
    log("  Agent Complete!")
    log("=" * 56)
    return (f"Done! {r3['caption_count']} captions for '{video.name}'. "
            f"SRT: {r4['srt_path']}" + (f" | Video: {burned}" if burned else ""))


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("video")
    p.add_argument("--style", choices=["standard","educational","cinematic","accessible"], default="standard")
    p.add_argument("--burn", action="store_true")
    p.add_argument("--language", default="")
    a = p.parse_args()
    if not os.environ.get("GROQ_API_KEY"):
        print("Set GROQ_API_KEY first. PowerShell: $env:GROQ_API_KEY='gsk_...'")
        exit(1)
    print(generate_captions_agent(a.video, a.style, a.burn, a.language))