# 📽️ AI News Shorts Generator

**AI News Shorts Generator** is a Python-based tool that scrapes top news from trusted sources, summarizes it using **Google Gemini AI**, converts the summary into **text-to-speech (TTS)**, and generates vertical videos with smooth scrolling text, a branding watermark, and a daily joke. Perfect for **YouTube Shorts**, **Instagram Reels**, or **WhatsApp status**.

---

## 🚀 Features

- 🔍 Scrapes headlines from:
  - [MoneyControl](https://www.moneycontrol.com) – *Trading*
  - [CricBuzz](https://www.cricbuzz.com) – *Cricket*
  - [Times of India](https://timesofindia.indiatimes.com) – *Entertainment*
- 🤖 Summarizes headlines using **Google Gemini LLM**
- 🎙️ Generates TTS voice-over using `pyttsx3`
- 📽️ Creates 1080x1920 vertical videos with:
  - Scrolling text synced to audio
  - Watermark: `@nileshyadav`
- 😂 Adds a “Joke of the Day” from a public joke API
- 📦 Outputs daily video compilations in `.mp4` format

---

## 🧠 How It Works

1. **Scrapes** top headlines from 3 news websites  
2. **Summarizes** them using Gemini API  
3. **Generates** voice-over with TTS  
4. **Creates** vertical video with animated text  
5. **Adds** branding and a joke  
6. **Exports** a fun, shareable video

---

## 📦 Installation

```bash
git clone https://github.com/nileshyadav12/ai-news-shorts-generator.git
cd ai-news-shorts-generator
pip install -r requirements.txt
