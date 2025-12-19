# 🎙️ Transcribe Social

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenAI Whisper](https://img.shields.io/badge/Powered%20by-OpenAI%20Whisper-412991.svg)](https://github.com/openai/whisper)

> CLI tool to transcribe social media videos using OpenAI Whisper.

**Supported Platforms:**
YouTube • Instagram • TikTok • Twitter/X • Facebook • Reddit

**Use Cases:**
- Transcribe videos for content repurposing
- Extract text from competitor content
- Create transcripts for accessibility
- Analyze video content at scale

## Features

- Simple CLI interface - paste URL, get transcript
- Supports 6 major social media platforms
- Multi-language support (50+ languages)
- Multiple Whisper models (tiny to turbo)
- Temporary file handling - no clutter
- Runs locally - no data sent to external services

## Installation

### 🎯 Quick Start (Recommended)

**Download the standalone app - no installation needed:**

<table>
<tr>
<td align="center"><strong>Windows</strong></td>
<td align="center"><strong>macOS</strong></td>
<td align="center"><strong>Linux</strong></td>
</tr>
<tr>
<td align="center">
<a href="https://github.com/mrizwan47/transcribe-social/releases/latest/download/transcribe-social-windows.exe">
<img src="https://img.shields.io/badge/Download-Windows-0078D4?style=for-the-badge&logo=windows" alt="Download for Windows"/>
</a>
</td>
<td align="center">
<a href="https://github.com/mrizwan47/transcribe-social/releases/latest/download/transcribe-social.command">
<img src="https://img.shields.io/badge/Download-macOS-000000?style=for-the-badge&logo=apple" alt="Download for macOS"/>
</a>
</td>
<td align="center">
<a href="https://github.com/mrizwan47/transcribe-social/releases/latest/download/install-and-run.sh">
<img src="https://img.shields.io/badge/Download-Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black" alt="Download for Linux"/>
</a>
</td>
</tr>
</table>

**How to run:**
- **Windows:** Double-click `transcribe-social-windows.exe`
- **macOS:** Double-click `transcribe-social.command`
- **Linux:** Double-click `install-and-run.sh` (or run in Terminal)

Everything is bundled - FFmpeg included, no dependencies needed!

---

### 📦 Alternative: Install via pip

For Python developers who prefer pip:

```bash
pip install transcribe-social
```

**Note:** This method requires Python 3.11+ and FFmpeg to be installed separately:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows (using Chocolatey)
choco install ffmpeg
```

Then run:
```bash
transcribe-social
```

## Usage

Start the CLI and paste any video URL:

```bash
$ transcribe-social

🎙️  Social Media Transcriber
Author: Rizwan (riz.codes)

Loading Whisper model 'base'...
✓ Model 'base' loaded successfully

  Model: base | Language: en

Type /help for commands, or paste a URL to transcribe.

URL> https://www.youtube.com/shorts/xyz123
Downloading audio...
Transcribing...

In this video, I'll show you three productivity hacks...
```

### Commands

| Command | Description |
|---------|-------------|
| `/model tiny\|base\|small\|medium\|large\|turbo` | Switch AI model (tiny=fastest, large=most accurate) |
| `/lang <code>` | Change language (en, es, fr, de, zh, ar, hi, ur, etc.) |
| `/status` | Show current settings |
| `/help` | Show help |
| `exit` | Quit |

## Troubleshooting

<details>
<summary><strong>macOS: "Cannot be opened because the developer cannot be verified"?</strong></summary>

This is normal for unsigned executables. To allow it:

1. Right-click `transcribe-social.command` → **Open**
2. Click **"Open"** in the security dialog
3. Or, run in Terminal: `xattr -d com.apple.quarantine transcribe-social.command`

After first run, double-clicking will work normally.

</details>

<details>
<summary><strong>Windows: "Windows protected your PC" warning?</strong></summary>

Click **"More info"** → **"Run anyway"**. This is normal for unsigned executables.

</details>

<details>
<summary><strong>YouTube 403 Forbidden error?</strong></summary>

For pip installations, update yt-dlp:
```bash
python3 -m pip install -U yt-dlp
```

For executables, download the latest release.

</details>

<details>
<summary><strong>Python version error? (pip install only)</strong></summary>

```bash
python3 --version  # Must be 3.11+
brew install python@3.11  # macOS
```
</details>

<details>
<summary><strong>FFmpeg not found? (pip install only)</strong></summary>

```bash
brew install ffmpeg        # macOS
sudo apt install ffmpeg    # Ubuntu/Debian
choco install ffmpeg       # Windows (Chocolatey)
scoop install ffmpeg       # Windows (Scoop)
```

**Note:** Standalone executables include FFmpeg - no separate install needed!
</details>

<details>
<summary><strong>How much disk space do models need?</strong></summary>

Models download automatically on first use:
- **tiny**: ~75MB (fastest, least accurate)
- **base**: ~150MB (default, balanced)
- **small**: ~500MB (good quality)
- **medium/turbo**: ~1.5GB (great quality)
- **large**: ~3GB (best quality)

Cached in `~/.cache/whisper/`
</details>

---

## License

MIT License - See [LICENSE](LICENSE)

## Author

[Rizwan](https://riz.codes/)
