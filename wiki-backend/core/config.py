import os
from dotenv import load_dotenv

# 自动加载 .env 里的变量
load_dotenv()

class Settings:
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", 8000))
    DB_PATH: str = os.getenv("DB_PATH")
    CHROMA_PATH: str = os.getenv("CHROMA_PATH")
    HF_ENDPOINT: str = os.getenv("HF_ENDPOINT", "https://hf-mirror.com")
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY")

settings = Settings()
