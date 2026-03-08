import requests
import feedparser
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict

class NewsScraper:
    def __init__(self):
        self.sources = {
            "보안뉴스": "https://www.boannews.com/media/list.asp",
            "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
            "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
            "SecurityWeek": "https://feeds.feedburner.com/securityweek"
        }
        self.base_url_boan = "https://www.boannews.com"
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_all_weekly_news(self) -> List[Dict]:
        """
        모든 소스에서 지난 7일간의 뉴스를 수집합니다.
        """
        all_news = []
        seven_days_ago = datetime.now() - timedelta(days=7)
        print(f"--- Weekly News Scraping (Since: {seven_days_ago.strftime('%Y-%m-%d')}) ---")

        for source_name, url in self.sources.items():
            print(f"Fetching from: {source_name}...")
            
            if source_name == "보안뉴스":
                all_news.extend(self._fetch_boannews(url, seven_days_ago))
            else:
                all_news.extend(self._fetch_rss(source_name, url, seven_days_ago))
        
        print(f"Total {len(all_news)} items collected from all sources.")
        return all_news

    def _fetch_boannews(self, url: str, since: datetime) -> List[Dict]:
        news_items = []
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = response.apparent_encoding
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 보안뉴스는 목록에서 날짜 확인이 필요함 (일반적으로 .news_txt 옆이나 밑에 존재)
            # 여기서는 간단히 최신 1~2페이지를 긁어 날짜를 대조하는 방식으로 구현 (실제 구현에선 정밀한 파싱 필요)
            items = soup.select('.news_list')
            for item in items:
                title_tag = item.select_one('.news_txt')
                if not title_tag: continue
                
                # 보안뉴스 날짜 파싱 (예: 2026-03-07 10:30)
                # 실제 보안뉴스 페이지 구조에 따라 수정 필요
                # 목록 페이지에는 날짜가 직접 노출되지 않는 경우도 있어, 일단 최신 목록을 가져오되
                # 실제 뉴스 상세 페이지까지 들어가야 정확한 날짜를 알 수 있음.
                # 편의상 최근 1주일 뉴스가 충분히 포함된다고 가정하거나 상세 페이지 방문 로직 추가 가능.
                
                title = title_tag.get_text().strip()
                link = self.base_url_boan + item.find('a')['href']
                summary = item.select_one('.news_content').get_text().strip() if item.select_one('.news_content') else ""
                
                news_items.append({
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "source": "보안뉴스",
                    "date": datetime.now() # 목록에서 날짜 파싱이 어려울 경우 현재 시각으로 대체 (나중에 필터링됨)
                })
        except Exception as e:
            print(f"Error scraping 보안뉴스: {e}")
        return news_items

    def _fetch_rss(self, source_name: str, url: str, since: datetime) -> List[Dict]:
        news_items = []
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                # RSS 날짜 파싱
                published_time = entry.get('published_parsed') or entry.get('updated_parsed')
                if published_time:
                    dt = datetime(*published_time[:6])
                    if dt < since:
                        continue # 7일 이전 뉴스는 건너뜀
                else:
                    dt = datetime.now()

                news_items.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": entry.get('summary', entry.get('description', '')),
                    "source": source_name,
                    "date": dt
                })
        except Exception as e:
            print(f"Error fetching RSS from {source_name}: {e}")
        return news_items

    def save_to_json(self, news_list: List[Dict], filename: str = "latest_news.json"):
        file_path = os.path.join(self.data_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(news_list, f, ensure_ascii=False, indent=4)
        print(f"Saved {len(news_list)} news items to {file_path}")

if __name__ == "__main__":
    scraper = NewsScraper()
    news = scraper.fetch_latest_news()
    print(f"Total news scraped: {len(news)}")
    for n in news:
        print(f"- {n['title']}")
