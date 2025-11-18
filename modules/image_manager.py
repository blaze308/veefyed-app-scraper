"""
Image Manager - Download, organize, and export scraped images
Optimized with progress tracking, concurrent downloads, and file size info
"""

import os
import requests
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Callable
from urllib.parse import urlparse, urljoin
import logging
import zipfile
from datetime import datetime
import concurrent.futures
import threading
import time

logger = logging.getLogger(__name__)


class ImageManager:
    """
    Manages image downloads and organization by website
    Optimized with progress tracking and concurrent downloads
    """
    
    def __init__(self, base_dir: str = None, max_workers: int = 5):
        """
        Initialize image manager
        
        Args:
            base_dir: Base directory for storing images (defaults to user's Downloads folder)
            max_workers: Maximum concurrent download threads
        """
        if base_dir is None:
            # Use user's Downloads folder
            base_dir = self._get_downloads_folder()
        
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers
        self.progress_callback = None
        self.download_stats = {
            'total': 0,
            'completed': 0,
            'failed': 0,
            'total_size': 0,
            'downloaded_size': 0
        }
    
    def _get_downloads_folder(self) -> str:
        """Get the user's Downloads folder path"""
        import platform
        
        system = platform.system()
        
        if system == "Windows":
            # Windows Downloads folder
            import os
            downloads = os.path.join(os.path.expanduser("~"), "Downloads", "ScrapedImages")
        elif system == "Darwin":  # macOS
            downloads = os.path.join(os.path.expanduser("~"), "Downloads", "ScrapedImages")
        else:  # Linux and others
            downloads = os.path.join(os.path.expanduser("~"), "Downloads", "ScrapedImages")
        
        return downloads
        
    def get_website_name(self, url: str) -> str:
        """Extract clean website name from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            # Clean domain name (remove .com, .co.uk, etc.)
            name = domain.split('.')[0]
            return name
        except:
            return 'unknown_website'
    
    def create_website_folder(self, url: str) -> tuple[Path, str]:
        """
        Create folder structure for website
        
        Returns:
            (folder_path, website_name)
        """
        website_name = self.get_website_name(url)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        folder_name = f"{website_name}_{timestamp}"
        
        folder_path = self.base_dir / folder_name
        images_folder = folder_path / 'images'
        
        folder_path.mkdir(parents=True, exist_ok=True)
        images_folder.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Created folder structure: {folder_path}")
        logger.info(f"Images will be saved to: {images_folder}")
        return folder_path, website_name
    
    def set_progress_callback(self, callback: Callable):
        """Set callback function for progress updates"""
        self.progress_callback = callback
    
    def _update_progress(self, message: str, increment_completed: bool = False, file_size: int = 0):
        """Update progress and call callback if set"""
        if increment_completed:
            self.download_stats['completed'] += 1
            self.download_stats['downloaded_size'] += file_size
        
        logger.debug(f"Progress update: {message} (completed: {self.download_stats['completed']}/{self.download_stats['total']})")
        
        if self.progress_callback:
            try:
                progress_data = {
                    'message': message,
                    'completed': self.download_stats['completed'],
                    'total': self.download_stats['total'],
                    'failed': self.download_stats['failed'],
                    'downloaded_size': self.download_stats['downloaded_size'],
                    'total_size': self.download_stats['total_size'],
                    'percentage': (self.download_stats['completed'] / max(self.download_stats['total'], 1)) * 100
                }
                self.progress_callback(progress_data)
                logger.debug(f"Progress callback executed successfully")
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
    
    def get_image_info(self, image_url: str) -> Dict:
        """Get image info (size, type) without downloading"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Range": "bytes=0-1023"  # Just get first 1KB to check headers
            }
            
            response = requests.head(image_url, headers=headers, timeout=10)
            
            info = {
                'url': image_url,
                'size': int(response.headers.get('content-length', 0)),
                'type': response.headers.get('content-type', 'unknown'),
                'valid': response.status_code == 200
            }
            
            return info
            
        except Exception as e:
            logger.debug(f"Failed to get info for {image_url}: {e}")
            return {
                'url': image_url,
                'size': 0,
                'type': 'unknown',
                'valid': False
            }
    
    def download_image(self, image_url: str, save_path: Path, product_name: str = '', index: int = 0) -> Optional[Dict]:
        """
        Download a single image with progress tracking
        
        Args:
            image_url: URL of image to download
            save_path: Directory to save image
            product_name: Name of product (for filename)
            index: Image index if multiple images
            
        Returns:
            Dict with download info or None if failed
        """
        try:
            if not image_url or not image_url.startswith('http'):
                logger.warning(f"Invalid image URL: {image_url}")
                self.download_stats['failed'] += 1
                return None
            
            # Generate filename
            url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
            ext = self._get_extension(image_url)
            
            # Sanitize product name
            safe_name = self._sanitize_filename(product_name)
            if safe_name:
                filename = f"{safe_name}_{index}_{url_hash}{ext}"
            else:
                filename = f"image_{index}_{url_hash}{ext}"
            
            file_path = save_path / filename
            
            # Update progress
            self._update_progress(f"Downloading {filename}...")
            
            # Download image
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            }
            
            response = requests.get(image_url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get file size
            file_size = int(response.headers.get('content-length', 0))
            
            # Save image with progress tracking
            downloaded_size = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded_size += len(chunk)
            
            # Get actual file size
            actual_size = file_path.stat().st_size
            
            # Update progress
            self._update_progress(f"Downloaded {filename} ({self._format_size(actual_size)})", 
                                increment_completed=True, file_size=actual_size)
            
            logger.info(f"Downloaded: {filename} ({self._format_size(actual_size)})")
            
            return {
                'path': str(file_path),
                'filename': filename,
                'size': actual_size,
                'url': image_url
            }
            
        except Exception as e:
            logger.error(f"Failed to download {image_url}: {e}")
            self.download_stats['failed'] += 1
            self._update_progress(f"Failed to download {image_url}")
            return None
    
    def download_product_images_concurrent(self, product_data: Dict, images_folder: Path) -> List[Dict]:
        """
        Download all images for a product using concurrent downloads
        
        Args:
            product_data: Product data dict with image URLs
            images_folder: Folder to save images
            
        Returns:
            List of download info dicts
        """
        product_name = product_data.get('product_name', 'unknown')
        
        # Collect all image URLs
        image_urls = []
        
        # Add main image
        main_image = product_data.get('product_image_url')
        if main_image:
            image_urls.append((main_image, 0))
        
        # Add gallery images
        gallery_images = product_data.get('product_images', [])
        if isinstance(gallery_images, list):
            for idx, img_url in enumerate(gallery_images, start=1):
                if img_url and img_url != main_image:  # Skip if same as main
                    image_urls.append((img_url, idx))
        
        if not image_urls:
            return []
        
        # Update total count
        self.download_stats['total'] += len(image_urls)
        
        # Download concurrently
        downloaded_images = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all download tasks
            future_to_url = {
                executor.submit(self.download_image, url, images_folder, product_name, idx): (url, idx)
                for url, idx in image_urls
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_url):
                url, idx = future_to_url[future]
                try:
                    result = future.result()
                    if result:
                        downloaded_images.append(result)
                except Exception as e:
                    logger.error(f"Error downloading {url}: {e}")
                    self.download_stats['failed'] += 1
        
        return downloaded_images
    
    def download_product_images(self, product_data: Dict, images_folder: Path) -> List[str]:
        """
        Download all images for a product (backward compatibility)
        
        Args:
            product_data: Product data dict with image URLs
            images_folder: Folder to save images
            
        Returns:
            List of downloaded image paths
        """
        results = self.download_product_images_concurrent(product_data, images_folder)
        return [result['path'] for result in results if result]
    
    def download_batch_images(self, products: List[Dict], images_folder: Path) -> Dict[str, List[str]]:
        """
        Download images for multiple products with progress tracking
        
        Args:
            products: List of product data dicts
            images_folder: Folder to save images
            
        Returns:
            Dict mapping product_id to list of downloaded image paths
        """
        # Reset stats
        self.download_stats = {
            'total': 0,
            'completed': 0,
            'failed': 0,
            'total_size': 0,
            'downloaded_size': 0
        }
        
        # Calculate total images first
        total_images = 0
        for product in products:
            main_image = product.get('product_image_url')
            gallery_images = product.get('product_images', [])
            
            if main_image:
                total_images += 1
            if isinstance(gallery_images, list):
                # Count unique gallery images
                unique_gallery = [img for img in gallery_images if img and img != main_image]
                total_images += len(unique_gallery)
        
        self.download_stats['total'] = total_images
        self._update_progress(f"Starting download of {total_images} images from {len(products)} products...")
        
        all_downloads = {}
        
        for i, product in enumerate(products, 1):
            product_id = product.get('product_id', 'unknown')
            product_name = product.get('product_name', 'unknown')
            
            self._update_progress(f"Processing product {i}/{len(products)}: {product_name[:30]}...")
            
            downloaded = self.download_product_images_concurrent(product, images_folder)
            all_downloads[product_id] = [result['path'] for result in downloaded if result]
            
            logger.info(f"Downloaded {len(downloaded)} images for {product_name}")
        
        # Final progress update
        total_downloaded = sum(len(paths) for paths in all_downloads.values())
        total_size = self._format_size(self.download_stats['downloaded_size'])
        
        self._update_progress(f"Completed! Downloaded {total_downloaded} images ({total_size})")
        
        return all_downloads
    
    def create_zip_with_progress(self, folder_path: Path, zip_name: str = None) -> Optional[Dict]:
        """
        Create ZIP file of images folder with progress tracking
        
        Args:
            folder_path: Path to folder containing images
            zip_name: Optional custom zip name
            
        Returns:
            Dict with ZIP info or None if failed
        """
        try:
            images_folder = folder_path / 'images'
            if not images_folder.exists():
                logger.error(f"Images folder not found: {images_folder}")
                return None
            
            # Count images and calculate total size
            image_files = [f for f in images_folder.glob('*') if f.is_file()]
            if not image_files:
                logger.warning(f"No images to zip in {images_folder}")
                return None
            
            total_size = sum(f.stat().st_size for f in image_files)
            
            self._update_progress(f"Creating ZIP archive with {len(image_files)} images ({self._format_size(total_size)})...")
            
            # Create ZIP
            if not zip_name:
                zip_name = f"{folder_path.name}_images.zip"
            
            zip_path = folder_path / zip_name
            
            processed_size = 0
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
                for i, image_file in enumerate(image_files, 1):
                    if image_file.is_file():
                        # Update progress
                        file_size = image_file.stat().st_size
                        progress = (i / len(image_files)) * 100
                        self._update_progress(f"Adding {image_file.name} to ZIP... ({i}/{len(image_files)}, {progress:.1f}%)")
                        
                        # Add with relative path (just filename)
                        zipf.write(image_file, arcname=image_file.name)
                        processed_size += file_size
            
            # Get final ZIP size
            zip_size = zip_path.stat().st_size
            compression_ratio = (1 - zip_size / total_size) * 100 if total_size > 0 else 0
            
            result = {
                'path': str(zip_path),
                'filename': zip_name,
                'size': zip_size,
                'original_size': total_size,
                'compression_ratio': compression_ratio,
                'file_count': len(image_files)
            }
            
            self._update_progress(f"ZIP created! {len(image_files)} images, {self._format_size(zip_size)} "
                                f"(compressed from {self._format_size(total_size)}, {compression_ratio:.1f}% savings)")
            
            logger.info(f"Created ZIP: {zip_name} with {len(image_files)} images "
                       f"({self._format_size(zip_size)}, {compression_ratio:.1f}% compression)")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create ZIP: {e}")
            self._update_progress(f"Failed to create ZIP: {e}")
            return None
    
    def create_zip(self, folder_path: Path, zip_name: str = None) -> Optional[str]:
        """
        Create ZIP file of images folder (backward compatibility)
        
        Args:
            folder_path: Path to folder containing images
            zip_name: Optional custom zip name
            
        Returns:
            Path to created ZIP file
        """
        result = self.create_zip_with_progress(folder_path, zip_name)
        return result['path'] if result else None
    
    def _get_extension(self, url: str) -> str:
        """Get file extension from URL"""
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # Common image extensions
        for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
            if ext in path:
                return ext
        
        # Default to .jpg
        return '.jpg'
    
    def _sanitize_filename(self, name: str, max_length: int = 50) -> str:
        """Sanitize string for use in filename"""
        if not name:
            return ''
        
        # Remove invalid characters
        valid_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        filename = ''.join(c for c in name if c in valid_chars)
        
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        
        # Trim to max length
        if len(filename) > max_length:
            filename = filename[:max_length]
        
        return filename.strip('_-.')
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        if i == 0:
            return f"{int(size_bytes)} {size_names[i]}"
        else:
            return f"{size_bytes:.1f} {size_names[i]}"


if __name__ == '__main__':
    # Test the image manager
    manager = ImageManager()
    
    # Test URL
    test_url = "https://bleakmakeup.com/products/test"
    folder, name = manager.create_website_folder(test_url)
    print(f"Created folder: {folder}")
    print(f"Website name: {name}")

