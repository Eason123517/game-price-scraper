import os
from datetime import timedelta

class Config:
    """基礎配置"""
    # Flask 設定
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    JSON_AS_ASCII = False  # 支援中文 JSON
    
    # 爬蟲設定
    REQUEST_TIMEOUT = 30  # 請求超時時間（秒）
    MAX_RETRIES = 3      # 最大重試次數
    RETRY_DELAY = 2      # 重試延遲時間（秒）
    
    # Selenium 設定
    SELENIUM_TIMEOUT = 10        # Selenium 等待超時時間
    SELENIUM_IMPLICIT_WAIT = 5   # 隱式等待時間
    
    # 搜尋限制
    MAX_RESULTS_PER_PLATFORM = 10  # 每個平台最大結果數
    MIN_PRICE_FILTER = 10          # 最低價格過濾
    MAX_PRICE_FILTER = 50000       # 最高價格過濾
    
    # 快取設定
    CACHE_TIMEOUT = timedelta(minutes=30)  # 快取超時時間
    
    # User Agent 池
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
    ]
    
    # 平台設定
    PLATFORMS = {
        'ruten': {
            'name': '露天拍賣',
            'enabled': True,
            'priority': 1
        },
        'shopee': {
            'name': '蝦皮購物',
            'enabled': True,
            'priority': 2
        },
        'yahoo': {
            'name': 'Yahoo拍賣',
            'enabled': True,
            'priority': 3
        },
        'pchome': {
            'name': 'PChome 24h',
            'enabled': True,
            'priority': 4
        }
    }

class DevelopmentConfig(Config):
    """開發環境配置"""
    DEBUG = True
    ENV = 'development'
    
    # 開發環境下的設定
    REQUEST_TIMEOUT = 60
    MAX_RESULTS_PER_PLATFORM = 5  # 開發時減少結果數量
    
class ProductionConfig(Config):
    """生產環境配置"""
    DEBUG = False
    ENV = 'production'
    
    # 生產環境安全設定
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 性能設定
    REQUEST_TIMEOUT = 45
    MAX_RETRIES = 2

class TestingConfig(Config):
    """測試環境配置"""
    TESTING = True
    ENV = 'testing'
    
    # 測試環境設定
    REQUEST_TIMEOUT = 10
    MAX_RESULTS_PER_PLATFORM = 2

# 配置映射
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """根據環境變數獲取配置"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config_map.get(env, config_map['default'])