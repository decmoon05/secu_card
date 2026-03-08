import os
import hashlib
from datetime import datetime
from src.collector.rss_collector import NewsScraper
from src.summarizer.gemini_summarizer import GeminiSummarizer
from src.generator.image_generator import ImageGenerator
from dotenv import load_dotenv

load_dotenv()

def main():
    print("--- Security News Automation Pipeline Starting ---")
    
    # 1. 주간 뉴스 수집 (다중 소스)
    scraper = NewsScraper()
    news_list = scraper.fetch_all_weekly_news()
    
    if not news_list:
        print("No news found. Check your scraper or target URLs.")
        return

    # 2. 요약 및 이미지 생성 준비
    try:
        summarizer = GeminiSummarizer()
        generator = ImageGenerator()
    except Exception as e:
        print(f"Error initializing modules: {e}")
        return

    # 오늘 날짜 (YYYYMMDD)
    today_str = datetime.now().strftime('%Y%m%d')
    news_id = f"WEEKLY_{today_str}"

    print(f"\n--- Processing Weekly Digest: {news_id} ---")
    
    # 2. Gemini를 통한 주간 종합 카드뉴스 텍스트 생성
    print("Summarizing weekly trends with Gemini...")
    slides = summarizer.summarize_weekly_news(news_list)
    
    if not slides:
        print("Summarization failure.")
        return
        
    # 3. 이미지 생성 (출처는 종합 정보로 표기)
    print("Generating weekly card images...")
    source_info = "보안뉴스, The Hacker News, BleepingComputer 등"
    generator.generate_cards(slides, news_id, source_info)
    
    print(f"Done! Weekly images saved in output/{news_id}/")

    print("\n--- Pipeline Completed ---")

if __name__ == "__main__":
    main()
