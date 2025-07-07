import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .utils import setup_chrome_driver

class AmazonScraper:
    def __init__(self):
        self.base_url = "https://www.amazon.com"
        
    def search_products(self, query, max_pages=3):
        driver = setup_chrome_driver()
        products = []
        
        try:
            # Navigate to Amazon
            print(f"Loading Amazon homepage...")
            driver.get(self.base_url)
            
            # Take a screenshot for debugging
            driver.save_screenshot('amazon_homepage.png')
            print("Screenshot saved as amazon_homepage.png")
            
            # Wait for page to load and handle different possible search box selectors
            wait = WebDriverWait(driver, 15)
            
            # Try different possible selectors for the search box
            search_box = None
            search_selectors = [
                (By.ID, "twotabsearchtextbox"),
                (By.NAME, "field-keywords"),
                (By.CSS_SELECTOR, "input[type='text'][id*='search']"),
                (By.CSS_SELECTOR, "input[placeholder*='Search']"),
            ]
            
            for by, selector in search_selectors:
                try:
                    print(f"Trying selector: {by} = {selector}")
                    search_box = wait.until(EC.presence_of_element_located((by, selector)))
                    print(f"Found search box with selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not search_box:
                # Print page source for debugging
                print("Could not find search box. Page title:", driver.title)
                print("Current URL:", driver.current_url)
                raise Exception("Could not find search box on Amazon")
            
            # Enter search query
            search_box.clear()
            search_box.send_keys(query)
            
            # Try different methods to submit the search
            try:
                # Method 1: Find and click search button
                search_button = driver.find_element(By.ID, "nav-search-submit-button")
                search_button.click()
            except:
                try:
                    # Method 2: Submit the form
                    search_box.submit()
                except:
                    # Method 3: Press Enter
                    from selenium.webdriver.common.keys import Keys
                    search_box.send_keys(Keys.RETURN)
            
            # Wait for search results
            print("Waiting for search results...")
            time.sleep(3)
            
            # Extract products from multiple pages
            for page in range(max_pages):
                print(f"Extracting products from page {page + 1}")
                products.extend(self._extract_products(driver))
                
                if page < max_pages - 1:
                    try:
                        # Try to find next button
                        next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.s-pagination-next")))
                        driver.execute_script("arguments[0].click();", next_button)
                        time.sleep(2)
                    except:
                        print("No more pages available")
                        break
                    
        except Exception as e:
            print(f"Error during Amazon scraping: {str(e)}")
            driver.save_screenshot('amazon_error.png')
            print("Error screenshot saved as amazon_error.png")
            
        finally:
            driver.quit()
            
        return products
    
    def _extract_products(self, driver):
        products = []
        
        # Updated selectors for current Amazon layout
        item_selectors = [
            "[data-component-type='s-search-result']",
            "[data-asin]:not([data-asin=''])",
            ".s-result-item[data-asin]"
        ]
        
        items = []
        for selector in item_selectors:
            items = driver.find_elements(By.CSS_SELECTOR, selector)
            if items:
                print(f"Found {len(items)} items with selector: {selector}")
                break
        
        for item in items[:10]:  # Limit to 10 items per page
            try:
                product = {}
                
                # Title - try multiple selectors
                title_selectors = [
                    "h2 a span",
                    "h2 span",
                    ".a-size-base-plus",
                    ".a-size-medium"
                ]
                for selector in title_selectors:
                    try:
                        product['title'] = item.find_element(By.CSS_SELECTOR, selector).text
                        break
                    except:
                        continue
                
                # Price - try multiple selectors
                price_selectors = [
                    ".a-price-whole",
                    ".a-price .a-offscreen",
                    ".a-price-range",
                    "[data-a-color='base'] .a-price"
                ]
                for selector in price_selectors:
                    try:
                        price_elem = item.find_element(By.CSS_SELECTOR, selector)
                        product['price'] = price_elem.text or price_elem.get_attribute('textContent')
                        break
                    except:
                        continue
                
                # Rating
                try:
                    rating_elem = item.find_element(By.CSS_SELECTOR, ".a-icon-alt")
                    product['rating'] = rating_elem.get_attribute('textContent').split()[0]
                except:
                    product['rating'] = "0"
                
                # Reviews count
                try:
                    reviews_elem = item.find_element(By.CSS_SELECTOR, "[aria-label*='stars']")
                    reviews_text = reviews_elem.get_attribute('aria-label')
                    product['reviews'] = ''.join(filter(str.isdigit, reviews_text.split(',')[1]))
                except:
                    product['reviews'] = "0"
                
                # URL
                try:
                    link_elem = item.find_element(By.CSS_SELECTOR, "h2 a")
                    product['url'] = link_elem.get_attribute("href")
                except:
                    product['url'] = "#"
                
                # Image
                try:
                    img_elem = item.find_element(By.CSS_SELECTOR, "img.s-image")
                    product['img_url'] = img_elem.get_attribute("src")
                except:
                    product['img_url'] = ""
                
                product['ref'] = 'amazon'
                
                # Only add if we have at least title and price
                if product.get('title') and product.get('price'):
                    products.append(product)
                    print(f"Extracted: {product['title'][:50]}...")
                    
            except Exception as e:
                print(f"Error extracting product: {str(e)}")
                continue
                
        return products