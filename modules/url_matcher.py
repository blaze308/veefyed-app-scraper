"""
URL Pattern Matcher
Matches URLs to appropriate scraping patterns
"""

import re
from typing import Tuple, Optional
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class URLMatcher:
    """Matches URLs to scraping patterns based on domain and structure"""
    
    def __init__(self):
        """Initialize URL matcher with domain patterns"""
        self.domain_patterns = {
            'amazon': ['amazon.com', 'amazon.co.uk', 'amazon.ca', 'amazon.de'],
            'shopify': ['myshopify.com'],
            'ecommerce_skincare': [
                'skincare', 'beauty', 'cosmetics', 'wellness',
                'dermstore', 'sephora', 'ulta', 'beautybay'
            ]
        }
        
        self.pattern_priority = [
            'amazon_products',
            'shopify_store',
            'ecommerce_skincare',
            'generic_ecommerce'
        ]
    
    def match(self, url: str) -> Tuple[str, float]:
        """
        Match URL to best scraping pattern
        
        Args:
            url: Target URL to match
            
        Returns:
            Tuple of (pattern_name, confidence_score)
        """
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            path = parsed_url.path.lower()
            
            # Check Amazon
            if any(d in domain for d in self.domain_patterns['amazon']):
                # Verify it's a product page
                if '/dp/' in path or '/gp/product/' in path:
                    logger.info(f"Matched {url} to Amazon pattern (high confidence)")
                    return ('amazon_products', 0.95)
            
            # Check Shopify
            if any(d in domain for d in self.domain_patterns['shopify']):
                logger.info(f"Matched {url} to Shopify pattern (high confidence)")
                return ('shopify_store', 0.90)
            
            # Check domain contains skincare/beauty keywords
            if any(keyword in domain for keyword in self.domain_patterns['ecommerce_skincare']):
                logger.info(f"Matched {url} to skincare e-commerce pattern (medium confidence)")
                return ('ecommerce_skincare', 0.75)
            
            # Check path for product indicators
            product_indicators = ['/product/', '/products/', '/item/', '/p/', '-p-', '_p_']
            if any(indicator in path for indicator in product_indicators):
                logger.info(f"Matched {url} to generic e-commerce pattern (low confidence)")
                return ('ecommerce_skincare', 0.60)
            
            # Default fallback
            logger.info(f"Using generic pattern for {url}")
            return ('generic_ecommerce', 0.40)
            
        except Exception as e:
            logger.error(f"Error matching URL {url}: {e}")
            return ('generic_ecommerce', 0.30)
    
    def is_product_page(self, url: str) -> bool:
        """
        Check if URL appears to be a product page
        
        Args:
            url: URL to check
            
        Returns:
            True if likely a product page
        """
        try:
            parsed = urlparse(url)
            path = parsed.path.lower()
            
            # Common product page patterns
            product_patterns = [
                r'/product[s]?/',
                r'/item[s]?/',
                r'/p/',
                r'/dp/',
                r'-p-\d+',
                r'_p_\d+',
                r'/buy/',
                r'/shop/'
            ]
            
            return any(re.search(pattern, path) for pattern in product_patterns)
            
        except Exception as e:
            logger.error(f"Error checking if product page: {e}")
            return False
    
    def extract_category_from_url(self, url: str) -> Optional[str]:
        """
        Try to extract category from URL structure
        
        Args:
            url: Product URL
            
        Returns:
            Category string or None
        """
        try:
            parsed = urlparse(url)
            path_parts = [p for p in parsed.path.split('/') if p]
            
            # Common category keywords
            category_keywords = {
                'skincare': 'Skin Care',
                'skin-care': 'Skin Care',
                'vitamins': 'Vitamins & Supplements',
                'supplements': 'Vitamins & Supplements',
                'beauty': 'Skin Care',
                'cosmetics': 'Skin Care',
                'serum': 'Skin Care',
                'moisturizer': 'Skin Care',
                'cream': 'Skin Care'
            }
            
            for part in path_parts:
                part_lower = part.lower()
                for keyword, category in category_keywords.items():
                    if keyword in part_lower:
                        return category
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting category: {e}")
            return None
    
    def get_pattern_info(self, pattern_name: str) -> dict:
        """
        Get information about a specific pattern
        
        Args:
            pattern_name: Name of the pattern
            
        Returns:
            Dictionary with pattern metadata
        """
        pattern_info = {
            'amazon_products': {
                'name': 'Amazon Products',
                'description': 'Optimized for Amazon product pages',
                'requires_js': True,
                'reliability': 'high'
            },
            'shopify_store': {
                'name': 'Shopify Store',
                'description': 'Works with Shopify-based stores',
                'requires_js': False,
                'reliability': 'high'
            },
            'ecommerce_skincare': {
                'name': 'E-commerce Skincare',
                'description': 'General pattern for skincare e-commerce sites',
                'requires_js': False,
                'reliability': 'medium'
            },
            'generic_ecommerce': {
                'name': 'Generic E-commerce',
                'description': 'Fallback pattern for any e-commerce site',
                'requires_js': False,
                'reliability': 'low'
            }
        }
        
        return pattern_info.get(pattern_name, {
            'name': 'Unknown',
            'description': 'Pattern not found',
            'requires_js': False,
            'reliability': 'unknown'
        })


if __name__ == '__main__':
    # Test the matcher
    matcher = URLMatcher()
    
    test_urls = [
        'https://www.amazon.com/dp/B08XYZ123',
        'https://mystore.myshopify.com/products/moisturizer',
        'https://www.skincare.com/products/vitamin-c-serum',
        'https://example.com/item/12345'
    ]
    
    for url in test_urls:
        pattern, confidence = matcher.match(url)
        print(f"\nURL: {url}")
        print(f"Pattern: {pattern} (confidence: {confidence:.2f})")
        print(f"Is product page: {matcher.is_product_page(url)}")

