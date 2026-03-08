from google import genai
import os
import json
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()

class GeminiSummarizer:
    def __init__(self, api_key: str = None):
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found. Please set it in .env file.")
        
        self.client = genai.Client(api_key=api_key)
        # 리스트 확인 결과: 정확한 모델 ID인 gemini-3.1-pro-preview 적용
        self.model_id = "gemini-3.1-pro-preview"

    def summarize_weekly_news(self, news_items: List[Dict]) -> List[Dict]:
        """
        한 주간의 다수 뉴스 기사를 분석하여 주간 종합 카드뉴스를 생성합니다.
        """
        # 뉴스 데이터를 텍스트로 결합 (토큰 제한을 고려하여 핵심만 추출)
        combined_context = ""
        for item in news_items[:20]: # 최대 20개 기사만 분석
            combined_context += f"- [{item['source']}] {item['title']}: {item['summary'][:150]}\n"

        prompt = f"""
        당신은 글로벌 보안 트렌드 분석가입니다. 지난 1주일간 발생한 아래 보안 뉴스들을 분석하여 
        가장 중요한 '주간 보안 TOP 5 이슈'를 선정하고 카드뉴스로 구성하세요.

        [수집된 뉴스 데이터]
        {combined_context}

        [지침]
        1. 여러 소스(국내외)의 정보를 종합하여 중복된 이슈는 하나로 묶을 것.
        2. 가장 파급력이 컸던 사건이나 기술적 위협 위주로 선정.
        3. 문장은 초간결(20자 내외)하고 강력하게 작성.
        4. 하루 뉴스가 아닌 '주간 종합' 성격이 나타나도록 작성.

        [출력 형식 (JSON)]
        [
            {{"slide_no": 1, "type": "cover", "title": "주간 보안 브리핑", "subtitle": "지난 1주일간의 핵심 위협 TOP 5"}},
            {{"slide_no": 2, "type": "body", "title": "1. 주요 침해 사고", "content": "가장 큰 사건 요약"}},
            {{"slide_no": 3, "type": "body", "title": "2. 신규 취약점", "content": "주의해야 할 제로데이 등"}},
            {{"slide_no": 4, "type": "body", "title": "3. 글로벌 트렌드", "content": "해외 주요 보안 이슈"}},
            {{"slide_no": 5, "type": "closing", "title": "이번 주 보안 팁", "content": "통합 대응 전략"}}
        ]
        """
        
        try:
            print(f"Calling Gemini API for Weekly Summary ({self.model_id})...")
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            return json.loads(text)
        except Exception as e:
            print(f"Error in weekly summarization: {e}")
            return []

if __name__ == "__main__":
    summarizer = GeminiSummarizer()
    print(f"Using model: {summarizer.model_id}")
