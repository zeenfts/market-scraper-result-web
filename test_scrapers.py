from scraper.amazon import AmazonScraper
from scraper.aliexpress import AliExpressScraper

def test_amazon():
    print("Testing Amazon scraper...")
    scraper = AmazonScraper()
    products = scraper.search_products("laptop", max_pages=1)
    print(f"Found {len(products)} products from Amazon")
    if products:
        print("Sample product:", products[0])
    return products

def test_aliexpress():
    print("\nTesting AliExpress scraper...")
    scraper = AliExpressScraper()
    products = scraper.search_products("laptop", max_pages=1)
    print(f"Found {len(products)} products from AliExpress")
    if products:
        print("Sample product:", products[0])
    return products

if __name__ == "__main__":
    # Test individually first
    amazon_products = test_amazon()
    # aliexpress_products = test_aliexpress()
