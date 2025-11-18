"""
Platform Detector - Auto-identifies e-commerce platform
Analyzes website to determine which specialized scraper to use
"""

import requests
from bs4 import BeautifulSoup
import re
import logging
from typing import Dict, Tuple
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class PlatformDetector:
    """Detects e-commerce platform and recommends scraper type"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def detect(self, url: str) -> Dict:
        """
        Detect platform and return scraping strategy
        
        Returns:
            {
                'platform': str,  # 'shopify', 'woocommerce', 'custom', etc.
                'scraper_type': str,  # 'api', 'selenium', 'beautifulsoup'
                'confidence': float,  # 0-1
                'details': dict,  # Additional platform-specific details
                'needs_js': bool  # Whether JavaScript rendering is required
            }
        """
        try:
            logger.info(f"Detecting platform for: {url}")
            
            # Fetch page
            response = self.session.get(url, timeout=15, allow_redirects=True)
            html = response.text
            soup = BeautifulSoup(html, 'lxml')
            
            # Run all detection methods
            detections = {
                'shopify': self._detect_shopify(url, html, soup, response),
                'woocommerce': self._detect_woocommerce(url, html, soup),
                'magento': self._detect_magento(url, html, soup),
                'bigcommerce': self._detect_bigcommerce(url, html, soup),
                'custom_api': self._detect_custom_api(url, html, soup),
                'js_heavy': self._detect_js_heavy(url, html, soup),
            }
            
            # Find best match
            best_match = max(detections.items(), key=lambda x: x[1]['confidence'])
            platform, result = best_match
            
            logger.info(f"Detected platform: {platform} (confidence: {result['confidence']:.2f})")
            
            return {
                'platform': platform,
                'scraper_type': result['scraper_type'],
                'confidence': result['confidence'],
                'details': result.get('details', {}),
                'needs_js': result.get('needs_js', False)
            }
            
        except Exception as e:
            logger.error(f"Error detecting platform: {e}")
            return {
                'platform': 'generic',
                'scraper_type': 'beautifulsoup',
                'confidence': 0.3,
                'details': {},
                'needs_js': False
            }
    
    def _detect_shopify(self, url: str, html: str, soup: BeautifulSoup, response) -> Dict:
        """Detect Shopify stores - HIGHEST PRIORITY from your scripts"""
        confidence = 0.0
        details = {}
        
        # Strong indicators (from beto_cosmetics.py pattern)
        if 'Shopify' in html or 'shopify' in html.lower():
            confidence += 0.3
        
        # Check for Shopify CDN
        if 'cdn.shopify.com' in html:
            confidence += 0.3
            details['has_shopify_cdn'] = True
        
        # Check for .myshopify.com domain
        if '.myshopify.com' in url:
            confidence += 0.4
            details['is_myshopify_domain'] = True
        
        # Check response headers
        if 'x-shopify-stage' in response.headers or 'x-shopify-shop-api-call-limit' in response.headers:
            confidence += 0.3
            details['shopify_headers'] = True
        
        # Check for Shopify.theme
        if re.search(r'Shopify\.theme', html):
            confidence += 0.2
        
        # Test for .json endpoint (Shopify's product API)
        if confidence > 0.3:
            try:
                # Try to access a typical Shopify JSON endpoint
                test_url = url.rstrip('/') + '.json'
                test_response = self.session.get(test_url, timeout=5)
                if test_response.status_code == 200 and 'product' in test_response.text.lower():
                    confidence = min(confidence + 0.4, 1.0)
                    details['has_json_api'] = True
            except:
                pass
        
        return {
            'confidence': min(confidence, 1.0),
            'scraper_type': 'api',  # Use Shopify JSON API
            'needs_js': False,
            'details': details
        }
    
    def _detect_woocommerce(self, url: str, html: str, soup: BeautifulSoup) -> Dict:
        """Detect WooCommerce (WordPress plugin)"""
        confidence = 0.0
        details = {}
        
        # Check for WooCommerce indicators
        if 'woocommerce' in html.lower():
            confidence += 0.4
            details['has_woocommerce_text'] = True
        
        # Check for WooCommerce CSS/JS
        if soup.find('link', href=re.compile(r'woocommerce.*\.css')) or \
           soup.find('script', src=re.compile(r'woocommerce.*\.js')):
            confidence += 0.3
            details['has_woocommerce_assets'] = True
        
        # Check for WordPress indicators
        if 'wp-content' in html or 'wp-includes' in html:
            confidence += 0.2
            details['is_wordpress'] = True
        
        # Check for WooCommerce classes
        woo_classes = ['woocommerce', 'product-type', 'woocommerce-product']
        if any(soup.find(class_=re.compile(cls)) for cls in woo_classes):
            confidence += 0.2
        
        return {
            'confidence': min(confidence, 1.0),
            'scraper_type': 'beautifulsoup',
            'needs_js': False,
            'details': details
        }
    
    def _detect_magento(self, url: str, html: str, soup: BeautifulSoup) -> Dict:
        """Detect Magento platform"""
        confidence = 0.0
        details = {}
        
        if 'magento' in html.lower():
            confidence += 0.4
        
        if soup.find('script', src=re.compile(r'mage/.*\.js')):
            confidence += 0.3
        
        if 'Mage.Cookies' in html or 'Magento' in html:
            confidence += 0.3
        
        return {
            'confidence': min(confidence, 1.0),
            'scraper_type': 'beautifulsoup',
            'needs_js': True,  # Magento often needs JS
            'details': details
        }
    
    def _detect_bigcommerce(self, url: str, html: str, soup: BeautifulSoup) -> Dict:
        """Detect BigCommerce"""
        confidence = 0.0
        details = {}
        
        if 'bigcommerce' in html.lower():
            confidence += 0.4
        
        if '.mybigcommerce.com' in url:
            confidence += 0.5
        
        return {
            'confidence': min(confidence, 1.0),
            'scraper_type': 'beautifulsoup',
            'needs_js': False,
            'details': details
        }
    
    def _detect_custom_api(self, url: str, html: str, soup: BeautifulSoup) -> Dict:
        """Detect if site has accessible JSON API (like DermStore pattern)"""
        confidence = 0.0
        details = {}
        
        # Look for patterns indicating API-based data loading
        api_patterns = [
            r'const\s+\w+\s*=\s*\[.*?\]',  # JavaScript array data
            r'window\.__INITIAL_STATE__',
            r'window\.__DATA__',
            r'const\s+trackedProducts',  # DermStore pattern
        ]
        
        for pattern in api_patterns:
            if re.search(pattern, html):
                confidence += 0.3
                details['has_embedded_json'] = True
                break
        
        # Check for API endpoints in HTML
        if re.search(r'/api/|/rest/|/graphql', html):
            confidence += 0.2
            details['has_api_endpoints'] = True
        
        return {
            'confidence': min(confidence, 1.0),
            'scraper_type': 'api',
            'needs_js': False,
            'details': details
        }
    
    def _detect_js_heavy(self, url: str, html: str, soup: BeautifulSoup) -> Dict:
        """
        Detect if site requires JavaScript rendering (like iHerb)
        This is checked if other detections fail
        """
        confidence = 0.0
        details = {}
        
        # Check if content is minimal (suggests JS rendering)
        text_content = soup.get_text(strip=True)
        if len(text_content) < 500:
            confidence += 0.3
            details['minimal_content'] = True
        
        # Check for React/Vue/Angular
        frameworks = {
            'react': r'react.*\.js|__REACT',
            'vue': r'vue.*\.js|Vue\.component',
            'angular': r'angular.*\.js|ng-app',
            'next': r'_next/|__NEXT_DATA__',
        }
        
        for fw, pattern in frameworks.items():
            if re.search(pattern, html, re.IGNORECASE):
                confidence += 0.4
                details[f'uses_{fw}'] = True
                break
        
        # Check for lazy loading indicators
        if 'data-src' in html or 'lazy-load' in html:
            confidence += 0.2
            details['has_lazy_loading'] = True
        
        return {
            'confidence': min(confidence, 1.0),
            'scraper_type': 'selenium',
            'needs_js': True,
            'details': details
        }
    
    def is_product_page(self, url: str) -> bool:
        """Check if URL is a product page"""
        product_patterns = [
            r'/product[s]?/',
            r'/item[s]?/',
            r'/p/',
            r'/dp/',
            r'-p-\d+',
        ]
        
        return any(re.search(pattern, url.lower()) for pattern in product_patterns)
    
    def is_category_page(self, url: str) -> bool:
        """Check if URL is a category/collection page"""
        category_patterns = [
            r'/categor[y|ies]/',
            r'/collection[s]?/',
            r'/c/',
            r'/shop/',
        ]
        
        return any(re.search(pattern, url.lower()) for pattern in category_patterns)


if __name__ == '__main__':
    # Test the detector
    detector = PlatformDetector()
    
    test_urls = [
        'https://betocosmetics.com/collections/skin-care',
        'https://www.dermstore.com/c/skin-care/',
        'https://gh.iherb.com/c/beauty',
    ]
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing: {url}")
        result = detector.detect(url)
        print(f"Platform: {result['platform']}")
        print(f"Scraper Type: {result['scraper_type']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Needs JS: {result['needs_js']}")
        print(f"Details: {result['details']}")

