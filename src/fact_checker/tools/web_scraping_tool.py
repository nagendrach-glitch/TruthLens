from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import requests
from bs4 import BeautifulSoup

class WebScrapingInput(BaseModel):
    url: str = Field(..., description="Website URL to scrape")

class WebScrapingTool(BaseTool):
    name: str = "Web Scraping Tool"
    description: str = "Extract content from web pages for fact-checking"
    args_schema: Type[BaseModel] = WebScrapingInput

    def _run(self, url: str) -> str:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            if len(text) > 5000:
                text = text[:5000] + "..."
            
            return f"Web Content from {url}:\n\n{text}"
            
        except Exception as e:
            return f"Error scraping website {url}: {str(e)}"