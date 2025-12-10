import os
import sys
import subprocess
import json
import shutil
import re
import threading
import time

# --- 1. 自動依賴檢查與安裝 (在 import 其他第三方庫之前) ---
def install(package):
    print(f"[系統] 正在安裝必要套件: {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

REQUIRED_PACKAGES = ['eel', 'yt-dlp', 'requests', 'mutagen']
for package in REQUIRED_PACKAGES:
    try:
        __import__(package.replace('-', '_')) # yt-dlp -> yt_dlp
    except ImportError:
        try:
            install(package)
        except Exception as e:
            print(f"[錯誤] 無法安裝 {package}: {e}")
            input("按 Enter 鍵退出...")
            sys.exit(1)

# --- 2. 引入庫 ---
import eel
from yt_dlp import YoutubeDL
import requests

# --- 3. 設定與初始化 ---
CONFIG_FILE = 'config.json'
DEFAULT_CONFIG = {
    "system_settings": {
        "ffmpeg_path": "",
        "output_directory": "Downloads",
        "theme": "dark"
    },
    "default_preferences": {
        "video_format": "mp4",
        "audio_format": "m4a",
        "audio_bitrate": "192",
        "embed_thumbnail": True,
        "embed_metadata": True,
        "video_resolution": "best"
    },
    "advanced": {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36",
        "retries": 10,
        "fragment_retries": 10,
        "check_dependencies_on_startup": True
    }
}

current_config = {}

def load_or_create_config():
    global current_config
    # 嘗試偵測系統 ffmpeg
    system_ffmpeg = shutil.which("ffmpeg")
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                current_config = json.load(f)
        except:
            current_config = DEFAULT_CONFIG
    else:
        current_config = DEFAULT_CONFIG
        if system_ffmpeg:
            current_config["system_settings"]["ffmpeg_path"] = system_ffmpeg
        save_config()
    
    # 如果設定檔裡沒有 ffmpeg 但系統有，自動補上
    if not current_config["system_settings"]["ffmpeg_path"] and system_ffmpeg:
        current_config["system_settings"]["ffmpeg_path"] = system_ffmpeg
        save_config()

def save_config():
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(current_config, f, indent=4, ensure_ascii=False)

def log_to_frontend(msg, level="info"):
    print(f"[{level.upper()}] {msg}")
    eel.add_log(msg, level)

# --- 4. 核心功能 ---

@eel.expose
def init_app():
    load_or_create_config()
    return current_config

@eel.expose
def update_config(new_settings):
    global current_config
    current_config = new_settings
    save_config()
    return "設定已儲存"

@eel.expose
def select_directory():
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    path = filedialog.askdirectory()
    root.destroy()
    return path

@eel.expose
def select_ffmpeg_file():
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    path = filedialog.askopenfilename(filetypes=[("Executable", "*.exe"), ("All Files", "*.*")])
    root.destroy()
    return path

@eel.expose
def analyze_url(url):
    """分析網址，回傳平台與是否為直播"""
    result = {"platform": "unknown", "is_live": False}
    
    if not url: return result
    
    # 簡單正則判斷平台
    if "youtube.com" in url or "youtu.be" in url:
        result["platform"] = "youtube"
    elif "bilibili.com" in url or "BV" in url:
        result["platform"] = "bilibili"
    elif "twitch.tv" in url:
        result["platform"] = "twitch"
    
    # 嘗試判斷是否為直播 (這只是一個初步檢查，準確判斷需要 yt-dlp extract_info)
    # 為了效能，我們先用關鍵字判斷，若要精準可在前端提示使用者自行確認
    if "live" in url: 
        result["is_live"] = True
    
    # 對於 Twitch，除了 /videos/ 之外的大多是直播
    if result["platform"] == "twitch" and "/videos/" not in url and "/clip/" not in url:
        result["is_live"] = True

    return result

class MyLogger:
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): log_to_frontend(f"警告: {msg}", "warn")
    def error(self, msg): log_to_frontend(f"錯誤: {msg}", "error")

def progress_hook(d):
    if d['status'] == 'downloading':
        try:
            p = d.get('_percent_str', '0%').replace('%','')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            eel.update_progress(float(p), f"下載中: {speed} | 剩餘: {eta}")
        except:
            pass
    elif d['status'] == 'finished':
        eel.update_progress(100, "下載完成，正在處理轉檔與 Metadata...")

