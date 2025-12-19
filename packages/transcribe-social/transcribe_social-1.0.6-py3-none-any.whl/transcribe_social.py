#!/usr/bin/env python3
"""
Transcribe Social - CLI tool for transcribing social media videos
"""

import os
import sys
import tempfile
import subprocess
import re
import warnings
from pathlib import Path
from urllib.parse import urlparse

# Suppress warnings
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL 1.1.1+")
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
warnings.filterwarnings("ignore", category=UserWarning, module="whisper")

try:
    import whisper
    import yt_dlp
except ImportError as e:
    print(f"Error: Missing required package: {e}")
    print("Please install with: pip install openai-whisper yt-dlp")
    sys.exit(1)


class TranscribeSocial:
    def __init__(self):
        self.model = None
        self.model_name = "base"
        self.language = "en"
        self.available_models = ["tiny", "base", "small", "medium", "large", "turbo"]
        
    def load_model(self, model_name):
        """Load Whisper model with progress indication"""
        if model_name not in self.available_models:
            print(f"Error: Invalid model '{model_name}'. Available: {', '.join(self.available_models)}")
            return False
            
        print(f"Loading Whisper model '{model_name}'...")
        try:
            self.model = whisper.load_model(model_name)
            self.model_name = model_name
            print(f"✓ Model '{model_name}' loaded successfully")
            return True
        except Exception as e:
            print(f"Error loading model '{model_name}': {e}")
            return False
    
    def download_audio(self, url):
        """Download audio from URL using yt-dlp"""
        temp_dir = tempfile.mkdtemp()
        audio_file = os.path.join(temp_dir, "audio.%(ext)s")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': audio_file,
            'quiet': True,
            'no_warnings': True,
            # Fix YouTube 403 errors
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                }
            },
        }
        
        try:
            print("Downloading audio...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Find the downloaded file
            audio_path = os.path.join(temp_dir, "audio.mp3")
            if os.path.exists(audio_path):
                return audio_path, temp_dir
            else:
                # Fallback: find any audio file in temp dir
                for file in os.listdir(temp_dir):
                    if file.endswith(('.mp3', '.m4a', '.wav')):
                        return os.path.join(temp_dir, file), temp_dir
                        
            raise FileNotFoundError("No audio file found after download")
            
        except Exception as e:
            # Clean up temp dir on error
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise e
    
    def validate_url(self, url):
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except:
            return False
    
    def transcribe_audio(self, audio_path):
        """Transcribe audio file using loaded Whisper model"""
        if not self.model:
            raise RuntimeError("No model loaded")
            
        print("Transcribing...")
        try:
            result = self.model.transcribe(audio_path, language=self.language)
            return result["text"].strip()
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {e}")
    
    def transcribe_url(self, url):
        """Complete transcription pipeline"""
        # Validate URL
        if not self.validate_url(url):
            raise ValueError("Invalid URL format. Please provide a valid http:// or https:// URL")
        
        temp_dir = None
        try:
            # Download audio
            audio_path, temp_dir = self.download_audio(url)
            
            # Transcribe
            transcript = self.transcribe_audio(audio_path)
            
            # Clean up
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return transcript
            
        except yt_dlp.utils.DownloadError as e:
            # Clean up on error
            if temp_dir:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            
            error_msg = str(e)
            if "403" in error_msg:
                raise RuntimeError("Access denied. The video may be private or region-restricted. Try updating yt-dlp: pip install -U yt-dlp")
            elif "404" in error_msg:
                raise RuntimeError("Video not found. The URL may be invalid or the video has been deleted")
            else:
                raise RuntimeError(f"Download failed: {error_msg}")
                
        except Exception as e:
            # Clean up on error
            if temp_dir:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            raise e
    
    def show_status(self):
        """Display current settings"""
        print(f"  Model: {self.model_name} | Language: {self.language}")
    
    def show_help(self):
        """Display help information"""
        print("Commands:")
        print("  /model <name>   - Set model (tiny, base, small, medium, large, turbo)")
        print("  /lang <code>    - Set language (en, ur, es, fr, de, zh, ar, hi, etc.)")
        print("  /status         - Show current settings")
        print("  /help           - Show this help")
        print("  exit            - Quit")
        print("")
        print("Or just paste a URL to transcribe.")
    
    def run(self):
        """Main interactive loop"""
        print("🎙️  Social Media Transcriber")
        print("Author: Rizwan (riz.codes)")
        print("")
        
        # Load initial model
        if not self.load_model(self.model_name):
            print("Failed to load initial model. Exiting.")
            sys.exit(1)
            
        print("")
        self.show_status()
        print("")
        print("Type /help for commands, or paste a URL to transcribe.")
        print("")
        
        while True:
            try:
                user_input = input("URL> ").strip()
                
                # Handle empty input
                if not user_input:
                    continue
                
                # Handle commands
                if user_input == "/help":
                    self.show_help()
                    continue
                
                if user_input == "/status":
                    self.show_status()
                    continue
                
                # Model command
                model_match = re.match(r'^/model\s+(.+)$', user_input)
                if model_match:
                    new_model = model_match.group(1).strip()
                    if self.load_model(new_model):
                        print(f"Model set to: {new_model}")
                    continue
                
                # Language command
                lang_match = re.match(r'^/lang\s+(.+)$', user_input)
                if lang_match:
                    self.language = lang_match.group(1).strip()
                    print(f"Language set to: {self.language}")
                    continue
                
                # Exit commands
                if user_input.lower() in ["exit", "quit", "q"]:
                    print("Bye!")
                    break
                
                # Treat as URL
                try:
                    transcript = self.transcribe_url(user_input)
                    print("")
                    print(transcript)
                    print("")
                except Exception as e:
                    print(f"Error: {e}")
                    
            except KeyboardInterrupt:
                print("\nBye!")
                break
            except EOFError:
                print("\nBye!")
                break


def main():
    """Entry point"""
    transcriber = TranscribeSocial()
    transcriber.run()


if __name__ == "__main__":
    main()

