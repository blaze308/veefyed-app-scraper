"""
Selenium Scraper - For JavaScript-heavy sites
Based on iHerb pattern from your scripts
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import uuid
import time
import random

logger = logging.getLogger(__name__)


class SeleniumScraper:
    """Specialized scraper for sites requiring JavaScript rendering"""
    
    def __init__(self, headless: bool = True):
        """
        Initialize Selenium scraper
        
        Args:
            headless: Run browser in headless mode
        """
        self.headless = headless
        self.driver = None
    
    def _init_driver(self):
        """Initialize undetected Chrome driver"""
        try:
            import undetected_chromedriver as uc
            from selenium.webdriver.common.by import By
            
            options = uc.ChromeOptions()
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            
            if self.headless:
                options.add_argument("--headless=new")
            
            self.driver = uc.Chrome(options=options)
            logger.info("Selenium driver initialized")
            
        except ImportError:
            logger.error("undetected-chromedriver not installed. Run: pip install undetected-chromedriver")
            raise
        except Exception as e:
            logger.error(f"Error initializing Selenium driver: {e}")
            raise
    
    def _human_sleep(self, min_sec: float = 2, max_sec: float = 5):
        """Random delay to mimic human behavior"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def _scroll_page(self, scrolls: int = 5):
        """Scroll page to trigger lazy loading"""
        from selenium.webdriver.common.by import By
        
        for _ in range(scrolls):
            self.driver.execute_script("window.scrollBy(0, window.innerHeight / 2);")
            time.sleep(0.3)
    
    def _close_popups(self):
        """Close any popups that might appear"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException
        
        popup_selectors = [
            (By.XPATH, "//button[contains(text(), 'Close')]"),
            (By.XPATH, "//button[contains(@class, 'close')]"),
            (By.XPATH, "//*[contains(@class, 'modal-close')]"),
            (By.XPATH, "//button[contains(@aria-label, 'Close')]"),
        ]
        
        for by, selector in popup_selectors:
            try:
                popup = WebDriverWait(self.driver, 2).until(
                    EC.element_to_be_clickable((by, selector))
                )
                popup.click()
                time.sleep(0.5)
                break
            except TimeoutException:
                continue
    
    def scrape_product(self, url: str) -> Optional[Dict]:
        """
        Scrape a single product page using Selenium
        
        Args:
            url: Product URL
            
        Returns:
            Product data dictionary
        """
        try:
            if not self.driver:
                self._init_driver()
            
            logger.info(f"Loading page with Selenium: {url}")
            self.driver.get(url)
            self._human_sleep(3, 5)
            self._scroll_page()
            self._close_popups()
            
            # Get page source after JS execution
            html = self.driver.page_source
            
            # Use BeautifulSoup to parse the rendered HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'lxml')
            
            # Extract product data (generic patterns)
            product_data = self._extract_product_data(soup, url)
            
            return product_data
            
        except Exception as e:
            logger.error(f"Error scraping with Selenium: {e}")
            return None
    
    def scrape_collection(self, url: str, max_products: int = 100) -> List[Dict]:
        """
        Scrape products from a collection/category page
        
        Args:
            url: Collection URL
            max_products: Maximum products to scrape
            
        Returns:
            List of product data dictionaries
        """
        products = []
        
        try:
            if not self.driver:
                self._init_driver()
            
            from selenium.webdriver.common.by import By
            from selenium.common.exceptions import NoSuchElementException
            
            page = 1
            while len(products) < max_products:
                # Build paginated URL
                if '?' in url:
                    page_url = f"{url}&page={page}"
                else:
                    page_url = f"{url}?page={page}"
                
                logger.info(f"Scraping collection page {page}: {page_url}")
                self.driver.get(page_url)
                self._human_sleep(3, 5)
                self._scroll_page(10)  # More scrolling for product lists
                
                # Find product elements (common selectors)
                product_selectors = [
                    '.product-item',
                    '.product-card',
                    '.product',
                    '[data-product]',
                    'article.product'
                ]
                
                found_products = []
                for selector in product_selectors:
                    try:
                        found_products = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if found_products:
                            break
                    except:
                        continue
                
                if not found_products:
                    logger.warning(f"No products found on page {page}")
                    break
                
                logger.info(f"Found {len(found_products)} products on page {page}")
                
                for elem in found_products:
                    if len(products) >= max_products:
                        break
                    
                    try:
                        # Extract basic product info from listing
                        product = self._extract_product_from_listing(elem)
                        if product:
                            products.append(product)
                    except Exception as e:
                        logger.debug(f"Error extracting product from listing: {e}")
                        continue
                
                page += 1
                self._human_sleep(5, 8)  # Longer delay between pages
            
            logger.info(f"Scraped {len(products)} products total")
            return products
            
        except Exception as e:
            logger.error(f"Error scraping collection: {e}")
            return products
    
    def _extract_product_data(self, soup, url: str) -> Dict:
        """Extract product data from rendered page"""
        
        # Common selectors (try multiple patterns)
        title_selectors = ['h1', '.product-title', '.product-name', '[itemprop="name"]']
        image_selectors = ['.product-image img', '[itemprop="image"]', '.main-image img']
        description_selectors = ['.product-description', '[itemprop="description"]', '.description']
        price_selectors = ['.price', '[itemprop="price"]', '.product-price']
        
        def find_first(selectors):
            for sel in selectors:
                elem = soup.select_one(sel)
                if elem:
                    return elem.get_text(strip=True) if elem.name != 'img' else elem.get('src', '')
            return ''
        
        # Extract all images
        images = []
        for img in soup.select('img'):
            src = img.get('src', '') or img.get('data-src', '')
            if src and any(x in src.lower() for x in ['product', 'item', 'image']):
                if src.startswith('//'):
                    src = 'https:' + src
                images.append(src)
        
        product_data = {
            'id': str(uuid.uuid4()),
            'product_name': find_first(title_selectors),
            'product_description': find_first(description_selectors),
            'product_id': str(uuid.uuid4().hex[:8]).upper(),
            'product_image_url': images[0] if images else '',
            'product_images': images[:10],  # Limit to 10
            'brand_name': '',
            'category': 'Skin Care',
            'subcategory': '',
            'product_type': 'Skincare',
            'package_size': '',
            'ingredients': '',
            'use_instructions': '',
            'benefits': '',
            'warnings': '',
            'barcode': '',
            'barcode_type': '',
            'product_line_name': '',
            'batch_number': '',
            'product_colour': '',
            'country_of_origin': '',
            'date_added': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'verification_status': 'pending',
            'verification_date': datetime.now().isoformat(),
            'source': 'Selenium Scraper',
            'source_url': url,
            'is_active': True,
            'is_new_product': True,
            'is_popular': False,
            'is_featured': False,
            'popularity_score': 0,
            'rating': 0.0,
            'review_count': 0,
            'stock_quantity': 0,
            'notes': 'Scraped with JavaScript rendering',
            'skin_type': '',
            'skin_concerns': '',
            'key_ingredients': '',
            'key_ingredients2': '',
            'key_ingredients3': '',
            'key_ingredients4': '',
            'key_ingredients5': '',
            'hero_ingredients_match': '',
            'precautions': '',
        }
        
        return product_data
    
    def _extract_product_from_listing(self, element) -> Optional[Dict]:
        """Extract basic product info from collection/category listing"""
        try:
            from selenium.webdriver.common.by import By
            from selenium.common.exceptions import NoSuchElementException
            
            title = ""
            url = ""
            image_url = ""
            
            # Try to find title and URL
            try:
                link = element.find_element(By.CSS_SELECTOR, 'a')
                url = link.get_attribute('href')
                title = link.get_attribute('title') or link.text.strip()
            except NoSuchElementException:
                pass
            
            # Try to find image
            try:
                img = element.find_element(By.CSS_SELECTOR, 'img')
                image_url = img.get_attribute('src') or img.get_attribute('data-src')
                if image_url and image_url.startswith('//'):
                    image_url = 'https:' + image_url
            except NoSuchElementException:
                pass
            
            if not title or not url:
                return None
            
            return {
                'id': str(uuid.uuid4()),
                'product_name': title,
                'product_image_url': image_url,
                'source_url': url,
                'date_added': datetime.now().isoformat(),
            }
            
        except Exception as e:
            return None
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("Selenium driver closed")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close()


if __name__ == '__main__':
    # Test the scraper
    scraper = SeleniumScraper(headless=False)
    
    try:
        test_url = "https://gh.iherb.com/c/beauty"
        products = scraper.scrape_collection(test_url, max_products=5)
        
        print(f"✅ Scraped {len(products)} products")
        for p in products:
            print(f"  - {p.get('product_name', 'Unknown')}")
    finally:
        scraper.close()

