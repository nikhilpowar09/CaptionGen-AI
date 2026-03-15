"""
CaptionAI — Responsive Web UI with live caption preview + demo player
python app.py  →  http://localhost:5000
"""
import os, time, threading, traceback, sys
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024 * 1024
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
jobs: dict = {}

HTML = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>CaptionAI</title>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
[data-theme=dark]{
  --bg:#08080e;--s1:#0e0e18;--s2:#14141f;--s3:#1a1a28;
  --b1:#ffffff0d;--b2:#ffffff1a;--b3:#ffffff28;
  --ac:#7c6af7;--ac2:#a78bfa;--acb:#7c6af715;
  --t1:#ededf4;--t2:#8888a8;--t3:#55556a;
  --g:#34d399;--gb:#34d39912;--r:#f87171;--rb:#f8717112;--y:#fbbf24;
  --sh:0 8px 32px #00000055;--sh2:0 2px 8px #00000040;
}
[data-theme=light]{
  --bg:#eef0f8;--s1:#ffffff;--s2:#f4f4fb;--s3:#e8e8f5;
  --b1:#00000008;--b2:#00000012;--b3:#0000001e;
  --ac:#6355e0;--ac2:#8b5cf6;--acb:#6355e010;
  --t1:#181828;--t2:#4a4a68;--t3:#8888a8;
  --g:#059669;--gb:#05966910;--r:#dc2626;--rb:#dc262610;--y:#b45309;
  --sh:0 8px 32px #0000001a;--sh2:0 2px 8px #00000010;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:'Plus Jakarta Sans',sans-serif;background:var(--bg);color:var(--t1);min-height:100vh;transition:background .25s,color .25s;line-height:1.5}

/* HEADER */
.hdr{position:sticky;top:0;z-index:200;background:var(--s1);border-bottom:1px solid var(--b2);padding:.8rem 1.5rem;display:flex;align-items:center;gap:.8rem;backdrop-filter:blur(16px)}
.logo{width:32px;height:32px;background:linear-gradient(135deg,var(--ac),var(--ac2));border-radius:9px;display:grid;place-items:center;font-size:16px;flex-shrink:0}
.brand{font-size:.95rem;font-weight:700;letter-spacing:-.02em}
.brand-sub{font-size:.72rem;color:var(--t3);margin-left:4px}
.hdr-r{margin-left:auto;display:flex;align-items:center;gap:.6rem}
.free-badge{background:var(--gb);color:var(--g);border:1px solid var(--g);padding:2px 9px;border-radius:20px;font-size:.68rem;font-weight:700}
.icon-btn{width:34px;height:34px;border-radius:50%;border:1px solid var(--b2);background:var(--s2);cursor:pointer;display:grid;place-items:center;font-size:14px;color:var(--t2);transition:.2s}
.icon-btn:hover{border-color:var(--ac);background:var(--acb)}

/* LAYOUT */
.page{max-width:1100px;margin:0 auto;padding:1.5rem 1rem 4rem}
.main-grid{display:grid;grid-template-columns:1fr 340px;gap:1.25rem;align-items:start}
@media(max-width:860px){.main-grid{grid-template-columns:1fr}}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:.9rem}
@media(max-width:560px){.two-col{grid-template-columns:1fr}}

/* CARDS */
.card{background:var(--s1);border:1px solid var(--b1);border-radius:16px;padding:1.35rem;margin-bottom:1.1rem;transition:background .25s,border .25s}
.card-title{font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--t3);margin-bottom:1rem;display:flex;align-items:center;gap:.5rem}
.step-num{width:18px;height:18px;background:var(--acb);color:var(--ac2);border-radius:5px;display:grid;place-items:center;font-size:.62rem;font-weight:700;flex-shrink:0}

/* DROP ZONE */
.dz{border:2px dashed var(--b3);border-radius:12px;padding:2.2rem 1rem;text-align:center;cursor:pointer;transition:.25s;position:relative;background:var(--s2)}
.dz:hover,.dz.over{border-color:var(--ac);background:var(--acb)}
.dz input{position:absolute;inset:0;opacity:0;cursor:pointer;width:100%;height:100%}
.dz-emoji{font-size:2.2rem;display:block;margin-bottom:.5rem}
.dz h3{font-size:.88rem;font-weight:600}
.dz p{font-size:.75rem;color:var(--t3);margin-top:.25rem}
.file-pill{display:none;align-items:center;gap:.65rem;padding:.65rem .9rem;background:var(--s2);border-radius:10px;margin-top:.8rem;border:1px solid var(--b2)}
.file-pill.show{display:flex}
.f-ext{background:var(--acb);color:var(--ac2);padding:2px 9px;border-radius:5px;font-size:.68rem;font-weight:700;font-family:'JetBrains Mono',monospace;flex-shrink:0}
.f-name{font-size:.8rem;font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1;min-width:0}
.f-size{font-size:.72rem;color:var(--t3);flex-shrink:0}

