"""
Shopify Scraper - Uses Shopify's JSON API
Based on beto_cosmetics.py pattern from your scripts
"""

import requests
from bs4 import BeautifulSoup
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class ShopifyScraper:
    """Specialized scraper for Shopify stores using JSON API"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_product(self, url: str) -> Optional[Dict]:
        """
        Scrape a single Shopify product using .json endpoint
        
        Args:
            url: Product URL
            
        Returns:
            Product data dictionary matching your Product model
        """
        try:
            # Convert product URL to JSON API endpoint
            json_url = self._get_json_url(url)
            
            logger.info(f"Fetching Shopify JSON: {json_url}")
            response = self.session.get(json_url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if 'product' in data:
                return self._parse_product(data['product'], url)
            else:
                logger.error("No 'product' key in JSON response")
                return None
                
        except Exception as e:
            logger.error(f"Error scraping Shopify product {url}: {e}")
            return None
    
    def scrape_collection(self, url: str, max_products: int = 100) -> List[Dict]:
        """
        Scrape products from a Shopify collection
        
        Args:
            url: Collection URL
            max_products: Maximum products to scrape
            
        Returns:
            List of product data dictionaries
        """
        products = []
        
        try:
            # Get collection products via API
            collection_slug = self._get_collection_slug(url)
            base_url = self._get_base_url(url)
            
            page = 1
            while len(products) < max_products:
                # Shopify collections support pagination
                api_url = f"{base_url}/collections/{collection_slug}/products.json?page={page}&limit=250"
                
                logger.info(f"Fetching collection page {page}: {api_url}")
                response = self.session.get(api_url, timeout=15)
                
                if response.status_code != 200:
                    logger.warning(f"API returned status {response.status_code}, stopping pagination")
                    break
                
                data = response.json()
                page_products = data.get('products', [])
                
                logger.info(f"Page {page}: Found {len(page_products)} products, total so far: {len(products)}")
                
                if not page_products:
                    logger.info(f"No more products found on page {page}, stopping pagination")
                    break
                
                for product_data in page_products:
                    if len(products) >= max_products:
                        break
                    
                    product = self._parse_product(product_data, None)
                    if product:
                        products.append(product)
                
                page += 1
            
            logger.info(f"Scraped {len(products)} products from collection")
            return products
            
        except Exception as e:
            logger.error(f"Error scraping collection {url}: {e}")
            return products
    
    def _get_json_url(self, url: str) -> str:
        """Convert product URL to JSON API endpoint"""
        # Remove query parameters and fragments
        clean_url = url.split('?')[0].split('#')[0]
        
        # If already has .json, return as is
        if clean_url.endswith('.json'):
            return clean_url
        
        # Add .json extension
        return clean_url.rstrip('/') + '.json'
    
    def _get_base_url(self, url: str) -> str:
        """Extract base URL from any Shopify URL"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def _get_collection_slug(self, url: str) -> str:
        """Extract collection slug from URL"""
        # Extract from /collections/[slug] pattern
        parts = url.split('/collections/')
        if len(parts) > 1:
            slug = parts[1].split('/')[0].split('?')[0]
            return slug
        return 'all'
    
    def _parse_product(self, product: Dict, url: Optional[str]) -> Dict:
        """
        Parse Shopify JSON product data to match your Product model
        
        Args:
            product: Raw Shopify product JSON
            url: Original product URL (if available)
            
        Returns:
            Formatted product data
        """
        try:
            # Get first variant (default)
            variant = product.get('variants', [{}])[0]
            
            # Parse HTML description
            html_description = product.get('body_html', '')
            soup = BeautifulSoup(html_description, 'html.parser')
            
            # Extract ingredients and instructions from HTML
            ingredients_text = ""
            instructions_text = ""
            benefits_text = ""
            warnings_text = ""
            
            for heading in soup.find_all(['h3', 'h4', 'h5', 'strong']):
                heading_text = heading.get_text().lower()
                next_elem = heading.find_next(['p', 'ul', 'ol', 'div'])
                
                if next_elem:
                    content = next_elem.get_text(strip=True)
                    
                    if 'ingredient' in heading_text:
                        ingredients_text = content
                    elif 'how to use' in heading_text or 'directions' in heading_text:
                        instructions_text = content
                    elif 'benefit' in heading_text:
                        benefits_text = content
                    elif 'warning' in heading_text or 'caution' in heading_text:
                        warnings_text = content
            
            # Get all image URLs
            image_urls = []
            for img in product.get('images', []):
                img_url = img.get('src', '')
                if img_url:
                    # Ensure full URL
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    image_urls.append(img_url)
            
            # Build product URL if not provided
            if not url and product.get('handle'):
                # We don't have the base domain, so use handle as identifier
                url = f"/products/{product['handle']}"
            
            # Format data to match your Product model
            product_data = {
                'id': str(uuid.uuid4()),
                'product_name': product.get('title', ''),
                'product_description': soup.get_text(separator=' ', strip=True) if html_description else '',
                'product_id': str(product.get('id', '')),
                'product_image_url': image_urls[0] if image_urls else '',
                'product_images': image_urls,  # All images
                'brand_name': product.get('vendor', ''),
                'category': 'Skin Care',  # Default, can be overridden
                'subcategory': product.get('product_type', ''),
                'product_type': product.get('product_type', 'Skincare'),
                'package_size': variant.get('title', ''),
                'ingredients': ingredients_text,
                'use_instructions': instructions_text,
                'benefits': benefits_text,
                'warnings': warnings_text,
                'barcode': variant.get('barcode') or variant.get('sku', ''),
                'barcode_type': 'EAN-13' if variant.get('barcode') else '',
                'product_line_name': '',
                'batch_number': '',
                'product_colour': variant.get('option1', '') if 'color' in str(variant.get('option1', '')).lower() else '',
                'country_of_origin': '',
                'date_added': datetime.now().isoformat(),
                'created_at': product.get('created_at', datetime.now().isoformat()),
                'updated_at': product.get('updated_at', datetime.now().isoformat()),
                'verification_status': 'pending',
                'verification_date': datetime.now().isoformat(),
                'source': 'Shopify Scraper',
                'source_url': url or '',
                'is_active': True,
                'is_new_product': True,
                'is_popular': False,
                'is_featured': False,
                'popularity_score': 0,
                'rating': 0.0,
                'review_count': 0,
                'stock_quantity': variant.get('inventory_quantity', 0),
                'notes': f"Shopify Product ID: {product.get('id')}",
                
                # Skincare-specific fields (extracted from description)
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
            
            # Try to extract key ingredients from ingredients list
            if ingredients_text:
                ingredient_list = [i.strip() for i in ingredients_text.split(',')]
                for i, ingredient in enumerate(ingredient_list[:5], 1):
                    product_data[f'key_ingredients{i if i > 1 else ""}'] = ingredient
            
            logger.info(f"Parsed Shopify product: {product_data['product_name']}")
            return product_data
            
        except Exception as e:
            logger.error(f"Error parsing Shopify product: {e}")
            return None


if __name__ == '__main__':
    # Test the scraper
    scraper = ShopifyScraper()
    
    # Test with a Shopify product URL
    test_url = "https://betocosmetics.com/products/facial-serum"
    result = scraper.scrape_product(test_url)
    
    if result:
        print("✅ Successfully scraped Shopify product!")
        print(f"Product: {result['product_name']}")
        print(f"Brand: {result['brand_name']}")
        print(f"Images: {len(result['product_images'])} found")
    else:
        print("❌ Failed to scrape product")

