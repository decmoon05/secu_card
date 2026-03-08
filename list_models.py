from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

def list_available_models():
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    print("--- 사용 가능한 모델 리스트 ---")
    # 최신 SDK 방식으로 모델 리스트 가져오기
    for model in client.models.list():
        print(f"Model ID: {model.name}")

if __name__ == "__main__":
    list_available_models()
