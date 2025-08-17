from flask import Flask, request, jsonify, render_template
from scraper import GamePriceScraper
import logging
import os

app = Flask(__name__)

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 設定Flask配置
app.config['JSON_AS_ASCII'] = False  # 支援中文JSON回應

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '無效的請求格式'}), 400
            
        game_name = data.get('game_name', '').strip()
        
        if not game_name:
            return jsonify({'error': '請輸入遊戲名稱'}), 400
        
        if len(game_name) < 2:
            return jsonify({'error': '遊戲名稱至少需要2個字元'}), 400
            
        logger.info(f"開始搜尋遊戲: {game_name}")
        
        scraper = GamePriceScraper()
        listings = scraper.search_all_platforms(game_name)
        
        # 轉換為字典格式
        results = []
        for listing in listings:
            results.append({
                'title': listing.title,
                'price': listing.price,
                'platform': listing.platform,
                'condition': listing.condition,
                'seller': listing.seller,
                'location': listing.location,
                'source': listing.source,
                'url': listing.url,
                'posted_time': listing.posted_time,
                'seller_rating': listing.seller_rating
            })
        
        logger.info(f"搜尋完成，找到 {len(results)} 個結果")
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results),
            'search_term': game_name
        })
        
    except Exception as e:
        logger.error(f"搜尋錯誤: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'搜尋過程中發生錯誤: {str(e)}',
            'success': False
        }), 500

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Game Price Scraper',
        'version': '1.0.0'
    })

@app.route('/api/platforms')
def get_platforms():
    """回傳支援的平台列表"""
    platforms = [
        {'name': '露天拍賣', 'code': 'ruten'},
        {'name': '蝦皮購物', 'code': 'shopee'},
        {'name': 'Yahoo拍賣', 'code': 'yahoo'},
        {'name': 'PChome 24h', 'code': 'pchome'}
    ]
    return jsonify({'platforms': platforms})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': '找不到請求的資源'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '伺服器內部錯誤'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=debug_mode
    )