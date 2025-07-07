import json
import re
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .utils import setup_chrome_driver, format_price_idr

class AliExpressScraper:
    def __init__(self):
        self.base_url = "https://www.aliexpress.com"
        
    def search_products(self, query, max_pages=3):
        driver = setup_chrome_driver()
        all_products = []
        
        try:
            for page in range(1, max_pages + 1):
                url = f"{self.base_url}/af/{query}.html?trafficChannel=af&d=y&CatId=0&SearchText={query}&ltype=affiliate&SortType=default&page={page}"
                driver.get(url)
                time.sleep(3)  # Wait for dynamic content
                
                # Extract product URLs from search results
                product_urls = self._extract_product_urls(driver)
                
                # Scrape individual product details
                for product_url in product_urls[:10]:  # Limit to 10 per page to avoid blocking
                    try:
                        product_data = self._scrape_product_details(product_url)
                        if product_data:
                            all_products.append(product_data)
                        time.sleep(1)  # Be respectful
                    except Exception as e:
                        print(f"Error scraping product: {e}")
                        continue
                        
        finally:
            driver.quit()
            
        return all_products
    
    def _extract_product_urls(self, driver):
        """Extract product URLs from search results page"""
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        product_urls = []
        
        # Find all product items
        for i in range(60):  # AliExpress typically shows up to 60 items
            product_items = soup.find_all('div', attrs={'product-index': i})
            if product_items:
                for item in product_items:
                    link = item.find('a')
                    if link and link.get('href'):
                        url = f"https:{link['href']}"
                        product_urls.append(url)
                        
        return product_urls
    
    def _scrape_product_details(self, url):
        """Scrape individual product details"""
        import requests
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return None
                
            # Extract JSON data from page
            match = re.search(r'data: ({.+})', response.text)
            if not match:
                return None
                
            data = json.loads(match.group(1))
            
            # Extract product information
            product = {
                'title': data.get('pageModule', {}).get('title', ''),
                'url': url,
                'img_url': data.get('pageModule', {}).get('imagePath', ''),
                'ref': 'aliexpress'
            }
            
            # Extract price
            price_module = data.get('priceModule', {})
            if 'formatedActivityPrice' in price_module:
                price_str = price_module['formatedActivityPrice']
            else:
                price_str = price_module.get('formatedPrice', '0')
            
            # Convert price to IDR
            product['price'] = self._parse_price(price_str)
            
            # Extract rating and reviews
            feedback = data.get('titleModule', {}).get('feedbackRating', {})
            product['rating'] = float(feedback.get('averageStar', 0))
            product['reviews'] = int(feedback.get('trialReviewNum', 0))