/* STYLE SELECTOR */
.style-grid{display:grid;grid-template-columns:1fr 1fr;gap:.6rem}
@media(max-width:400px){.style-grid{grid-template-columns:1fr}}
.sc{padding:.8rem;border:1.5px solid var(--b2);border-radius:10px;cursor:pointer;transition:.2s;display:flex;align-items:flex-start;gap:.55rem}
.sc:hover{border-color:var(--ac2);background:var(--acb)}
.sc.on{border-color:var(--ac);background:var(--acb)}
.sc-icon{font-size:1.25rem;flex-shrink:0;margin-top:1px}
.sc-name{font-size:.8rem;font-weight:600}
.sc-desc{font-size:.7rem;color:var(--t3);margin-top:1px;line-height:1.35}

/* CONTROLS */
.ctrl-lbl{display:block;font-size:.7rem;font-weight:600;color:var(--t2);margin-bottom:.4rem;text-transform:uppercase;letter-spacing:.06em}
select{width:100%;background:var(--s2);border:1px solid var(--b2);color:var(--t1);padding:.58rem .8rem;border-radius:9px;font-family:inherit;font-size:.83rem;outline:none;transition:.2s;cursor:pointer}
select:focus{border-color:var(--ac);box-shadow:0 0 0 3px var(--acb)}
select option{background:var(--s2)}
.tog{display:flex;align-items:center;gap:.65rem;padding:.75rem .9rem;background:var(--s2);border-radius:10px;cursor:pointer;border:1.5px solid var(--b2);transition:.2s;user-select:none}
.tog:hover{border-color:var(--ac2)}.tog.on{border-color:var(--ac);background:var(--acb)}
.tog input{accent-color:var(--ac);width:15px;height:15px;flex-shrink:0}
.tog-lbl{font-size:.82rem;font-weight:500;flex:1}
.tog-hint{font-size:.7rem;color:var(--t3)}

