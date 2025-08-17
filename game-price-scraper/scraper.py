import requests
import time
import random
import json
import logging
from dataclasses import dataclass
from typing import List, Optional
import re
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

@dataclass
class GameListing:
    title: str
    price: int
    platform: str
    condition: str
    seller: str
    location: str
    url: str
    source: str
    posted_time: Optional[str] = None
    seller_rating: Optional[str] = None

class GamePriceScraper:
    def __init__(self):
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        self.results = []
    
    def setup_selenium_driver(self):
        """設定 Selenium WebDriver (適用於 Codespaces)"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            driver = webdriver.Chrome(
                executable_path=ChromeDriverManager().install(),
                options=chrome_options
            )
            return driver
        except Exception as e:
            logger.error(f"設定 Selenium WebDriver 失敗: {e}")
            return None
    
    def extract_price(self, price_text):
        """從價格文字中提取數字"""
        if not price_text:
            return 0
        numbers = re.findall(r'\d+', str(price_text).replace(',', ''))
        if numbers:
            return int(''.join(numbers))
        return 0
    
    def detect_platform(self, title):
        """根據標題偵測遊戲平台"""
        title_lower = title.lower()
        
        if any(keyword in title_lower for keyword in ['switch', 'ns', 'nintendo']):
            return 'Nintendo Switch'
        elif any(keyword in title_lower for keyword in ['ps5', 'playstation 5']):
            return 'PlayStation 5'
        elif any(keyword in title_lower for keyword in ['ps4', 'playstation 4']):
            return 'PlayStation 4'
        elif any(keyword in title_lower for keyword in ['xbox series x', 'xbox series s', 'xsx', 'xss']):
            return 'Xbox Series X/S'
        elif any(keyword in title_lower for keyword in ['xbox one', 'xbone']):
            return 'Xbox One'
        else:
            return '未知平台'
    
    def search_carousel_demo(self, game_name):
        """旋轉拍賣搜尋 (示例資料)"""
        logger.info(f"模擬搜尋旋轉拍賣: {game_name}")
        
        # 由於實際爬蟲需要處理反爬蟲機制，這裡提供示例資料
        demo_listings = [
            GameListing(
                title=f"{game_name} Nintendo Switch 二手",
                price=1200,
                platform="Nintendo Switch",
                condition="二手",
                seller="user123",
                location="台北市",
                url="https://www.carousell.com.tw/p/example1",
                source="旋轉拍賣"
            ),
            GameListing(
                title=f"{game_name} PS5 中文版",
                price=1800,
                platform="PlayStation 5",
                condition="二手",
                seller="gamer456",
                location="新北市",
                url="https://www.carousell.com.tw/p/example2",
                source="旋轉拍賣"
            )
        ]
        
        time.sleep(1)  # 模擬請求延遲
        return demo_listings
    
    def search_ruten_demo(self, game_name):
        """露天拍賣搜尋 (示例資料)"""
        logger.info(f"模擬搜尋露天拍賣: {game_name}")
        
        demo_listings = [
            GameListing(
                title=f"{game_name} Switch 日版",
                price=1500,
                platform="Nintendo Switch",
                condition="二手",
                seller="seller789",
                location="台中市",
                url="https://www.ruten.com.tw/item/example1",
                source="露天拍賣"
            ),
            GameListing(
                title=f"{game_name} PS4 完整版",
                price=800,
                platform="PlayStation 4",
                condition="二手",
                seller="retro_gamer",
                location="高雄市",
                url="https://www.ruten.com.tw/item/example2",
                source="露天拍賣"
            )
        ]
        
        time.sleep(1)
        return demo_listings
    
    def search_all_platforms(self, game_name):
        """搜尋所有平台"""
        logger.info(f"開始搜尋遊戲: {game_name}")
        
        all_listings = []
        
        # 搜尋各個平台
        platforms = [
            ('旋轉拍賣', self.search_carousel_demo),
            ('露天拍賣', self.search_ruten_demo),
        ]
        
        for platform_name, search_func in platforms:
            try:
                listings = search_func(game_name)
                all_listings.extend(listings)
                logger.info(f"{platform_name} 找到 {len(listings)} 個結果")
            except Exception as e:
                logger.error(f"搜尋 {platform_name} 時發生錯誤: {e}")
        
        # 按價格排序
        all_listings.sort(key=lambda x: x.price)
        
        return all_listings