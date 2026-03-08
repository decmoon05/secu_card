from playwright.sync_api import sync_playwright
import os
import json
from typing import List, Dict

class ImageGenerator:
    def __init__(self, template_path: str = "templates/card_news.html"):
        self.template_path = os.path.abspath(template_path)
        self.output_dir = "output"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_cards(self, slides: List[Dict], news_id: str, news_source: str = "보안뉴스"):
        """
        슬라이드 데이터를 바탕으로 카드 이미지를 생성합니다.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 1080, 'height': 1080})
            
            # 템플릿 로드
            page.goto(f"file://{self.template_path}")
            
            news_output_dir = os.path.join(self.output_dir, news_id)
            if not os.path.exists(news_output_dir):
                os.makedirs(news_output_dir)

            for i, slide in enumerate(slides):
                # DOM 조작으로 내용 변경
                # 슬라이드 타입에 따른 클래스 변경
                slide_type = slide.get('type', 'body')
                
                # evaluate에 slide와 news_source를 함께 전달
                page.evaluate(f"""
                    ([slide, news_source]) => {{
                        const container = document.getElementById('card-container');
                        const title = document.getElementById('title');
                        const subtitle = document.getElementById('subtitle');
                        const sourceText = document.getElementById('source-text');
                        
                        container.className = ''; // 클래스 초기화
                        container.classList.add('card-' + slide.type);
                        
                        title.innerText = slide.title || '';
                        subtitle.innerText = slide.content || slide.subtitle || '';
                        
                        if (sourceText) {{
                            sourceText.innerText = `Copyright © ${{news_source}}. All Rights Reserved.`;
                        }}
                    }}
                """, [slide, news_source])
                
                # 스크린샷 저장
                output_path = os.path.join(news_output_dir, f"slide_{i+1}.png")
                page.screenshot(path=output_path)
                print(f"Generated: {output_path}")
                
            browser.close()

if __name__ == "__main__":
    # 테스트 데이터
    test_slides = [
        {"slide_no": 1, "type": "cover", "title": "메인 제목", "subtitle": "부제목"},
        {"slide_no": 2, "type": "body", "title": "포인트 1", "content": "내용입니다."},
        {"slide_no": 5, "type": "closing", "title": "마무리", "content": "팁입니다."}
    ]
    generator = ImageGenerator()
    generator.generate_cards(test_slides, "test_news")
