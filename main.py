import os
import re
import requests
import pyttsx3
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime
from moviepy.editor import TextClip, ImageClip, CompositeVideoClip, AudioFileClip
from moviepy.config import change_settings
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(r"C:\Users\Deepak\Desktop\changes\cloudinary_uploader\.env")

# URL to download ImageMagick for Windows: https://imagemagick.org/script/download.php#windows

# Config from .env
API_KEY = os.getenv("API_KEY")
IMAGEMAGICK_PATH = os.getenv("IMAGEMAGICK_PATH")
MODEL = os.getenv("MODEL", "gemini-model-name")

# Validate critical config
if not API_KEY or not IMAGEMAGICK_PATH:
    raise EnvironmentError("Please set API_KEY and IMAGEMAGICK_PATH in your .env file.")

# Set ImageMagick path for moviepy
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_PATH})
os.environ["IMAGEMAGICK_BINARY"] = IMAGEMAGICK_PATH

# Gemini API base URL
BASE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

# Fetch latest news headlines from given sources
def fetch_latest_news():
    news_sources = {
        "Trading": "https://www.moneycontrol.com/news/business/",
        "Cricket": "https://www.cricbuzz.com/cricket-news/latest-news",
        "Entertainment": "https://timesofindia.indiatimes.com/entertainment"
    }
    headlines = {}
    headers = {"User-Agent": "Mozilla/5.0"}
    for category, url in news_sources.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            if category == "Trading":
                items = soup.select("li.clearfix a")
            elif category == "Cricket":
                items = soup.select("h2.cb-nws-hdln a")
            elif category == "Entertainment":
                items = soup.select("div.w_tle a")
            else:
                items = []

            headlines[category] = [item.get_text(strip=True) for item in items[:3]]
        except Exception as e:
            print(f"Error fetching {category} news: {e}")
            headlines[category] = []
    return headlines

# Call Gemini API with prompt, returns text summary
def call_gemini(prompt: str) -> str:
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(BASE_URL, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        content = response.json()
        raw_text = content["candidates"][0]["content"]["parts"][0]["text"]
        return clean_text(raw_text)
    except Exception as e:
        print(f"Gemini API call failed: {e}")
        return "⚠️ Unable to generate summary."

# Remove unwanted characters from text
def clean_text(text: str) -> str:
    return re.sub(r"[*•]", "", text).strip()

# Fetch a random joke from joke API
def get_joke() -> str:
    try:
        response = requests.get("https://official-joke-api.appspot.com/jokes/random", timeout=5)
        response.raise_for_status()
        data = response.json()
        return f"{data['setup']} {data['punchline']}"
    except:
        return "Why did the web developer go broke? Because he used up all his cache!"

# Generate TTS audio file from text
def generate_tts_audio(text: str, filename: str):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.save_to_file(text, filename)
    engine.runAndWait()

# Generate scrolling video with text and audio
def generate_video(text: str, filename: str):
    print("🎬 Generating scrolling video with audio...")
    audio_filename = filename.replace(".mp4", ".mp3")
    generate_tts_audio(text, audio_filename)

    audio_clip = AudioFileClip(audio_filename)
    duration = audio_clip.duration
    width, height = 1080, 1920

    # Create black background clip
    bg = ImageClip(np.zeros((height, width, 3), dtype=np.uint8)).set_duration(duration)

    # Create text clip with wrap and alignment
    text_clip = TextClip(text, fontsize=50, color='white', font="Arial",
                         method='caption', size=(width - 200, None), align='West')

    scroll_height = height + text_clip.h

    # Scrolling function: text scrolls from bottom to top
    def scroll_pos(t):
        return ('center', height - (scroll_height / duration) * t)

    scrolling_text = text_clip.set_pos(scroll_pos).set_duration(duration)

    # Watermark clip
    watermark = (TextClip("@nileshyadav", fontsize=30, color='white', font="Arial")
                 .set_duration(duration).set_pos(('right', 'bottom')).set_opacity(0.5))

    # Composite all clips and add audio
    final_clip = CompositeVideoClip([bg, scrolling_text, watermark]).set_duration(duration).set_audio(audio_clip)

    # Write video file
    final_clip.write_videofile(filename, fps=24, codec="libx264", audio_codec="aac")
    print(f"✅ Video saved as {filename}")

# Main execution
if __name__ == "__main__":
    print("📽️ Starting daily news + fun video generation...")
    headlines = fetch_latest_news()
    summaries = {}

    for category, titles in headlines.items():
        if titles:
            print(f"\n📰 {category} Headlines:")
            for title in titles:
                print(f"- {title}")
            combined_titles = " ".join(titles)
            print("⏳ Summarizing using Gemini...")
            summary = call_gemini(f"Summarize the following {category} news headlines: {combined_titles}")
            print("✅ Summary:")
            print(summary)
            summaries[category] = summary
            date_str = datetime.now().strftime("%Y%m%d")
            filename = f"{category.lower()}_news_{date_str}.mp4"
            generate_video(summary, filename)
        else:
            print(f"No {category} headlines found.")
            summaries[category] = "No data"

    # Combine all summaries + joke into a final fun video
    joke = get_joke()
    fun_summary = (
        f"📰 Trading Update:\n{summaries.get('Trading', 'No data')}\n\n"
        f"🏏 Cricket News:\n{summaries.get('Cricket', 'No data')}\n\n"
        f"🎬 Entertainment:\n{summaries.get('Entertainment', 'No data')}\n\n"
        f"😂 Joke of the Day:\n{joke}"
    )
    print("\n🎉 Creating final combined fun video...")
    final_filename = f"daily_fun_news_{datetime.now().strftime('%Y%m%d')}.mp4"
    generate_video(fun_summary, final_filename)
