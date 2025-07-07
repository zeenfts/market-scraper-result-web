import os
from flask import Flask, render_template, jsonify, request
from scraper.amazon import AmazonScraper
from scraper.aliexpress import AliExpressScraper
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Cache for storing scraped data
CACHE_FILE = 'data/products_cache.json'

def load_cached_products():
    """Load products from cache file"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return []

def save_products_to_cache(products):
    """Save products to cache file"""
    os.makedirs('data', exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(products, f)

@app.route('/')
def index():
    # Load cached products or use dummy data
    products = load_cached_products()
    if not products:
        products = [
            {
                'title': 'LG French Door Refrigerator',
                'price': 'Rp 15.000.000',
                'rating': 4.5,
                'reviews': 120,
                'img_url': 'https://via.placeholder.com/300x200?text=Refrigerator',
                'url': '#',
                'ref': 'amazon'
            },
            {
                'title': 'Samsung Smart Refrigerator',
                'price': 'Rp 18.500.000',
                'rating': 4.7,
                'reviews': 89,
                'img_url': 'https://via.placeholder.com/300x200?text=Smart+Fridge',
                'url': '#',
                'ref': 'aliexpress'
            }
        ]
    
    # Sort by rating and reviews
    products.sort(key=lambda x: (x.get('rating', 0), x.get('reviews', 0)), reverse=True)
    
    return render_template('index.html', products=products)

@app.route('/api/scrape')
def scrape():
    query = request.args.get('query', 'refrigerator')
    source = request.args.get('source', 'both')
    
    products = []
    
    try:
        if source in ['amazon', 'both']:
            amazon = AmazonScraper()
            amazon_products = amazon.search_products(query, max_pages=2)
            products.extend(amazon_products)
        
        if source in ['aliexpress', 'both']:
            aliexpress = AliExpressScraper()
            aliexpress_products = aliexpress.search_products(query, max_pages=2)
            products.extend(aliexpress_products)
        
        # Save to cache
        if products:
            save_products_to_cache(products)
        
        return jsonify({
            'success': True,
            'count': len(products),
            'products': products
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/products')
def get_products():
    """Get cached products"""
    products = load_cached_products()
    return jsonify(products)

if __name__ == '__main__':
    app.run(debug=True)