@eel.expose
def start_download_task(url, options):
    """
    options 結構預期:
    {
        "mode": "video" | "audio" | "cover" | "metadata",
        "video_quality": "best" | "1080" | ...,
        "audio_quality": "192",
        "embed_cover": bool,
        "embed_meta": bool,
        "is_live_mode": bool
    }
    """
    threading.Thread(target=_download_worker, args=(url, options), daemon=True).start()

def _download_worker(url, options):
    cfg = current_config
    ffmpeg_path = cfg["system_settings"]["ffmpeg_path"]
    
    if not ffmpeg_path or not os.path.exists(ffmpeg_path):
        log_to_frontend("找不到 FFmpeg，請先至設定頁面指定路徑！", "error")
        return

    output_dir = os.path.join(cfg["system_settings"]["output_directory"], options['mode'].capitalize())
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    log_to_frontend(f"開始任務: {url} [{options['mode']}]", "info")
    
    # 基礎 yt-dlp 設定
    ydl_opts = {
        'ffmpeg_location': ffmpeg_path,
        'logger': MyLogger(),
        'progress_hooks': [progress_hook],
        'outtmpl': os.path.join(output_dir, '[%(uploader)s] %(title)s [%(id)s].%(ext)s'),
        'retries': cfg['advanced']['retries'],
        'fragment_retries': cfg['advanced']['fragment_retries'],
        # 解決部分網站 User-Agent 問題
        'user_agent': cfg['advanced']['user_agent'],
        # Bilibili cookie 支援 (如果有需要可在 config 加入 cookies_from_browser)
    }

    mode = options['mode']
    
    try:
        if mode == 'video':
            # 畫質選擇
            if options['video_quality'] == 'best':
                ydl_opts['format'] = "bestvideo+bestaudio/best"
            elif options['video_quality'] == '4k':
                ydl_opts['format'] = "bestvideo[height<=2160]+bestaudio/best[height<=2160]"
            elif options['video_quality'] == '1080':
                ydl_opts['format'] = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
            elif options['video_quality'] == '720':
                ydl_opts['format'] = "bestvideo[height<=720]+bestaudio/best[height<=720]"
            
            ydl_opts['merge_output_format'] = 'mp4'
            
            if options['embed_thumbnail']:
                ydl_opts['writethumbnail'] = True
                ydl_opts['embedthumbnail'] = True
            
            if options['embed_meta']:
                ydl_opts['addmetadata'] = True

        elif mode == 'audio':
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a', # 預設 m4a，較好支援 metadata
                'preferredquality': options['audio_quality'],
            }]
            
            if options['embed_thumbnail']:
                ydl_opts['writethumbnail'] = True
                # Audio 嵌入封面需要 EmbedThumbnail PP
                ydl_opts['postprocessors'].append({'key': 'EmbedThumbnail'})
            
            if options['embed_meta']:
                ydl_opts['addmetadata'] = True
                ydl_opts['postprocessors'].append({'key': 'FFmpegMetadata'})

        elif mode == 'cover':
            ydl_opts['skip_download'] = True
            ydl_opts['writethumbnail'] = True
            # 只下載封面，不轉檔

        elif mode == 'metadata':
            ydl_opts['skip_download'] = True
            ydl_opts['writeinfojson'] = True

        # 直播模式特殊處理
        if options.get('is_live_mode'):
            log_to_frontend("警告: 正在使用直播錄製模式 (Live/DVR)。", "warn")
            ydl_opts['live_from_start'] = True # 嘗試回朔
            # 直播通常不建議即時嵌入封面，容易出錯，但 yt-dlp 通常會忽略
        
        # 執行下載
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        log_to_frontend("任務圓滿完成！", "success")
        eel.update_progress(100, "完成")

    except Exception as e:
        log_to_frontend(f"執行失敗: {str(e)}", "error")
        eel.update_progress(0, "錯誤")

# --- 5. 啟動 Eel ---
if __name__ == '__main__':
    load_or_create_config()
    eel.init('web')
    try:
        eel.start('index.html', size=(950, 800))
    except (SystemExit, MemoryError, KeyboardInterrupt):
        pass