/* GEN BUTTON */
.gen-btn{width:100%;padding:.95rem;background:linear-gradient(135deg,var(--ac),#9b5cf6);border:none;border-radius:13px;color:#fff;font-family:inherit;font-size:.92rem;font-weight:700;cursor:pointer;transition:.25s;display:flex;align-items:center;justify-content:center;gap:.5rem;box-shadow:0 4px 20px #7c6af738;letter-spacing:-.01em}
.gen-btn:hover:not(:disabled){transform:translateY(-2px);box-shadow:0 8px 28px #7c6af750}
.gen-btn:disabled{opacity:.4;cursor:not-allowed;transform:none;box-shadow:none}

/* PROGRESS */
.prog{display:none}.prog.show{display:block}
.steps-wrap{display:flex;gap:4px;margin-bottom:.75rem}
.s-item{flex:1}
.s-bar{height:3px;border-radius:2px;background:var(--b3);transition:.4s;margin-bottom:3px}
.s-bar.done{background:var(--g)}.s-bar.act{background:var(--ac);animation:pulse 1.1s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}
.s-lbl{font-size:.6rem;color:var(--t3);text-align:center;font-weight:500}
.s-lbl.done{color:var(--g)}.s-lbl.act{color:var(--ac2)}
.timer{font-size:.72rem;color:var(--t3);text-align:right;margin-bottom:.6rem;font-family:'JetBrains Mono',monospace}
.log{background:var(--bg);border:1px solid var(--b2);border-radius:11px;padding:.9rem 1rem;font-family:'JetBrains Mono',monospace;font-size:.73rem;color:var(--t2);height:200px;overflow-y:auto;line-height:1.7}
.log::-webkit-scrollbar{width:3px}.log::-webkit-scrollbar-thumb{background:var(--b3);border-radius:2px}
.ll{margin-bottom:1px}.lt{color:var(--ac2);font-weight:500}.lf{color:#60a5fa}.ls{color:var(--g)}.le{color:var(--r)}.lw{color:var(--y)}

/* RESULTS */
.res{display:none}.res.show{display:block}
.stats-row{display:grid;grid-template-columns:repeat(3,1fr);gap:.65rem;margin-bottom:1rem}
.stat{background:var(--s2);border:1px solid var(--b1);border-radius:10px;padding:.7rem;text-align:center}
.stat-v{font-size:1.15rem;font-weight:700;color:var(--ac2);font-family:'JetBrains Mono',monospace}
.stat-l{font-size:.63rem;color:var(--t3);margin-top:2px;text-transform:uppercase;letter-spacing:.06em}
.tabs{display:flex;gap:.4rem;margin-bottom:.9rem;flex-wrap:wrap}
.tab{padding:.38rem .9rem;border-radius:7px;border:1px solid var(--b2);font-size:.76rem;font-weight:600;cursor:pointer;background:var(--s2);color:var(--t2);transition:.2s}
.tab.on{background:var(--acb);border-color:var(--ac);color:var(--ac2)}

/* VIDEO PLAYER with live captions */
.player-wrap{position:relative;background:#000;border-radius:12px;overflow:hidden;aspect-ratio:16/9}
.player-wrap video{width:100%;height:100%;display:block}
.live-caption{position:absolute;bottom:12px;left:50%;transform:translateX(-50%);width:92%;text-align:center;pointer-events:none}
.live-caption span{display:inline-block;background:rgba(0,0,0,.82);color:#fff;padding:5px 14px;border-radius:6px;font-size:clamp(.75rem,2vw,1rem);font-weight:500;line-height:1.45;max-width:100%;backdrop-filter:blur(4px);border:1px solid rgba(255,255,255,.1)}
.player-controls{display:flex;align-items:center;gap:.6rem;padding:.6rem .9rem;background:var(--s2);border-radius:0 0 12px 12px;flex-wrap:wrap}
.pc-btn{padding:.38rem .8rem;background:var(--acb);border:1px solid var(--ac);color:var(--ac2);border-radius:7px;font-family:inherit;font-size:.76rem;font-weight:600;cursor:pointer;transition:.2s}
.pc-btn:hover{background:var(--ac);color:#fff}
.pc-time{font-size:.72rem;color:var(--t3);font-family:'JetBrains Mono',monospace;flex:1;text-align:right}

/* SRT VIEWER */
.srt-view{background:var(--bg);border:1px solid var(--b2);border-radius:11px;padding:1rem;font-family:'JetBrains Mono',monospace;font-size:.73rem;max-height:320px;overflow-y:auto;line-height:1.8}
.srt-view::-webkit-scrollbar{width:3px}.srt-view::-webkit-scrollbar-thumb{background:var(--b3);border-radius:2px}
.srt-idx{color:var(--t3)}.srt-ts{color:var(--ac2)}.srt-txt{color:var(--t1)}.srt-sep{color:var(--b3)}

/* FILE CARDS */
.file-card{display:flex;align-items:center;gap:.9rem;padding:.9rem 1rem;background:var(--s2);border-radius:11px;margin-bottom:.65rem;border:1px solid var(--b1);transition:.2s}
.file-card:hover{border-color:var(--b2)}
.f-icon{font-size:1.8rem;flex-shrink:0}
.f-info{flex:1;min-width:0}
.f-nm{font-size:.8rem;font-weight:600;font-family:'JetBrains Mono',monospace;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.f-mt{font-size:.7rem;color:var(--t3);margin-top:2px}
.dl-btn{padding:.45rem 1rem;background:var(--s1);border:1px solid var(--b3);color:var(--ac2);border-radius:8px;font-family:inherit;font-size:.76rem;font-weight:600;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;gap:.3rem;white-space:nowrap;flex-shrink:0;transition:.2s}
.dl-btn:hover{background:var(--acb);border-color:var(--ac)}
.dl-all{width:100%;padding:.75rem;background:linear-gradient(135deg,var(--ac),#9b5cf6);border:none;border-radius:10px;color:#fff;font-family:inherit;font-size:.85rem;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:.4rem;margin-top:.5rem;transition:.2s}
.dl-all:hover{opacity:.88;transform:translateY(-1px)}

/* SIDEBAR */
.sidebar-card{background:var(--s1);border:1px solid var(--b1);border-radius:14px;padding:1.1rem;margin-bottom:1rem}
.tip{display:flex;gap:.55rem;font-size:.76rem;color:var(--t2);line-height:1.45;margin-bottom:.75rem}
.tip:last-child{margin-bottom:0}
.tip-i{flex-shrink:0;font-size:.9rem;margin-top:1px}
.flow-step{display:flex;align-items:center;gap:.55rem;font-size:.76rem;color:var(--t2);margin-bottom:.6rem}
.flow-n{width:20px;height:20px;background:var(--acb);color:var(--ac2);border-radius:5px;display:grid;place-items:center;font-size:.62rem;font-weight:700;flex-shrink:0}

/* TOAST */
.toast{position:fixed;bottom:1.25rem;right:1.25rem;z-index:999;background:var(--s1);border:1px solid var(--b3);border-radius:10px;padding:.7rem 1rem;font-size:.8rem;display:flex;align-items:center;gap:.5rem;box-shadow:var(--sh);transform:translateY(70px);opacity:0;transition:.3s cubic-bezier(.34,1.56,.64,1);pointer-events:none;max-width:calc(100vw - 2.5rem)}
.toast.show{transform:translateY(0);opacity:1}
.toast.ok{border-color:var(--g);color:var(--g)}.toast.err{border-color:var(--r);color:var(--r)}

@media(max-width:480px){
  .hdr{padding:.7rem 1rem}
  .page{padding:1rem .75rem 3rem}
  .card{padding:1rem}
  .stats-row{grid-template-columns:repeat(3,1fr)}
  .stat-v{font-size:.95rem}
}
</style>
</head>
<body>

<header class="hdr">
  <div class="logo">🎬</div>
  <span class="brand">CaptionAI<span class="brand-sub">Groq + Whisper</span></span>
  <div class="hdr-r">
    <span class="free-badge">FREE</span>
    <button class="icon-btn" id="themeBtn" title="Toggle theme">🌙</button>
  </div>
</header>

<div class="toast" id="toast"></div>

<div class="page">
<div class="main-grid">

<!-- LEFT COLUMN -->
<div>

<!-- 1. Upload -->
<div class="card">
  <div class="card-title"><span class="step-num">1</span> Upload Video</div>
  <div class="dz" id="dz">
    <input type="file" id="fi" accept="video/*"/>
    <span class="dz-emoji">📹</span>
    <h3>Drop video here or tap to browse</h3>
    <p>MP4 · MKV · AVI · MOV · WEBM · up to 2 GB</p>
  </div>
  <div class="file-pill" id="fpill">
    <span class="f-ext" id="fext">MP4</span>
    <span class="f-name" id="fname">—</span>
    <span class="f-size" id="fsize">—</span>
  </div>
</div>

<!-- 2. Style -->
<div class="card">
  <div class="card-title"><span class="step-num">2</span> Caption Style</div>
  <div class="style-grid">
    <div class="sc on" data-s="standard"><span class="sc-icon">📝</span><div><div class="sc-name">Standard</div><div class="sc-desc">Clean grammar, natural reading speed</div></div></div>
    <div class="sc" data-s="educational"><span class="sc-icon">🎓</span><div><div class="sc-name">Educational</div><div class="sc-desc">Precise, defines terms, proper punctuation</div></div></div>
    <div class="sc" data-s="cinematic"><span class="sc-icon">🎞️</span><div><div class="sc-name">Cinematic</div><div class="sc-desc">Artistic phrasing, pauses preserved</div></div></div>
    <div class="sc" data-s="accessible"><span class="sc-icon">♿</span><div><div class="sc-name">Accessible</div><div class="sc-desc">Simple words, marks [MUSIC], [APPLAUSE]</div></div></div>
  </div>
</div>

<!-- 3. Options -->
<div class="card">
  <div class="card-title"><span class="step-num">3</span> Options</div>
  <div class="two-col" style="margin-bottom:.85rem">
    <div>
      <label class="ctrl-lbl">Language</label>
      <select id="lang">
        <option value="">🌍 Auto-detect</option>
        <option value="en">🇺🇸 English</option>
        <option value="hi">🇮🇳 Hindi</option>
        <option value="es">🇪🇸 Spanish</option>
        <option value="fr">🇫🇷 French</option>
        <option value="de">🇩🇪 German</option>
        <option value="zh">🇨🇳 Chinese</option>
        <option value="ja">🇯🇵 Japanese</option>
        <option value="ar">🇸🇦 Arabic</option>
        <option value="pt">🇧🇷 Portuguese</option>
        <option value="ru">🇷🇺 Russian</option>
        <option value="ko">🇰🇷 Korean</option>
      </select>
    </div>
    <div>
      <label class="ctrl-lbl">Whisper Model</label>
      <select id="wm">
        <option value="base">⚡ Base — fastest</option>
        <option value="small">⚖️ Small — balanced</option>
        <option value="medium">🎯 Medium — accurate</option>
      </select>
    </div>
  </div>
  <label class="tog" id="burnTog">
    <input type="checkbox" id="burnCb"/>
    <span class="tog-lbl">🔥 Burn captions into video</span>
    <span class="tog-hint">Creates new MP4</span>
  </label>
</div>

<button class="gen-btn" id="genBtn" disabled>
  <span id="genIco">✨</span><span id="genTxt">Generate Captions</span>
</button>

<!-- Progress -->
<div class="prog card" id="progCard" style="margin-top:1rem">
  <div class="card-title">⚙️ Processing</div>
  <div class="steps-wrap">
    <div class="s-item"><div class="s-bar" id="sb1"></div><div class="s-lbl" id="sl1">Extract</div></div>
    <div class="s-item"><div class="s-bar" id="sb2"></div><div class="s-lbl" id="sl2">Transcribe</div></div>
    <div class="s-item"><div class="s-bar" id="sb3"></div><div class="s-lbl" id="sl3">AI Format</div></div>
    <div class="s-item"><div class="s-bar" id="sb4"></div><div class="s-lbl" id="sl4">Save</div></div>
  </div>
  <div class="timer" id="timer">00:00</div>
  <div class="log" id="logBox"></div>
</div>

<!-- Results -->
<div class="res card" id="resCard" style="margin-top:1rem">
  <div class="card-title">✅ Results</div>
  <div class="stats-row" id="statsRow"></div>

  <div class="tabs">
    <div class="tab on" onclick="switchTab(this,'demo')">▶ Live Demo</div>
    <div class="tab" onclick="switchTab(this,'preview')">📄 SRT Preview</div>
    <div class="tab" onclick="switchTab(this,'files')">📁 Download</div>
  </div>

  <!-- Demo player tab -->
  <div id="tabDemo">
    <div class="player-wrap" id="playerWrap">
      <video id="vidPlayer" controls></video>
      <div class="live-caption" id="liveCaption"><span id="capText"></span></div>
    </div>
    <div class="player-controls">
      <button class="pc-btn" onclick="toggleCC()">CC: <span id="ccState">ON</span></button>
      <button class="pc-btn" onclick="jumpTo(0)">⏮ Start</button>
      <div class="pc-time" id="pcTime">00:00 / 00:00</div>
    </div>
    <p style="font-size:.72rem;color:var(--t3);margin-top:.6rem;text-align:center">Live captions update as the video plays — download when you're happy ✓</p>
  </div>

  <!-- SRT preview tab -->
  <div id="tabPreview" style="display:none">
    <div class="srt-view" id="srtView"></div>
  </div>

  <!-- Download tab -->
  <div id="tabFiles" style="display:none">
    <div id="fileList"></div>
    <button class="dl-all" id="dlAllBtn" style="display:none" onclick="downloadAll()">⬇ Download All Files</button>
  </div>
</div>

</div><!-- /left -->

<!-- SIDEBAR -->
<div>
  <div class="sidebar-card">
    <div class="card-title" style="margin-bottom:.85rem">💡 Tips</div>
    <div class="tip"><span class="tip-i">⏱️</span><span>30-min video = ~3-5 min Whisper time. Timer shows progress.</span></div>
    <div class="tip"><span class="tip-i">🎯</span><span>Set language manually for faster, more accurate results</span></div>
    <div class="tip"><span class="tip-i">🎬</span><span>Use the <b>Live Demo</b> tab to watch captions synced to your video</span></div>
    <div class="tip"><span class="tip-i">🔥</span><span>Burn mode permanently embeds captions — great for social media</span></div>
    <div class="tip"><span class="tip-i">📂</span><span>SRT files work in VLC, YouTube, Premiere, DaVinci Resolve</span></div>
  </div>

  <div class="sidebar-card">
    <div class="card-title" style="margin-bottom:.85rem">🔄 Pipeline</div>
    <div class="flow-step"><span class="flow-n">1</span> ffmpeg extracts audio track</div>
    <div class="flow-step"><span class="flow-n">2</span> Whisper AI transcribes speech</div>
    <div class="flow-step"><span class="flow-n">3</span> Groq Llama 3.3 formats SRT</div>
    <div class="flow-step"><span class="flow-n">4</span> Download SRT or burned MP4</div>
  </div>

  <div class="sidebar-card" id="prevCard" style="display:none">
    <div class="card-title" style="margin-bottom:.85rem">🕓 Last Job</div>
    <div id="prevInfo" style="font-size:.76rem;color:var(--t2)"></div>
  </div>
</div>

</div><!-- /main-grid -->
</div><!-- /page -->

<script>
// ── Theme ──────────────────────────────────────────────────────
let dark = true;
document.getElementById('themeBtn').onclick = () => {
  dark = !dark;
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
  document.getElementById('themeBtn').textContent = dark ? '🌙' : '☀️';
};

// ── State ──────────────────────────────────────────────────────
let selStyle = 'standard', upPath = null, pollId = null;
let lastLogLen = 0, startTs = null, timerInt = null;
let captions = [], ccOn = true;

// ── Style cards ────────────────────────────────────────────────
document.querySelectorAll('.sc').forEach(c => {
  c.onclick = () => { document.querySelectorAll('.sc').forEach(x => x.classList.remove('on')); c.classList.add('on'); selStyle = c.dataset.s; };
});

// ── Burn toggle ────────────────────────────────────────────────
document.getElementById('burnTog').onclick = function(e) {
  if (e.target.type === 'checkbox') return;
  const cb = document.getElementById('burnCb'); cb.checked = !cb.checked;
  this.classList.toggle('on', cb.checked);
};

// ── File drop ──────────────────────────────────────────────────
const dz = document.getElementById('dz');
document.getElementById('fi').onchange = handleFile;
dz.ondragover = e => { e.preventDefault(); dz.classList.add('over'); };
dz.ondragleave = () => dz.classList.remove('over');
dz.ondrop = e => {
  e.preventDefault(); dz.classList.remove('over');
  if (e.dataTransfer.files[0]) { document.getElementById('fi').files = e.dataTransfer.files; handleFile({ target: document.getElementById('fi') }); }
};

function handleFile(e) {
  const f = e.target.files[0]; if (!f) return;
  document.getElementById('fext').textContent = f.name.split('.').pop().toUpperCase();
  document.getElementById('fname').textContent = f.name;
  document.getElementById('fsize').textContent = (f.size / 1024 / 1024).toFixed(1) + ' MB';
  document.getElementById('fpill').classList.add('show');
  document.getElementById('genBtn').disabled = false;
  const fd = new FormData(); fd.append('video', f);
  fetch('/upload', { method: 'POST', body: fd }).then(r => r.json()).then(d => { upPath = d.path; });
}

// ── Generate ───────────────────────────────────────────────────
document.getElementById('genBtn').onclick = async () => {
  if (!upPath) return;
  document.getElementById('genBtn').disabled = true;
  document.getElementById('genIco').textContent = '⏳';
  document.getElementById('genTxt').textContent = 'Processing...';
  document.getElementById('progCard').classList.add('show');
  document.getElementById('resCard').classList.remove('show');
  document.getElementById('logBox').innerHTML = '';
  lastLogLen = 0; resetSteps();
  startTs = Date.now();
  timerInt = setInterval(() => {
    const s = Math.floor((Date.now() - startTs) / 1000);
    document.getElementById('timer').textContent = 'Elapsed: ' + pad(~~(s/60)) + ':' + pad(s%60);
  }, 1000);

  const r = await fetch('/generate', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ video_path: upPath, style: selStyle,
      burn: document.getElementById('burnCb').checked,
      language: document.getElementById('lang').value,
      whisper_model: document.getElementById('wm').value })
  });
  const { job_id } = await r.json();
  pollId = setInterval(() => doPoll(job_id), 700);
};

function doPoll(id) {
  fetch('/job/' + id).then(r => r.json()).then(j => {
    appendLogs(j.logs || []);
    setStep(j.step || 0);
    if (j.status === 'done') {
      clearInterval(pollId); clearInterval(timerInt);
      allStepsDone(); showResults(j); resetBtn();
      toast('✅ Captions ready!', 'ok');
      savePrev(j);
    } else if (j.status === 'error') {
      clearInterval(pollId); clearInterval(timerInt);
      appendLogs((j.error || '').split('\n').filter(Boolean), true);
      resetBtn(); toast('❌ Error — see log below', 'err');
    }
  });
}

// ── Logs ───────────────────────────────────────────────────────
function appendLogs(logs, isErr) {
  const box = document.getElementById('logBox');
  for (let i = lastLogLen; i < logs.length; i++) {
    const l = logs[i];
    const c = l.includes('► Tool') ? 'lt' :
      (l.includes('[ffmpeg]') || l.includes('[Whisper]') || l.includes('[Groq]') || l.includes('[Save]') || l.includes('[Info]')) ? 'lf' :
      (l.includes('Done') || l.includes('Complete') || l.includes('written') || l.includes('saved')) ? 'ls' :
      (l.includes('ERROR') || l.includes('error') || l.includes('FAILED') || isErr) ? 'le' : '';
    box.innerHTML += '<div class="ll ' + c + '">' + esc(l) + '</div>';
  }
  box.scrollTop = box.scrollHeight;
  lastLogLen = logs.length;
}

// ── Steps ──────────────────────────────────────────────────────
const slbls = ['Extract','Transcribe','AI Format','Save'];
function resetSteps() {
  for (let i=1;i<=4;i++){document.getElementById('sb'+i).className='s-bar';document.getElementById('sl'+i).className='s-lbl';document.getElementById('sl'+i).textContent=slbls[i-1];}
}
function setStep(n) {
  for (let i=1;i<=4;i++){
    const b=document.getElementById('sb'+i),l=document.getElementById('sl'+i);
    if(i<n){b.className='s-bar done';l.className='s-lbl done';}
    else if(i===n){b.className='s-bar act';l.className='s-lbl act';}
    else{b.className='s-bar';l.className='s-lbl';}
  }
}
function allStepsDone(){for(let i=1;i<=4;i++){document.getElementById('sb'+i).className='s-bar done';document.getElementById('sl'+i).className='s-lbl done';}}
function resetBtn(){
  document.getElementById('genBtn').disabled=false;
  document.getElementById('genIco').textContent='✨';
  document.getElementById('genTxt').textContent='Generate Captions';
}

// ── Results ────────────────────────────────────────────────────
function showResults(j) {
  document.getElementById('resCard').classList.add('show');

  const elapsed = Math.floor((Date.now() - startTs) / 1000);
  document.getElementById('statsRow').innerHTML =
    stat(j.caption_count || '—', 'Captions') +
    stat((j.output_files||[]).length, 'Files') +
    stat(pad(~~(elapsed/60))+':'+pad(elapsed%60), 'Time');

  // Parse SRT into caption array for live player
  captions = parseSRT(j.srt_content || '');

  // Set up video player with the uploaded video
  const vid = document.getElementById('vidPlayer');
  vid.src = '/serve_upload/' + encodeURIComponent(upPath.split(/[/\\]/).pop());
  vid.ontimeupdate = syncCaption;
  vid.ondurationchange = () => {
    document.getElementById('pcTime').textContent = '00:00 / ' + fmtTime(vid.duration);
  };

  // SRT preview with syntax highlight
  const srtHtml = (j.srt_content || '').split('\n\n').slice(0, 40).map(block => {
    const lines = block.split('\n');
    if (lines.length < 2) return '';
    return '<div style="margin-bottom:.6rem">' +
      '<span class="srt-idx">' + esc(lines[0]) + '</span>\n' +
      (lines[1] ? '<span class="srt-ts">' + esc(lines[1]) + '</span>\n' : '') +
      lines.slice(2).map(l => '<span class="srt-txt">' + esc(l) + '</span>').join('\n') +
      '\n</div>';
  }).join('');
  document.getElementById('srtView').innerHTML = srtHtml || '<span style="color:var(--t3)">No SRT content</span>';

  // File list
  const srts = (j.output_files||[]).filter(f=>f.endsWith('.srt'));
  const mp4s = (j.output_files||[]).filter(f=>!f.endsWith('.srt'));
  document.getElementById('fileList').innerHTML = [...srts,...mp4s].map(f => {
    const n = f.split(/[/\\]/).pop();
    const isSrt = f.endsWith('.srt');
    return '<div class="file-card">' +
      '<span class="f-icon">' + (isSrt ? '📄' : '🎬') + '</span>' +
      '<div class="f-info"><div class="f-nm">' + esc(n) + '</div>' +
      '<div class="f-mt">' + (isSrt ? 'SRT — VLC, YouTube, Premiere, DaVinci' : 'MP4 with burned-in captions') + '</div></div>' +
      '<a class="dl-btn" href="/download/' + encodeURIComponent(n) + '" download>⬇ Download</a>' +
      '</div>';
  }).join('');
  if (j.output_files && j.output_files.length > 1) document.getElementById('dlAllBtn').style.display='';

  // Switch to demo tab
  switchTab(document.querySelector('.tab'), 'demo');
}

function stat(v, l) { return '<div class="stat"><div class="stat-v">' + v + '</div><div class="stat-l">' + l + '</div></div>'; }

// ── Tab switching ──────────────────────────────────────────────
function switchTab(el, id) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('on'));
  el.classList.add('on');
  ['tabDemo','tabPreview','tabFiles'].forEach(t => {
    document.getElementById(t).style.display = t === 'tab' + id.charAt(0).toUpperCase() + id.slice(1) ? '' : 'none';
  });
}

// ── Live caption player ────────────────────────────────────────
function parseSRT(srt) {
  const blocks = srt.split('\n\n');
  return blocks.map(b => {
    const lines = b.trim().split('\n');
    if (lines.length < 3) return null;
    const ts = lines[1] || '';
    const m = ts.match(/(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)/);
    if (!m) return null;
    const start = +m[1]*3600 + +m[2]*60 + +m[3] + +m[4]/1000;
    const end   = +m[5]*3600 + +m[6]*60 + +m[7] + +m[8]/1000;
    const text  = lines.slice(2).join(' ');
    return { start, end, text };
  }).filter(Boolean);
}

function syncCaption() {
  const vid = document.getElementById('vidPlayer');
  const t = vid.currentTime;
  document.getElementById('pcTime').textContent = fmtTime(t) + ' / ' + fmtTime(vid.duration || 0);
  if (!ccOn) { document.getElementById('capText').textContent = ''; return; }
  const cap = captions.find(c => t >= c.start && t <= c.end);
  document.getElementById('capText').textContent = cap ? cap.text : '';
}

function toggleCC() {
  ccOn = !ccOn;
  document.getElementById('ccState').textContent = ccOn ? 'ON' : 'OFF';
  if (!ccOn) document.getElementById('capText').textContent = '';
}
function jumpTo(t) { document.getElementById('vidPlayer').currentTime = t; }

// ── Download all ───────────────────────────────────────────────
function downloadAll() {
  document.querySelectorAll('#fileList .dl-btn').forEach((a, i) => {
    setTimeout(() => { const tmp = document.createElement('a'); tmp.href = a.href; tmp.download = ''; tmp.click(); }, i * 600);
  });
}

// ── Prev job ───────────────────────────────────────────────────
function savePrev(j) {
  const card = document.getElementById('prevCard');
  card.style.display = '';
  document.getElementById('prevInfo').innerHTML = (j.output_files||[]).map(f => {
    const n = f.split(/[/\\]/).pop();
    return '<a class="dl-btn" style="margin-bottom:.4rem;display:inline-flex" href="/download/' + encodeURIComponent(n) + '" download>⬇ ' + esc(n) + '</a>';
  }).join('<br>');
}

// ── Helpers ────────────────────────────────────────────────────
let toastTmr;
function toast(msg, type) {
  const el = document.getElementById('toast');
  el.textContent = msg; el.className = 'toast show ' + type;
  clearTimeout(toastTmr); toastTmr = setTimeout(() => el.className = 'toast', 3500);
}
function fmtTime(s) { s = s || 0; return pad(~~(s/60)) + ':' + pad(~~(s%60)); }
function pad(n) { return String(n).padStart(2,'0'); }
function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
</script>
</body>
</html>"""

@app.route("/")
def index(): return HTML

@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("video")
    if not f: return jsonify({"error":"no file"}),400
    p = UPLOAD_DIR / f.filename
    f.save(p)
    return jsonify({"path": str(p)})

@app.route("/serve_upload/<filename>")
def serve_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)

@app.route("/download/<filename>")
def download(filename):
    import caption_generator as cg
    return send_from_directory(cg.CAPTIONS_DIR, filename, as_attachment=True)

@app.route("/generate", methods=["POST"])
def generate():
    data   = request.json
    job_id = f"job_{int(time.time()*1000)}"
    job    = {"status":"running","logs":[],"step":0}
    jobs[job_id] = job

    def run():
        def log(msg):
            s = str(msg); print(s, flush=True); job["logs"].append(s)
            if   "► Tool: extract_audio"     in s: job["step"]=1
            elif "► Tool: transcribe_audio"  in s: job["step"]=2
            elif "► Tool: generate_captions" in s: job["step"]=3
            elif "► Tool: save_captions"     in s: job["step"]=4
        try:
            if "caption_generator" in sys.modules: del sys.modules["caption_generator"]
            import caption_generator as cg
            log(f"  [Info] Video   : {Path(data['video_path']).name}")
            log(f"  [Info] Style   : {data.get('style','standard')}")
            log(f"  [Info] Model   : whisper-{data.get('whisper_model','base')}")
            log(f"  [Info] Language: {data.get('language','auto') or 'auto-detect'}")

            summary = cg.generate_captions_agent(
                video_path    = data["video_path"],
                style         = data.get("style","standard"),
                burn          = data.get("burn",False),
                language      = data.get("language",""),
                whisper_model = data.get("whisper_model","base"),
                log_callback  = log,
            )
            stem  = Path(data["video_path"]).stem
            files = [f for f in cg.CAPTIONS_DIR.glob(f"{stem}*") if f.suffix!=".wav"]
            srt_content = ""
            count = 0
            srts = [f for f in files if f.suffix==".srt"]
            if srts:
                srt_content = srts[0].read_text("utf-8")
                count = srt_content.count("\n\n") + 1
            job.update({"status":"done","step":4,
                        "output_files":[str(f) for f in files],
                        "srt_content": srt_content,
                        "caption_count": count, "summary": summary})
        except Exception:
            err = traceback.format_exc(); print(err,flush=True)
            job.update({"status":"error","error":err})

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"job_id": job_id})

@app.route("/job/<job_id>")
def job_status(job_id):
    return jsonify(jobs.get(job_id,{"status":"not_found"}))

if __name__=="__main__":
    if not os.environ.get("GROQ_API_KEY"):
        print("⚠  Set GROQ_API_KEY first!\n   PowerShell: $env:GROQ_API_KEY='gsk_...'")
    print("\n🎬 CaptionAI  →  http://localhost:5000\n")
    app.run(debug=False, port=5000, threaded=True)