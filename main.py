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


class Config:
    def __init__(self, dotenv_path: str):
        load_dotenv(dotenv_path)
        self.api_key = os.getenv("API_KEY")
        self.imagemagick_path = os.getenv("IMAGEMAGICK_PATH")
        self.model = os.getenv("MODEL", "gemini-model-name")
        self.validate()

    def validate(self):
        if not self.api_key or not self.imagemagick_path:
            raise EnvironmentError("API_KEY and IMAGEMAGICK_PATH must be set in the .env file.")
        # Set ImageMagick path for moviepy
        change_settings({"IMAGEMAGICK_BINARY": self.imagemagick_path})
        os.environ["IMAGEMAGICK_BINARY"] = self.imagemagick_path


class NewsFetcher:
    def __init__(self):
        self.news_sources = {
            "Trading": "https://www.moneycontrol.com/news/business/",
            "Cricket": "https://www.cricbuzz.com/cricket-news/latest-news",
            "Entertainment": "https://timesofindia.indiatimes.com/entertainment"
        }
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def fetch_latest_news(self):
        headlines = {}
        for category, url in self.news_sources.items():
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
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


class GeminiClient:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def call_api(self, prompt: str) -> str:
        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            content = response.json()
            raw_text = content["candidates"][0]["content"]["parts"][0]["text"]
            return self.clean_text(raw_text)
        except Exception as e:
            print(f"Gemini API call failed: {e}")
            return "⚠️ Unable to generate summary."

    @staticmethod
    def clean_text(text: str) -> str:
        return re.sub(r"[*•]", "", text).strip()


class JokeFetcher:
    @staticmethod
    def get_joke() -> str:
        try:
            response = requests.get("https://official-joke-api.appspot.com/jokes/random", timeout=5)
            response.raise_for_status()
            data = response.json()
            return f"{data['setup']} {data['punchline']}"
        except Exception:
            return "Why did the web developer go broke? Because he used up all his cache!"


class TTSGenerator:
    @staticmethod
    def generate_tts_audio(text: str, filename: str):
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.save_to_file(text, filename)
        engine.runAndWait()


class VideoGenerator:
    def __init__(self, width=1080, height=1920, font="Arial"):
        self.width = width
        self.height = height
        self.font = font

    def generate_video(self, text: str, filename: str):
        print("🎬 Generating scrolling video with audio...")
        audio_filename = filename.replace(".mp4", ".mp3")

        TTSGenerator.generate_tts_audio(text, audio_filename)
        audio_clip = AudioFileClip(audio_filename)
        duration = audio_clip.duration

        # Black background clip
        bg = ImageClip(np.zeros((self.height, self.width, 3), dtype=np.uint8)).set_duration(duration)

        # Text clip with wrapping and alignment
        text_clip = TextClip(text, fontsize=50, color='white', font=self.font,
                             method='caption', size=(self.width - 200, None), align='West')

        scroll_height = self.height + text_clip.h

        def scroll_pos(t):
            return ('center', self.height - (scroll_height / duration) * t)

        scrolling_text = text_clip.set_pos(scroll_pos).set_duration(duration)

        watermark = (TextClip("@nileshyadav", fontsize=30, color='white', font=self.font)
                     .set_duration(duration).set_pos(('right', 'bottom')).set_opacity(0.5))

        final_clip = CompositeVideoClip([bg, scrolling_text, watermark]).set_duration(duration).set_audio(audio_clip)

        final_clip.write_videofile(filename, fps=24, codec="libx264", audio_codec="aac")
        print(f"✅ Video saved as {filename}")


def main():
    dotenv_path = r"C:\Users\Deepak\Desktop\changes\cloudinary_uploader\.env"
    config = Config(dotenv_path)
    news_fetcher = NewsFetcher()
    gemini_client = GeminiClient(config.api_key, config.model)
    video_generator = VideoGenerator()

    print("📽️ Starting daily news + fun video generation...")
    headlines = news_fetcher.fetch_latest_news()
    summaries = {}

    for category, titles in headlines.items():
        if titles:
            print(f"\n📰 {category} Headlines:")
            for title in titles:
                print(f"- {title}")

            combined_titles = " ".join(titles)
            print("⏳ Summarizing using Gemini...")
            summary = gemini_client.call_api(f"Summarize the following {category} news headlines: {combined_titles}")
            print("✅ Summary:")
            print(summary)
            summaries[category] = summary

            date_str = datetime.now().strftime("%Y%m%d")
            filename = f"{category.lower()}_news_{date_str}.mp4"
            video_generator.generate_video(summary, filename)
        else:
            print(f"No {category} headlines found.")
            summaries[category] = "No data"

    joke = JokeFetcher.get_joke()
    fun_summary = (
        f"📰 Trading Update:\n{summaries.get('Trading', 'No data')}\n\n"
        f"🏏 Cricket News:\n{summaries.get('Cricket', 'No data')}\n\n"
        f"🎬 Entertainment:\n{summaries.get('Entertainment', 'No data')}\n\n"
        f"😂 Joke of the Day:\n{joke}"
    )

    print("\n🎉 Creating final combined fun video...")
    final_filename = f"daily_fun_news_{datetime.now().strftime('%Y%m%d')}.mp4"
    video_generator.generate_video(fun_summary, final_filename)


if __name__ == "__main__":
    main()
