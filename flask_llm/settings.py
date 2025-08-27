import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DJANGO_API_URL = os.getenv("DJANGO_API_URL", "http://localhost:8000")
    FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    AZURE_OPENAI_API_VERSION = os.getenv(
        "AZURE_OPENAI_API_VERSION", "2024-02-15-preview"
    )


settings = Settings()
