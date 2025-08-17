from flask import Flask, request, jsonify, render_template
from scraper import GamePriceScraper
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        game_name = request.json.get('game_name', '').strip()
        
        if not game_name:
            return jsonify({'error': '請輸入遊戲名稱'}), 400
        
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
                'url': listing.url
            })
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        logging.error(f"搜尋錯誤: {e}")
        return jsonify({'error': f'搜尋過程中發生錯誤: {str(e)}'}), 500

@app.route('/health')
def health_check():
    return {'status': 'healthy'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)