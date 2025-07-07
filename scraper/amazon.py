import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .utils import setup_chrome_driver

class AmazonScraper:
    def __init__(self):
        self.base_url = "https://www.amazon.com"
        
    def search_products(self, query, max_pages=3):
        driver = setup_chrome_driver()
        products = []
        
        try:
            driver.get(self.base_url)
            search_box = driver.find_element(By.ID, "twotabsearchtextbox")
            search_box.send_keys(query)
            search_box.submit()
            
            for page in range(max_pages):
                time.sleep(2)  # Be respectful
                products.extend(self._extract_products(driver))
                
                try:
                    next_button = driver.find_element(By.CLASS_NAME, "s-pagination-next")
                    if "disabled" not in next_button.get_attribute("class"):
                        next_button.click()
                    else:
                        break
                except:
                    break
                    
        finally:
            driver.quit()
            
        return products
    
    def _extract_products(self, driver):
        products = []
        items = driver.find_elements(By.CSS_SELECTOR, "[data-component-type='s-search-result']")
        
        for item in items:
            try:
                product = {
                    'title': item.find_element(By.CSS_SELECTOR, "h2 a span").text,
                    'price': item.find_element(By.CSS_SELECTOR, ".a-price-whole").text,
                    'rating': item.find_element(By.CSS_SELECTOR, ".a-icon-alt").text.split()[0],
                    'url': item.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href"),
                    'img_url': item.find_element(By.CSS_SELECTOR, "img.s-image").get_attribute("src"),
                    'ref': 'amazon'
                }
                products.append(product)
            except:
                continue
                
        return products
