import requests
import time
import random
import json
import logging
from dataclasses import dataclass
from typing import List, Optional
import re
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def get_random_user_agent(self):
        return random.choice(self.user_agents)
    
    def setup_selenium_driver(self):
        """設定 Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument(f'--user-agent={self.get_random_user_agent()}')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            logger.error(f"設定 Selenium WebDriver 失敗: {e}")
            return None
    
    def extract_price(self, price_text):
        """從價格文字中提取數字"""
        if not price_text:
            return 0
        # 移除所有非數字字符，但保留數字
        price_str = re.sub(r'[^\d]', '', str(price_text))
        if price_str:
            return int(price_str)
        return 0
    
    def detect_platform(self, title):
        """根據標題偵測遊戲平台"""
        title_lower = title.lower()
        
        platform_keywords = {
            'Nintendo Switch': ['switch', 'ns', 'nintendo switch'],
            'PlayStation 5': ['ps5', 'playstation 5', 'play station 5'],
            'PlayStation 4': ['ps4', 'playstation 4', 'play station 4'],
            'Xbox Series X/S': ['xbox series x', 'xbox series s', 'xsx', 'xss'],
            'Xbox One': ['xbox one', 'xbone'],
            'PC': ['pc', 'steam', '電腦版']
        }
        
        for platform, keywords in platform_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                return platform
        
        return '未知平台'
    
    def search_ruten(self, game_name):
        """搜尋露天拍賣"""
        listings = []
        try:
            logger.info(f"搜尋露天拍賣: {game_name}")
            
            # 使用露天拍賣的搜尋API
            search_url = f"https://www.ruten.com.tw/find/?q={quote(game_name)}"
            
            self.session.headers['User-Agent'] = self.get_random_user_agent()
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 尋找商品項目
                items = soup.find_all('div', class_='rt-item') or soup.find_all('div', class_='item')
                
                for item in items[:10]:  # 限制結果數量
                    try:
                        # 提取標題
                        title_elem = item.find('a', class_='rt-item-title') or item.find('h3')
                        if not title_elem:
                            continue
                        title = title_elem.get_text(strip=True)
                        
                        # 提取價格
                        price_elem = item.find('b', class_='rt-item-price') or item.find('span', class_='price')
                        if not price_elem:
                            continue
                        price = self.extract_price(price_elem.get_text(strip=True))
                        
                        if price == 0:
                            continue
                        
                        # 提取網址
                        url = title_elem.get('href', '')
                        if url and not url.startswith('http'):
                            url = 'https://www.ruten.com.tw' + url
                        
                        # 提取賣家資訊
                        seller_elem = item.find('span', class_='rt-item-seller')
                        seller = seller_elem.get_text(strip=True) if seller_elem else '未知賣家'
                        
                        listing = GameListing(
                            title=title,
                            price=price,
                            platform=self.detect_platform(title),
                            condition='二手',  # 預設為二手
                            seller=seller,
                            location='台灣',
                            url=url,
                            source='露天拍賣'
                        )
                        listings.append(listing)
                        
                    except Exception as e:
                        logger.warning(f"解析露天拍賣項目時發生錯誤: {e}")
                        continue
                        
            time.sleep(random.uniform(1, 2))  # 隨機延遲
            
        except Exception as e:
            logger.error(f"搜尋露天拍賣時發生錯誤: {e}")
        
        return listings
    
    def search_shopee(self, game_name):
        """搜尋蝦皮購物"""
        listings = []
        try:
            logger.info(f"搜尋蝦皮購物: {game_name}")
            
            driver = self.setup_selenium_driver()
            if not driver:
                return listings
            
            search_url = f"https://shopee.tw/search?keyword={quote(game_name)}"
            driver.get(search_url)
            
            # 等待頁面載入
            time.sleep(3)
            
            # 尋找商品項目
            items = driver.find_elements(By.CSS_SELECTOR, '[data-sqe="item"]')
            
            for item in items[:8]:  # 限制結果數量
                try:
                    # 提取標題
                    title_elem = item.find_element(By.CSS_SELECTOR, '[data-sqe="name"]')
                    title = title_elem.text.strip()
                    
                    # 提取價格
                    price_elem = item.find_element(By.CSS_SELECTOR, '.shopee-price')
                    price_text = price_elem.text.strip()
                    price = self.extract_price(price_text)
                    
                    if price == 0:
                        continue
                    
                    # 提取網址
                    link_elem = item.find_element(By.CSS_SELECTOR, 'a')
                    url = link_elem.get_attribute('href')
                    
                    # 提取位置
                    location_elem = item.find_elements(By.CSS_SELECTOR, '.shopee-item-card__location')
                    location = location_elem[0].text.strip() if location_elem else '台灣'
                    
                    listing = GameListing(
                        title=title,
                        price=price,
                        platform=self.detect_platform(title),
                        condition='二手',
                        seller='蝦皮賣家',
                        location=location,
                        url=url,
                        source='蝦皮購物'
                    )
                    listings.append(listing)
                    
                except Exception as e:
                    logger.warning(f"解析蝦皮項目時發生錯誤: {e}")
                    continue
            
            driver.quit()
            
        except Exception as e:
            logger.error(f"搜尋蝦皮購物時發生錯誤: {e}")
            if 'driver' in locals():
                driver.quit()
        
        return listings
    
    def search_yahoo_auction(self, game_name):
        """搜尋Yahoo拍賣"""
        listings = []
        try:
            logger.info(f"搜尋Yahoo拍賣: {game_name}")
            
            search_url = f"https://tw.bid.yahoo.com/search/auction/product?p={quote(game_name)}"
            
            self.session.headers['User-Agent'] = self.get_random_user_agent()
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 尋找商品項目
                items = soup.find_all('li', class_='BaseGridItem') or soup.find_all('div', class_='srp-item')
                
                for item in items[:8]:
                    try:
                        # 提取標題
                        title_elem = item.find('h3') or item.find('a', class_='product-name')
                        if not title_elem:
                            continue
                        title = title_elem.get_text(strip=True)
                        
                        # 提取價格
                        price_elem = item.find('span', class_='price') or item.find('em', class_='price')
                        if not price_elem:
                            continue
                        price = self.extract_price(price_elem.get_text(strip=True))
                        
                        if price == 0:
                            continue
                        
                        # 提取網址
                        url_elem = item.find('a')
                        url = url_elem.get('href', '') if url_elem else ''
                        if url and not url.startswith('http'):
                            url = 'https://tw.bid.yahoo.com' + url
                        
                        listing = GameListing(
                            title=title,
                            price=price,
                            platform=self.detect_platform(title),
                            condition='二手',
                            seller='Yahoo賣家',
                            location='台灣',
                            url=url,
                            source='Yahoo拍賣'
                        )
                        listings.append(listing)
                        
                    except Exception as e:
                        logger.warning(f"解析Yahoo拍賣項目時發生錯誤: {e}")
                        continue
            
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            logger.error(f"搜尋Yahoo拍賣時發生錯誤: {e}")
        
        return listings
    
    def search_pchome_24h(self, game_name):
        """搜尋PChome 24h購物"""
        listings = []
        try:
            logger.info(f"搜尋PChome 24h: {game_name}")
            
            search_url = f"https://24h.pchome.com.tw/search/v3.3/?q={quote(game_name)}"
            
            self.session.headers['User-Agent'] = self.get_random_user_agent()
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 尋找商品項目
                items = soup.find_all('div', class_='prod_item') or soup.find_all('li', class_='item')
                
                for item in items[:5]:  # PChome通常是新品，限制較少結果
                    try:
                        # 提取標題
                        title_elem = item.find('h5') or item.find('a', class_='prod_name')
                        if not title_elem:
                            continue
                        title = title_elem.get_text(strip=True)
                        
                        # 提取價格
                        price_elem = item.find('b', class_='price') or item.find('span', class_='price')
                        if not price_elem:
                            continue
                        price = self.extract_price(price_elem.get_text(strip=True))
                        
                        if price == 0:
                            continue
                        
                        # 提取網址
                        url_elem = item.find('a')
                        url = url_elem.get('href', '') if url_elem else ''
                        if url and not url.startswith('http'):
                            url = 'https://24h.pchome.com.tw' + url
                        
                        listing = GameListing(
                            title=title,
                            price=price,
                            platform=self.detect_platform(title),
                            condition='全新',  # PChome多為全新商品
                            seller='PChome',
                            location='台灣',
                            url=url,
                            source='PChome 24h'
                        )
                        listings.append(listing)
                        
                    except Exception as e:
                        logger.warning(f"解析PChome項目時發生錯誤: {e}")
                        continue
            
            time.sleep(random.uniform(0.5, 1))
            
        except Exception as e:
            logger.error(f"搜尋PChome 24h時發生錯誤: {e}")
        
        return listings
    
    def search_all_platforms(self, game_name):
        """搜尋所有平台"""
        logger.info(f"開始搜尋遊戲: {game_name}")
        
        all_listings = []
        
        # 搜尋各個平台
        search_functions = [
            ('露天拍賣', self.search_ruten),
            ('蝦皮購物', self.search_shopee),
            ('Yahoo拍賣', self.search_yahoo_auction),
            ('PChome 24h', self.search_pchome_24h),
        ]
        
        for platform_name, search_func in search_functions:
            try:
                logger.info(f"正在搜尋 {platform_name}...")
                listings = search_func(game_name)
                
                if listings:
                    all_listings.extend(listings)
                    logger.info(f"{platform_name} 找到 {len(listings)} 個結果")
                else:
                    logger.info(f"{platform_name} 沒有找到結果")
                    
                # 在每個平台搜尋後休息
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                logger.error(f"搜尋 {platform_name} 時發生錯誤: {e}")
                continue
        
        # 過濾重複項目和異常價格
        unique_listings = []
        seen_titles = set()
        
        for listing in all_listings:
            # 簡化標題用於比較
            simple_title = re.sub(r'[^\w\s]', '', listing.title.lower())
            
            # 過濾異常價格（太低或太高）
            if listing.price < 10 or listing.price > 50000:
                continue
                
            # 避免重複
            if simple_title not in seen_titles:
                seen_titles.add(simple_title)
                unique_listings.append(listing)
        
        # 按價格排序
        unique_listings.sort(key=lambda x: x.price)
        
        logger.info(f"總共找到 {len(unique_listings)} 個去重後的結果")
        return unique_listings