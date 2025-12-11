# Simple_yt-dlp_GUI

![License](https://img.shields.io/github/license/h-o-w-a-r-d/Simple_yt-dlp_GUI)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

<!-- Keywords: yt-dlp gui, video downloader, youtube downloader, bilibili downloader, twitch downloader, python, ffmpeg, mp3 converter, audio extraction, windows, macos, linux, B站下載, 影片下載神器, 直播錄影 -->

**Simple yt-dlp GUI** 是一個基於 Python 與 Eel 開發的現代化影音下載工具。它整合了 `yt-dlp` 強大的核心，並提供直覺的圖形介面 (GUI)，支援 YouTube、Bilibili、Twitch 等主流平台的高畫質影片、純音訊、封面與 Metadata 下載。

![Screenshot](https://raw.githubusercontent.com/h-o-w-a-r-d/Simple_yt-dlp_GUI/refs/heads/main/screenshot/screenshot.png)

## ✨ 核心功能

*   **多平台支援**：自動偵測並支援 YouTube、Bilibili (含分P)、Twitch (VOD 與 Clips)。
*   **高度自訂化下載**：
    *   🎬 **影片模式**：支援 4K/1080p/720p 畫質選擇，可選是否內嵌封面與 Metadata。
    *   🎵 **音訊模式**：自動轉檔為 M4A/MP3，支援位元率選擇 (128k/192k/320k)。
    *   🖼️ **純封面模式**：僅下載高解析度縮圖。
    *   📄 **純 Metadata**：僅下載影片資訊 JSON。
*   **直播錄製 (DVR)**：支援直播回朔錄製（由直播開頭開始下載），並具備實驗性功能警告。
*   **自動化依賴管理**：首次啟動自動檢查並安裝所需 Python 套件。
*   **FFmpeg 整合**：自動偵測系統中的 FFmpeg，並提供設定介面手動指定路徑。
*   **現代化 GUI**：基於 Web 技術 (HTML/CSS/JS) 的響應式深色主題介面。

## 🛠️ 安裝與使用

### 前置需求

1.  **Python 3.8 或更高版本**
2.  **FFmpeg**：
    *   請確保電腦中已下載 `ffmpeg.exe`。
    *   程式首次啟動時會嘗試自動偵測，若失敗可在設定頁面手動指定。

### 快速開始

1.  複製此專案到本地：
    ```bash
    git clone https://github.com/h-o-w-a-r-d/Simple_yt-dlp_GUI.git
    cd 你的專案名
    ```

2.  (可選) 建立虛擬環境：
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  直接執行主程式（程式會自動安裝缺少的依賴項）：
    ```bash
    python main.py
    ```

### 依賴項列表

雖然程式會自動安裝，但你也可以手動安裝：
```txt
eel
yt-dlp
requests
mutagen
```

## ⚙️ 設定說明

設定檔位於根目錄的 `config.json` (首次執行後自動生成)：

*   **ffmpeg_path**: FFmpeg 執行檔的絕對路徑。
*   **output_directory**: 檔案預設儲存位置。
*   **advanced**: 包含 User-Agent 與重試次數等進階設定。

## ⚠️ 免責聲明 (Disclaimer)

本專案僅供技術研究與個人學習使用。
1.  使用者在使用本工具下載內容時，請務必遵守各平台的服務條款 (Terms of Service)。
2.  請勿使用本工具下載受版權保護且未經授權的內容。
3.  開發者不對使用者因使用本工具而產生的任何法律責任負責。

## 📄 授權 (License)

本專案採用 **MIT License** 授權。詳情請參閱 [LICENSE](LICENSE) 檔案。

---
**致謝**：本專案核心依賴於強大的 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 與 [FFmpeg](https://ffmpeg.org/)。
