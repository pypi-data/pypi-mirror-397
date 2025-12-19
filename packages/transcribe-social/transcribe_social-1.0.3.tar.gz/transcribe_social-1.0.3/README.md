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

**Requirements:** Python 3.11+ and FFmpeg

### 1. Install FFmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows (using Chocolatey)
choco install ffmpeg

# Windows (using Scoop)
scoop install ffmpeg
```

### 2. Install Transcribe Social

```bash
pip install transcribe-social
```

### 3. Run

```bash
transcribe-social
```

**Alternative - Install from source:**
```bash
git clone https://github.com/mrizwan47/transcribe-social.git
cd transcribe-social
pip install .
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
<summary><strong>Python version error?</strong></summary>

```bash
python3 --version  # Must be 3.11+
brew install python@3.11  # macOS
```
</details>

<details>
<summary><strong>YouTube 403 Forbidden error?</strong></summary>

```bash
python3 -m pip install -U yt-dlp
```
</details>

<details>
<summary><strong>FFmpeg not found?</strong></summary>

```bash
brew install ffmpeg        # macOS
sudo apt install ffmpeg    # Ubuntu/Debian
choco install ffmpeg       # Windows (Chocolatey)
scoop install ffmpeg       # Windows (Scoop)
```
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
