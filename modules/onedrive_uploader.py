"""
OneDrive Uploader - Upload images and get shareable links
Uses Microsoft Graph API
"""

import os
import requests
from pathlib import Path
from urllib.parse import urlparse
import hashlib
import logging
from typing import Optional, List
import tempfile

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use system env vars

logger = logging.getLogger(__name__)


class OneDriveUploader:
    """
    Upload images to OneDrive and generate shareable links
    Uses Microsoft Graph API
    """
    
    def __init__(self, tenant_id: str = None, client_id: str = None, 
                 client_secret: str = None, user_id: str = None, 
                 parent_folder_id: str = None):
        """
        Initialize OneDrive uploader with credentials
        
        Args:
            tenant_id: Azure AD tenant ID
            client_id: Azure app client ID
            client_secret: Azure app client secret
            user_id: OneDrive user ID
            parent_folder_id: Parent folder ID for uploads
        """
        # Use provided credentials or from environment variables
        # SECURITY: Never hardcode secrets! Use environment variables or .env file
        self.tenant_id = tenant_id or os.getenv('ONEDRIVE_TENANT_ID')
        self.client_id = client_id or os.getenv('ONEDRIVE_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('ONEDRIVE_CLIENT_SECRET')
        self.user_id = user_id or os.getenv('ONEDRIVE_USER_ID')
        self.parent_folder_id = parent_folder_id or os.getenv('ONEDRIVE_PARENT_FOLDER')
        
        # Validate required credentials
        if not all([self.tenant_id, self.client_id, self.client_secret, self.user_id, self.parent_folder_id]):
            logger.warning("OneDrive credentials not found in environment variables")
            logger.warning("Set ONEDRIVE_TENANT_ID, ONEDRIVE_CLIENT_ID, ONEDRIVE_CLIENT_SECRET, ONEDRIVE_USER_ID, ONEDRIVE_PARENT_FOLDER")
            logger.warning("Or create a .env file with these values")
        
        self.access_token = None
        self.headers = {}
        self.upload_root = Path(tempfile.gettempdir()) / "scraper_uploads"
        self.upload_root.mkdir(exist_ok=True)
        
        # Authenticate on initialization
        self._authenticate()
    
    def _authenticate(self) -> bool:
        """Get access token from Microsoft"""
        try:
            token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            token_data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "https://graph.microsoft.com/.default"
            }
            
            response = requests.post(token_url, data=token_data, timeout=10)
            
            if response.status_code == 401:
                error_detail = response.text
                logger.error(f"OneDrive authentication failed: 401 Unauthorized")
                logger.error(f"Error details: {error_detail}")
                logger.error("Possible causes:")
                logger.error("  1. Client secret has expired (check Azure portal)")
                logger.error("  2. Client ID or Tenant ID is incorrect")
                logger.error("  3. Azure app doesn't have required permissions")
                logger.error("  4. Client secret value is wrong")
                return False
            
            response.raise_for_status()
            
            self.access_token = response.json().get("access_token")
            if not self.access_token:
                logger.error("OneDrive authentication failed: No access token received")
                return False
                
            self.headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            logger.info("OneDrive authentication successful")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OneDrive authentication failed: Network error - {e}")
            return False
        except Exception as e:
            logger.error(f"OneDrive authentication failed: {e}")
            return False
    
    def process_and_upload_image(self, image_url: str, category_name: str = "products") -> Optional[str]:
        """
        Download image from URL, upload to OneDrive, and return shareable link
        
        Args:
            image_url: URL of image to download
            category_name: Category/folder name for organization
            
        Returns:
            Shareable OneDrive link or None if failed
        """
        try:
            # Download image
            local_path = self._download_image(image_url, category_name)
            if not local_path:
                return None
            
            # Upload to OneDrive
            file_id = self._upload_to_onedrive(local_path, category_name)
            if not file_id:
                return None
            
            # Get shareable link
            share_link = self._get_shareable_link(file_id)
            
            # Cleanup local file
            try:
                os.remove(local_path)
            except:
                pass
            
            return share_link
            
        except Exception as e:
            logger.error(f"Error processing image {image_url}: {e}")
            return None
    
    def process_multiple_images(self, image_urls: List[str], category_name: str = "products") -> List[str]:
        """
        Process multiple images and return list of shareable links
        
        Args:
            image_urls: List of image URLs
            category_name: Category for organization
            
        Returns:
            List of shareable links (empty strings for failed uploads)
        """
        share_links = []
        
        for img_url in image_urls:
            link = self.process_and_upload_image(img_url, category_name)
            if link:
                share_links.append(link)
                logger.info(f"✅ Uploaded: {img_url[:50]}...")
            else:
                logger.warning(f"⚠️ Failed: {img_url[:50]}...")
                share_links.append("")  # Keep position in array
        
        return share_links
    
    def _download_image(self, image_url: str, category_name: str) -> Optional[Path]:
        """Download image from URL to local temp folder"""
        try:
            # Create category folder
            folder_path = self.upload_root / self._sanitize_filename(category_name)
            folder_path.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename
            file_name = self._generate_filename(image_url)
            local_path = folder_path / file_name
            
            # Skip if already exists
            if local_path.exists():
                logger.debug(f"Image already exists locally: {local_path}")
                return local_path
            
            # Download image
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            }
            
            response = requests.get(image_url, headers=headers, stream=True, timeout=15)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.debug(f"Downloaded: {local_path}")
            return local_path
            
        except Exception as e:
            logger.error(f"Error downloading image {image_url}: {e}")
            return None
    
    def _upload_to_onedrive(self, local_path: Path, category_name: str) -> Optional[str]:
        """Upload file to OneDrive and return file ID"""
        try:
            file_name = local_path.name
            
            # Upload to parent folder (not creating subfolders for simplicity)
            url = f"https://graph.microsoft.com/v1.0/users/{self.user_id}/drive/items/{self.parent_folder_id}:/{file_name}:/content"
            
            with open(local_path, 'rb') as f:
                upload_headers = {"Authorization": self.headers["Authorization"]}
                response = requests.put(url, headers=upload_headers, data=f, timeout=30)
                response.raise_for_status()
            
            file_id = response.json().get("id")
            logger.debug(f"Uploaded to OneDrive: {file_name} (ID: {file_id})")
            return file_id
            
        except Exception as e:
            logger.error(f"Error uploading to OneDrive: {e}")
            return None
    
    def _get_shareable_link(self, file_id: str) -> Optional[str]:
        """Generate shareable link for uploaded file"""
        try:
            url = f"https://graph.microsoft.com/v1.0/users/{self.user_id}/drive/items/{file_id}/createLink"
            payload = {
                "type": "view",
                "scope": "anonymous"
            }
            
            response = requests.post(url, headers=self.headers, json=payload, timeout=10)
            response.raise_for_status()
            
            link = response.json()["link"]["webUrl"]
            logger.debug(f"Shareable link created: {link}")
            return link
            
        except Exception as e:
            logger.error(f"Error creating shareable link: {e}")
            return None
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize filename for filesystem"""
        return name.replace("/", "-").replace("\\", "-").replace(" ", "_").strip()
    
    def _generate_filename(self, url: str) -> str:
        """Generate unique filename from URL"""
        parsed = urlparse(url)
        original_name = os.path.basename(parsed.path)
        
        # Add hash for uniqueness
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        
        # Keep original extension
        name, ext = os.path.splitext(original_name)
        if not ext:
            ext = '.jpg'  # Default extension
        
        return f"{url_hash}_{name[:30]}{ext}"
    
    def is_enabled(self) -> bool:
        """Check if OneDrive integration is properly configured"""
        return bool(self.access_token)


# Create a global instance (lazy initialization)
_uploader_instance = None


def get_uploader() -> Optional[OneDriveUploader]:
    """Get or create OneDrive uploader instance"""
    global _uploader_instance
    
    if _uploader_instance is None:
        try:
            _uploader_instance = OneDriveUploader()
            if not _uploader_instance.is_enabled():
                logger.warning("OneDrive uploader not properly configured")
                return None
        except Exception as e:
            logger.error(f"Failed to initialize OneDrive uploader: {e}")
            return None
    
    return _uploader_instance


if __name__ == '__main__':
    # Test the uploader
    import sys
    
    try:
        uploader = OneDriveUploader()
        
        if uploader.is_enabled():
            print("OneDrive authentication successful!")
            
            # Test with a sample image
            test_url = "https://via.placeholder.com/600x400"
            link = uploader.process_and_upload_image(test_url, "test_category")
            
            if link:
                print(f"Image uploaded successfully!")
                print(f"Share link: {link}")
            else:
                print("Image upload failed")
        else:
            print("OneDrive not configured")
            print("\nTo fix:")
            print("1. Check Azure portal - client secret may have expired")
            print("2. Verify credentials in modules/onedrive_uploader.py")
            print("3. Ensure Azure app has Files.ReadWrite.All permission")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

