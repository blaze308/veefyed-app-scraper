"""
Smart Scraping Engine - Swiss Army Knife Edition
Auto-detects platforms and routes to specialized scrapers
"""

import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import re
import uuid

# Import specialized scrapers
from modules.platform_detector import PlatformDetector
from modules.shopify_scraper import ShopifyScraper
from modules.selenium_scraper import SeleniumScraper
from modules.onedrive_uploader import get_uploader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ScraperEngine:
    """
    Smart scraping engine that:
    1. Detects platform type
    2. Routes to appropriate specialized scraper
    3. Handles image uploads to OneDrive
    4. Returns data matching Product model
    """
    
    def __init__(self, pattern_library_path: str = 'modules/pattern_library.json', 
                 use_onedrive: bool = True):
        """Initialize the smart scraper"""
        self.patterns = self._load_patterns(pattern_library_path)
        self.session = requests.Session()
        
        # Initialize components
        self.detector = PlatformDetector()
        self.shopify_scraper = ShopifyScraper()
        self.selenium_scraper = None  # Lazy initialization
        self.onedrive_uploader = None
        self.use_onedrive = use_onedrive
        
        # Try to initialize OneDrive
        if use_onedrive:
            try:
                self.onedrive_uploader = get_uploader()
                if self.onedrive_uploader and self.onedrive_uploader.is_enabled():
                    logger.info("OneDrive integration enabled")
                else:
                    logger.warning("OneDrive not configured - images will not be uploaded")
                    logger.warning("Check logs above for authentication error details")
                    logger.warning("You can still scrape without OneDrive - images will use original URLs")
                    self.use_onedrive = False
            except Exception as e:
                logger.warning(f"OneDrive initialization failed: {e}")
                logger.warning("Scraping will continue without OneDrive uploads")
                self.use_onedrive = False
        
    def _load_patterns(self, path: str) -> Dict:
        """Load pattern library from JSON file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading pattern library: {e}")
            return {}
    
    def fetch(self, url: str, headers: Optional[Dict] = None) -> Optional[str]:
        """
        Fetch HTML content from URL
        
        Args:
            url: Target URL to scrape
            headers: Optional custom headers
            
        Returns:
            HTML content as string or None if error
        """
        try:
            default_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            if headers:
                default_headers.update(headers)
            
            logger.info(f"Fetching URL: {url}")
            response = self.session.get(url, headers=default_headers, timeout=30)
            response.raise_for_status()
            logger.info(f"Successfully fetched {url} - Status: {response.status_code}")
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def parse(self, html: str, pattern_name: str) -> Dict[str, Any]:
        """
        Parse HTML using specified pattern
        
        Args:
            html: HTML content to parse
            pattern_name: Name of pattern from pattern library
            
        Returns:
            Dictionary of extracted product data
        """
        if pattern_name not in self.patterns:
            logger.warning(f"Pattern '{pattern_name}' not found, using generic")
            pattern_name = 'generic_ecommerce'
        
        pattern = self.patterns[pattern_name]
        soup = BeautifulSoup(html, 'lxml')
        
        # Initialize product data matching the Dart Product model
        product_data = {
            'id': str(uuid.uuid4()),
            'product_name': '',
            'product_description': '',
            'product_id': '',
            'product_image_url': '',
            'product_images': [],
            'brand_name': '',
            'ingredients': '',
            'package_size': '',
            'barcode': '',
            'barcode_type': 'EAN-13',
            'category': '',
            'subcategory': '',
            'product_type': 'Skincare',
            'rating': 0.0,
            'review_count': 0,
            'stock_quantity': 0,
            'use_instructions': '',
            'warnings': '',
            'precautions': '',
            'skin_type': '',
            'skin_concerns': '',
            'benefits': '',
            'key_ingredients': '',
            'key_ingredients2': '',
            'key_ingredients3': '',
            'key_ingredients4': '',
            'key_ingredients5': '',
            'country_of_origin': '',
            'product_colour': '',
            'product_line_name': '',
            'batch_number': '',
            'notes': '',
            'source': 'Web Scraper',
            'verification_status': 'pending',
            'verification_date': datetime.now().isoformat(),
            'date_added': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'is_active': True,
            'is_new_product': True,
            'is_popular': False,
            'is_featured': False,
            'popularity_score': 0,
            'hero_ingredients_match': ''
        }
        
        # Extract data using selectors from pattern
        selectors = pattern.get('selectors', {})
        
        for field, selector_list in selectors.items():
            value = self._extract_field(soup, selector_list, field)
            if value and field in product_data:
                product_data[field] = value
        
        # Generate product_id if not found
        if not product_data['product_id']:
            product_data['product_id'] = f"SCRP-{uuid.uuid4().hex[:8].upper()}"
        
        logger.info(f"Extracted product: {product_data['product_name'][:50]}")
        return product_data
    
    def _extract_field(self, soup: BeautifulSoup, selectors: List[str], field_name: str) -> Any:
        """
        Extract a single field using multiple selector options
        
        Args:
            soup: BeautifulSoup object
            selectors: List of CSS selectors to try
            field_name: Name of the field being extracted
            
        Returns:
            Extracted value or empty string/list
        """
        for selector in selectors:
            try:
                # Handle image arrays
                if 'images' in field_name:
                    elements = soup.select(selector)
                    if elements:
                        images = [img.get('src', '') or img.get('data-src', '') 
                                 for img in elements if img.name == 'img']
                        return [img for img in images if img][:10]  # Limit to 10 images
                
                # Handle single image
                if 'image' in field_name:
                    element = soup.select_one(selector)
                    if element:
                        if element.name == 'img':
                            return element.get('src', '') or element.get('data-src', '')
                        else:
                            img = element.find('img')
                            if img:
                                return img.get('src', '') or img.get('data-src', '')
                
                # Handle rating (extract numeric value)
                if 'rating' in field_name:
                    element = soup.select_one(selector)
                    if element:
                        text = element.get_text(strip=True)
                        match = re.search(r'(\d+\.?\d*)', text)
                        if match:
                            return float(match.group(1))
                
                # Handle counts (review_count, stock_quantity)
                if 'count' in field_name or 'quantity' in field_name:
                    element = soup.select_one(selector)
                    if element:
                        text = element.get_text(strip=True)
                        match = re.search(r'(\d+)', text.replace(',', ''))
                        if match:
                            return int(match.group(1))
                
                # Handle text content
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text:
                        return text
                        
            except Exception as e:
                logger.debug(f"Error with selector '{selector}' for {field_name}: {e}")
                continue
        
        # Return appropriate default based on field type
        if 'images' in field_name:
            return []
        elif 'rating' in field_name:
            return 0.0
        elif 'count' in field_name or 'quantity' in field_name:
            return 0
        else:
            return ''
    
    def scrape(self, url: str, pattern_name: str = None) -> Optional[Dict]:
        """
        Smart scrape operation:
        1. Detect platform
        2. Route to appropriate scraper
        3. Upload images to OneDrive
        4. Return formatted data
        
        Args:
            url: Target URL
            pattern_name: Optional manual override
            
        Returns:
            Extracted product data with detection info
        """
        try:
            logger.info(f"🔍 Starting smart scrape for: {url}")
            
            # Step 1: Detect platform
            detection = self.detector.detect(url)
            logger.info(f"✅ Detected: {detection['platform']} (confidence: {detection['confidence']:.0%})")
            
            # Step 2: Route to appropriate scraper
            product_data = None
            
            if detection['platform'] == 'shopify' and detection['confidence'] > 0.5:
                logger.info("→ Using Shopify API scraper")
                product_data = self.shopify_scraper.scrape_product(url)
                
            elif detection['needs_js'] or detection['scraper_type'] == 'selenium':
                logger.info("→ Using Selenium scraper (JS rendering)")
                if not self.selenium_scraper:
                    self.selenium_scraper = SeleniumScraper(headless=True)
                product_data = self.selenium_scraper.scrape_product(url)
                
            else:
                logger.info("→ Using generic scraper")
                product_data = self._generic_scrape(url)
            
            if not product_data:
                logger.error("❌ No data extracted")
                return None
            
            # Step 3: Upload images to OneDrive
            if self.use_onedrive and self.onedrive_uploader:
                product_data = self._process_images(product_data)
            
            # Step 4: Add detection metadata
            product_data['detection_info'] = {
                'detected_platform': detection['platform'],
                'scraper_used': detection['scraper_type'],
                'confidence': detection['confidence'],
                'needs_js': detection['needs_js']
            }
            
            logger.info(f"✅ Successfully scraped: {product_data['product_name'][:50]}")
            return product_data
            
        except Exception as e:
            logger.error(f"❌ Error scraping {url}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _generic_scrape(self, url: str) -> Optional[Dict]:
        """Generic scraper for sites without specialized handler"""
        try:
            html = self.fetch(url)
            if not html:
                return None
            
            # Use the old parse method as fallback
            return self.parse(html, 'ecommerce_skincare')
            
        except Exception as e:
            logger.error(f"Generic scrape failed: {e}")
            return None
    
    def _process_images(self, product_data: Dict) -> Dict:
        """Upload images to OneDrive and update URLs"""
        try:
            category = product_data.get('category', 'products')
            
            # Process main image
            if product_data.get('product_image_url'):
                logger.info("📤 Uploading main image to OneDrive...")
                onedrive_link = self.onedrive_uploader.process_and_upload_image(
                    product_data['product_image_url'],
                    category
                )
                if onedrive_link:
                    product_data['product_image_url'] = onedrive_link
                    logger.info("✅ Main image uploaded")
            
            # Process gallery images
            if product_data.get('product_images') and isinstance(product_data['product_images'], list):
                logger.info(f"📤 Uploading {len(product_data['product_images'])} gallery images...")
                onedrive_links = self.onedrive_uploader.process_multiple_images(
                    product_data['product_images'],
                    category
                )
                # Filter out empty strings (failed uploads)
                product_data['product_images'] = [link for link in onedrive_links if link]
                logger.info(f"✅ Uploaded {len(product_data['product_images'])} images")
            
            return product_data
            
        except Exception as e:
            logger.warning(f"⚠️ Image upload failed: {e}")
            return product_data
    
    def save_to_json(self, data: Dict, output_path: str) -> bool:
        """Save scraped data to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved data to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
            return False
    
    def save_to_csv(self, data: List[Dict], output_path: str) -> bool:
        """Save scraped data to CSV file"""
        try:
            import csv
            
            if not data:
                logger.warning("No data to save")
                return False
            
            # Convert single dict to list
            if isinstance(data, dict):
                data = [data]
            
            keys = data[0].keys()
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
            
            logger.info(f"Saved {len(data)} products to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            return False


if __name__ == '__main__':
    # Test the scraper
    scraper = ScraperEngine()
    print("Scraper Engine initialized successfully")
    print(f"Loaded {len(scraper.patterns)} patterns")

