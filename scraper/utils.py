import os
from dotenv import load_dotenv

load_dotenv()

def setup_chrome_driver():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    return webdriver.Chrome(options=chrome_options)

def format_price_idr(value):
    """Format price to IDR"""
    str_value = str(int(value))
    reversed_str = str_value[::-1]
    grouped = '.'.join([reversed_str[i:i+3] for i in range(0, len(reversed_str), 3)])
    return f"Rp {grouped[::-1]}"
