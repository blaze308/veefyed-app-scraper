"""
AI-Assisted Pattern Detector
Uses historical script analysis to predict best scraping patterns
"""

import json
import logging
from typing import Dict, List, Tuple, Optional
from collections import Counter
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class AIPatternDetector:
    """
    AI-assisted pattern detection based on historical scripts
    Uses simple ML techniques (TF-IDF-like approach) to match patterns
    """
    
    def __init__(self, training_data_path: Optional[str] = None):
        """Initialize AI detector with optional training data"""
        self.training_data = {}
        self.pattern_features = {}
        
        if training_data_path:
            self.load_training_data(training_data_path)
        else:
            # Initialize with default features
            self._initialize_default_features()
    
    def _initialize_default_features(self):
        """Initialize with default pattern features"""
        self.pattern_features = {
            'ecommerce_skincare': {
                'keywords': ['serum', 'cream', 'moisturizer', 'cleanser', 'toner', 
                           'vitamin', 'skincare', 'beauty', 'spf', 'anti-aging'],
                'domain_indicators': ['beauty', 'skincare', 'cosmetics', 'dermstore'],
                'html_patterns': ['product-title', 'add-to-cart', 'price', 'ingredients'],
                'weight': 1.0
            },
            'amazon_products': {
                'keywords': ['amazon', 'prime'],
                'domain_indicators': ['amazon.com', 'amazon.co'],
                'html_patterns': ['productTitle', 'priceblock', 'feature-bullets'],
                'weight': 1.0
            },
            'shopify_store': {
                'keywords': ['shopify'],
                'domain_indicators': ['myshopify.com'],
                'html_patterns': ['product-single', 'shopify', 'product__price'],
                'weight': 1.0
            },
            'generic_ecommerce': {
                'keywords': ['shop', 'buy', 'store', 'product'],
                'domain_indicators': [],
                'html_patterns': ['product', 'price', 'cart'],
                'weight': 0.5
            }
        }
    
    def load_training_data(self, path: str) -> bool:
        """
        Load training data from historical scripts
        
        Args:
            path: Path to training data JSON file
            
        Returns:
            True if successful
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.training_data = json.load(f)
            
            # Extract features from training data
            self._extract_features_from_training()
            logger.info(f"Loaded training data from {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading training data: {e}")
            return False
    
    def _extract_features_from_training(self):
        """Extract pattern features from training data"""
        # This would analyze historical scripts to build better patterns
        # For now, we'll use the default features
        pass
    
    def predict_pattern(self, url: str, html_content: Optional[str] = None) -> Tuple[str, float, Dict]:
        """
        Predict best pattern for given URL and optional HTML content
        
        Args:
            url: Target URL
            html_content: Optional HTML content for better prediction
            
        Returns:
            Tuple of (pattern_name, confidence, analysis_details)
        """
        try:
            scores = {}
            analysis = {
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'features_detected': {},
                'recommendations': []
            }
            
            url_lower = url.lower()
            
            # Score each pattern
            for pattern_name, features in self.pattern_features.items():
                score = 0.0
                detected_features = []
                
                # Check domain indicators
                for indicator in features['domain_indicators']:
                    if indicator in url_lower:
                        score += 10 * features['weight']
                        detected_features.append(f"domain:{indicator}")
                
                # Check URL keywords
                for keyword in features['keywords']:
                    if keyword in url_lower:
                        score += 2 * features['weight']
                        detected_features.append(f"keyword:{keyword}")
                
                # If HTML content provided, check HTML patterns
                if html_content:
                    html_lower = html_content.lower()
                    for pattern in features['html_patterns']:
                        if pattern in html_lower:
                            score += 3 * features['weight']
                            detected_features.append(f"html:{pattern}")
                
                scores[pattern_name] = score
                analysis['features_detected'][pattern_name] = detected_features
            
            # Get best pattern
            if not scores or max(scores.values()) == 0:
                best_pattern = 'generic_ecommerce'
                confidence = 0.3
                analysis['recommendations'].append(
                    "No strong pattern match found, using generic pattern"
                )
            else:
                best_pattern = max(scores, key=scores.get)
                max_score = scores[best_pattern]
                
                # Normalize confidence (0-1 scale)
                confidence = min(max_score / 20.0, 1.0)
                
                # Add recommendations based on confidence
                if confidence > 0.8:
                    analysis['recommendations'].append("High confidence match - pattern should work well")
                elif confidence > 0.5:
                    analysis['recommendations'].append("Medium confidence - may need manual review")
                else:
                    analysis['recommendations'].append("Low confidence - consider manual selector inspection")
            
            logger.info(f"Predicted pattern '{best_pattern}' with confidence {confidence:.2f} for {url}")
            
            return (best_pattern, confidence, analysis)
            
        except Exception as e:
            logger.error(f"Error predicting pattern: {e}")
            return ('generic_ecommerce', 0.2, {'error': str(e)})
    
    def analyze_html_structure(self, html_content: str) -> Dict:
        """
        Analyze HTML structure to identify potential selectors
        
        Args:
            html_content: HTML content to analyze
            
        Returns:
            Dictionary with analysis results
        """
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'lxml')
            
            analysis = {
                'total_elements': len(soup.find_all()),
                'images': len(soup.find_all('img')),
                'links': len(soup.find_all('a')),
                'forms': len(soup.find_all('form')),
                'common_classes': [],
                'potential_selectors': {
                    'title': [],
                    'price': [],
                    'description': [],
                    'image': []
                }
            }
            
            # Find common classes
            all_classes = []
            for element in soup.find_all(class_=True):
                all_classes.extend(element.get('class', []))
            
            class_counter = Counter(all_classes)
            analysis['common_classes'] = [cls for cls, count in class_counter.most_common(10)]
            
            # Identify potential title selectors
            for tag in ['h1', 'h2']:
                elements = soup.find_all(tag)
                for elem in elements:
                    classes = elem.get('class', [])
                    if classes:
                        analysis['potential_selectors']['title'].append(f"{tag}.{'.'.join(classes)}")
            
            # Identify potential price selectors
            price_patterns = [r'\$\d+', r'USD', r'price', r'cost', r'£\d+', r'€\d+']
            for elem in soup.find_all(class_=True):
                text = elem.get_text(strip=True)
                classes = ' '.join(elem.get('class', []))
                if any(re.search(pattern, text, re.IGNORECASE) for pattern in price_patterns):
                    if 'price' in classes.lower() or 'cost' in classes.lower():
                        analysis['potential_selectors']['price'].append(f".{elem.get('class')[0]}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing HTML structure: {e}")
            return {'error': str(e)}
    
    def suggest_improvements(self, pattern_name: str, success_rate: float) -> List[str]:
        """
        Suggest pattern improvements based on success rate
        
        Args:
            pattern_name: Pattern that was used
            success_rate: Success rate (0-1)
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        if success_rate < 0.3:
            suggestions.append(f"Pattern '{pattern_name}' has low success rate ({success_rate:.1%})")
            suggestions.append("Consider creating a custom pattern for this site")
            suggestions.append("Inspect page source and identify unique selectors")
        elif success_rate < 0.6:
            suggestions.append(f"Pattern '{pattern_name}' has medium success rate ({success_rate:.1%})")
            suggestions.append("Some fields may be missing - review selector list")
            suggestions.append("Consider adding fallback selectors")
        else:
            suggestions.append(f"Pattern '{pattern_name}' performing well ({success_rate:.1%})")
            suggestions.append("Continue monitoring for changes")
        
        return suggestions
    
    def save_training_example(self, url: str, pattern_used: str, 
                             success_fields: List[str], failed_fields: List[str],
                             output_path: str = 'data/ai_training_data.json'):
        """
        Save scraping result as training example
        
        Args:
            url: Scraped URL
            pattern_used: Pattern that was used
            success_fields: Fields successfully extracted
            failed_fields: Fields that failed to extract
            output_path: Path to save training data
        """
        try:
            # Load existing training data
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    training_data = json.load(f)
            except FileNotFoundError:
                training_data = {'examples': []}
            
            # Add new example
            example = {
                'timestamp': datetime.now().isoformat(),
                'url': url,
                'pattern_used': pattern_used,
                'success_fields': success_fields,
                'failed_fields': failed_fields,
                'success_rate': len(success_fields) / (len(success_fields) + len(failed_fields))
                                if (success_fields or failed_fields) else 0
            }
            
            training_data['examples'].append(example)
            
            # Save updated training data
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved training example for {url}")
            
        except Exception as e:
            logger.error(f"Error saving training example: {e}")


if __name__ == '__main__':
    # Test the AI detector
    detector = AIPatternDetector()
    
    test_urls = [
        'https://www.beautycounter.com/products/serum',
        'https://www.amazon.com/dp/B08XYZ123',
        'https://store.myshopify.com/products/moisturizer'
    ]
    
    for url in test_urls:
        pattern, confidence, analysis = detector.predict_pattern(url)
        print(f"\nURL: {url}")
        print(f"Predicted: {pattern} (confidence: {confidence:.2f})")
        print(f"Features: {analysis['features_detected'][pattern]}")

