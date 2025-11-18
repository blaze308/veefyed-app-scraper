"""
Auto-Scraper FastAPI Application
Main backend server for the web scraping tool
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime
import json
import os
import logging

# Import our modules
from modules.scraper_engine import ScraperEngine
from modules.url_matcher import URLMatcher
from modules.ai_pattern_detector import AIPatternDetector
from modules.image_manager import ImageManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Auto-Scraper AI Tool",
    description="Intelligent web scraper for product data extraction",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize components
scraper = ScraperEngine()
url_matcher = URLMatcher()
ai_detector = AIPatternDetector()
image_manager = ImageManager()

# Job storage (in production, use Redis or database)
jobs: Dict[str, Dict[str, Any]] = {}


# Pydantic models
class ScrapeRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "url": "https://example.com/collections/skincare",
                "pattern": "ecommerce_skincare",
                "use_ai": True,
                "scrape_all_products": True,
                "max_products": 50,
                "upload_images": True
            }
        }
    )
    
    url: HttpUrl
    pattern: Optional[str] = None
    use_ai: bool = True
    scrape_all_products: bool = False  # Scrape all products on page
    max_products: int = 50  # Limit for batch scraping
    upload_images: bool = True  # NEW: Upload images to OneDrive


class ScrapeResponse(BaseModel):
    status: str
    job_id: str
    message: str
    pattern_used: Optional[str] = None
    confidence: Optional[float] = None
    detected_platform: Optional[str] = None
    scraper_type: Optional[str] = None


class JobStatus(BaseModel):
    job_id: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    url: str
    pattern_used: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None
    detected_platform: Optional[str] = None
    scraper_type: Optional[str] = None
    is_batch: bool = False  # NEW: Is this a batch scrape?
    products_found: int = 0  # NEW: Number of products found
    products_scraped: int = 0  # NEW: Number successfully scraped
    failed_products: List[Dict] = []  # NEW: Failed products with reasons


@app.get("/")
async def home(request: Request):
    """Render main UI page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.post("/api/scrape", response_model=ScrapeResponse)
async def scrape_url(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Main scraping endpoint - SMART EDITION
    
    Process:
    1. Auto-detect platform (Shopify, WooCommerce, etc.)
    2. Route to specialized scraper
    3. Upload images to OneDrive
    4. Return formatted data matching Product model
    """
    try:
        url_str = str(request.url)
        job_id = str(uuid.uuid4())
        
        logger.info(f"🔍 New smart scrape request: {url_str} (Job: {job_id})")
        
        # Create job entry
        jobs[job_id] = {
            'job_id': job_id,
            'status': 'processing',
            'created_at': datetime.now().isoformat(),
            'completed_at': None,
            'url': url_str,
            'pattern_used': None,
            'confidence': None,
            'detected_platform': None,
            'scraper_type': None,
            'result': None,
            'error': None,
            'is_batch': request.scrape_all_products,
            'products_found': 0,
            'products_scraped': 0,
            'failed_products': []
        }
        
        # Run scraping in background (smart scraper will auto-detect)
        background_tasks.add_task(
            run_scraping_job, 
            job_id, 
            url_str, 
            None,
            request.scrape_all_products,
            request.max_products,
            request.upload_images
        )
        
        return ScrapeResponse(
            status="processing",
            job_id=job_id,
            message="🔍 Detecting platform and starting scrape...",
            pattern_used=None,
            confidence=None
        )
        
    except Exception as e:
        logger.error(f"Error creating scrape job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_scraping_job(job_id: str, url: str, pattern_name: str, 
                          scrape_all: bool = False, max_products: int = 50,
                          upload_images: bool = True):
    """
    Background task to run SMART scraping job
    
    Args:
        job_id: Unique job identifier
        url: Target URL to scrape
        pattern_name: Pattern to use (unused - auto-detected now)
        scrape_all: Whether to scrape all products on the page
        max_products: Maximum products to scrape in batch mode
        upload_images: Whether to upload images to OneDrive
    """
    try:
        # Temporarily disable OneDrive if user unchecked it
        original_onedrive_setting = scraper.use_onedrive
        scraper.use_onedrive = upload_images and scraper.onedrive_uploader is not None
        
        if scrape_all:
            logger.info(f"🚀 Starting BATCH scraping job {job_id} (max: {max_products})")
            await run_batch_scraping(job_id, url, max_products)
        else:
            logger.info(f"🚀 Starting single product scraping job {job_id}")
            await run_single_scraping(job_id, url, pattern_name)
        
        # Restore original setting
        scraper.use_onedrive = original_onedrive_setting
            
    except Exception as e:
        logger.error(f"❌ Error in scraping job {job_id}: {e}")
        import traceback
        traceback.print_exc()
        jobs[job_id]['status'] = 'failed'
        jobs[job_id]['completed_at'] = datetime.now().isoformat()
        jobs[job_id]['error'] = str(e)
        scraper.use_onedrive = original_onedrive_setting


async def run_single_scraping(job_id: str, url: str, pattern_name: str):
    """Scrape a single product with detailed error reporting"""
    try:
        # Perform SMART scraping (auto-detects platform)
        result = scraper.scrape(url, pattern_name)
        
        if result:
            # Extract detection info
            detection_info = result.get('detection_info', {})
            
            # Analyze field extraction success
            extraction_report = analyze_extraction(result)
            
            # Save to JSON
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"product_{timestamp}_{job_id[:8]}.json"
            output_path = os.path.join('data', 'outputs', output_filename)
            
            scraper.save_to_json(result, output_path)
            
            # Update job status with detection info
            jobs[job_id]['status'] = 'completed'
            jobs[job_id]['completed_at'] = datetime.now().isoformat()
            jobs[job_id]['result'] = result
            jobs[job_id]['output_file'] = output_filename
            jobs[job_id]['detected_platform'] = detection_info.get('detected_platform', 'unknown')
            jobs[job_id]['scraper_type'] = detection_info.get('scraper_used', 'generic')
            jobs[job_id]['pattern_used'] = detection_info.get('detected_platform', 'auto-detected')
            jobs[job_id]['confidence'] = detection_info.get('confidence', 0.5)
            jobs[job_id]['extraction_report'] = extraction_report  # NEW: Field-by-field report
            
            logger.info(f"✅ Job {job_id} completed | Platform: {jobs[job_id]['detected_platform']}")
        else:
            # Scraping failed
            jobs[job_id]['status'] = 'failed'
            jobs[job_id]['completed_at'] = datetime.now().isoformat()
            jobs[job_id]['error'] = 'Failed to extract data - no result returned'
            
            logger.error(f"❌ Job {job_id} failed")
            
    except Exception as e:
        logger.error(f"❌ Error in single scraping: {e}")
        raise


async def run_batch_scraping(job_id: str, url: str, max_products: int):
    """Scrape multiple products from a collection/category page"""
    try:
        logger.info(f"📦 Batch scraping: {url}")
        
        # Detect platform first
        detection = scraper.detector.detect(url)
        jobs[job_id]['detected_platform'] = detection['platform']
        jobs[job_id]['scraper_type'] = detection['scraper_type']
        
        products = []
        failed_products = []
        
        # Route to appropriate batch scraper
        if detection['platform'] == 'shopify' and detection['confidence'] > 0.5:
            logger.info("→ Using Shopify collection scraper")
            products = scraper.shopify_scraper.scrape_collection(url, max_products)
            
        elif detection['needs_js'] or detection['scraper_type'] == 'selenium':
            logger.info("→ Using Selenium collection scraper")
            if not scraper.selenium_scraper:
                scraper.selenium_scraper = SeleniumScraper(headless=True)
            products = scraper.selenium_scraper.scrape_collection(url, max_products)
            
        else:
            logger.warning("⚠️ Batch scraping not fully supported for this platform yet")
            # Fall back to single product scrape
            single_result = scraper.scrape(url, None)
            if single_result:
                products = [single_result]
        
        jobs[job_id]['products_found'] = len(products)
        
        # Process images for each product
        if scraper.use_onedrive and scraper.onedrive_uploader:
            logger.info(f"☁️ Processing images for {len(products)} products...")
            for i, product in enumerate(products):
                try:
                    products[i] = scraper._process_images(product)
                    jobs[job_id]['products_scraped'] = i + 1
                except Exception as e:
                    logger.error(f"Failed to process images for product {i}: {e}")
                    failed_products.append({
                        'product_name': product.get('product_name', 'Unknown'),
                        'reason': f'Image upload failed: {str(e)}'
                    })
        
        # Save all products to JSON
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"products_batch_{timestamp}_{job_id[:8]}.json"
        output_path = os.path.join('data', 'outputs', output_filename)
        
        scraper.save_to_json({'products': products, 'count': len(products)}, output_path)
        
        # Also save as CSV for easy viewing
        csv_filename = f"products_batch_{timestamp}_{job_id[:8]}.csv"
        csv_path = os.path.join('data', 'outputs', csv_filename)
        scraper.save_to_csv(products, csv_path)
        
        # Update job status
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['completed_at'] = datetime.now().isoformat()
        jobs[job_id]['result'] = {'products': products, 'count': len(products)}
        jobs[job_id]['output_file'] = output_filename
        jobs[job_id]['csv_file'] = csv_filename
        jobs[job_id]['products_scraped'] = len(products)
        jobs[job_id]['failed_products'] = failed_products
        
        logger.info(f"✅ Batch job {job_id} completed | Scraped: {len(products)} products")
        
    except Exception as e:
        logger.error(f"❌ Error in batch scraping: {e}")
        raise


def analyze_extraction(product_data: Dict) -> Dict:
    """
    Analyze which fields were successfully extracted and which failed
    
    Returns:
        {
            'total_fields': 45,
            'extracted': 32,
            'missing': 13,
            'success_rate': 0.71,
            'critical_missing': ['product_name', 'price'],
            'field_details': {...}
        }
    """
    critical_fields = [
        'product_name', 'product_description', 'product_image_url',
        'brand_name', 'category'
    ]
    
    important_fields = [
        'ingredients', 'use_instructions', 'package_size',
        'barcode', 'product_images'
    ]
    
    optional_fields = [
        'skin_type', 'skin_concerns', 'benefits', 'warnings',
        'key_ingredients', 'rating', 'review_count'
    ]
    
    all_fields = critical_fields + important_fields + optional_fields
    
    extracted = []
    missing = []
    field_details = {}
    
    for field in all_fields:
        value = product_data.get(field)
        has_value = bool(value and value != '' and value != [] and value != 0)
        
        if has_value:
            extracted.append(field)
            field_details[field] = {
                'status': 'success',
                'value_preview': str(value)[:50] if not isinstance(value, list) else f"{len(value)} items"
            }
        else:
            missing.append(field)
            field_details[field] = {
                'status': 'missing',
                'reason': 'Not found in page or selector failed'
            }
    
    critical_missing = [f for f in critical_fields if f in missing]
    
    return {
        'total_fields': len(all_fields),
        'extracted': len(extracted),
        'missing': len(missing),
        'success_rate': len(extracted) / len(all_fields) if all_fields else 0,
        'critical_missing': critical_missing,
        'important_missing': [f for f in important_fields if f in missing],
        'field_details': field_details,
        'extracted_fields': extracted,
        'missing_fields': missing
    }


@app.get("/api/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    Get status of scraping job
    
    Args:
        job_id: Job identifier
        
    Returns:
        Job status and results if complete
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatus(**jobs[job_id])


@app.get("/api/download/{job_id}")
async def download_result(job_id: str):
    """
    Download scraped data as JSON
    
    Args:
        job_id: Job identifier
        
    Returns:
        JSON file download
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    if 'output_file' not in job:
        raise HTTPException(status_code=404, detail="Output file not found")
    
    file_path = os.path.join('data', 'outputs', job['output_file'])
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path,
        media_type='application/json',
        filename=job['output_file']
    )


@app.get("/api/patterns")
async def list_patterns():
    """
    List available scraping patterns
    
    Returns:
        List of patterns with descriptions
    """
    patterns = scraper.patterns
    
    pattern_list = []
    for name, config in patterns.items():
        pattern_list.append({
            'name': name,
            'description': config.get('description', 'No description'),
            'requires_js': config.get('requires_js', False),
            'field_count': len(config.get('selectors', {}))
        })
    
    return {'patterns': pattern_list}


@app.get("/api/jobs")
async def list_jobs(limit: int = 20):
    """
    List recent scraping jobs
    
    Args:
        limit: Maximum number of jobs to return
        
    Returns:
        List of recent jobs
    """
    sorted_jobs = sorted(
        jobs.values(),
        key=lambda x: x['created_at'],
        reverse=True
    )
    
    return {'jobs': sorted_jobs[:limit]}


@app.post("/api/analyze")
async def analyze_url(request: ScrapeRequest):
    """
    Analyze URL without scraping
    Returns pattern prediction and confidence
    
    Args:
        request: URL to analyze
        
    Returns:
        Analysis results
    """
    try:
        url_str = str(request.url)
        
        # Get AI prediction
        pattern_name, confidence, analysis = ai_detector.predict_pattern(url_str)
        
        # Get pattern info
        pattern_info = url_matcher.get_pattern_info(pattern_name)
        
        return {
            'url': url_str,
            'predicted_pattern': pattern_name,
            'confidence': confidence,
            'pattern_info': pattern_info,
            'analysis': analysis,
            'is_product_page': url_matcher.is_product_page(url_str)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/job/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a job and its output file
    
    Args:
        job_id: Job identifier
        
    Returns:
        Success message
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    # Delete output file if exists
    if 'output_file' in job:
        file_path = os.path.join('data', 'outputs', job['output_file'])
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Remove job from memory
    del jobs[job_id]
    
    return {'message': 'Job deleted successfully'}


@app.get("/api/download/{job_id}/csv")
async def download_csv(job_id: str):
    """
    Download scraped data as CSV
    
    Args:
        job_id: Job identifier
        
    Returns:
        CSV file download
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    # Check if CSV file exists (batch mode)
    if 'csv_file' in job:
        file_path = os.path.join('data', 'outputs', job['csv_file'])
        if os.path.exists(file_path):
            return FileResponse(
                file_path,
                media_type='text/csv',
                filename=job['csv_file']
            )
    
    # Generate CSV from result (single product)
    if 'result' in job:
        result = job['result']
        
        # Convert to list if single product
        if isinstance(result, dict) and 'products' in result:
            products = result['products']
        else:
            products = [result]
        
        # Generate CSV filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"product_data_{timestamp}.csv"
        csv_path = os.path.join('data', 'outputs', csv_filename)
        
        # Save as CSV
        scraper.save_to_csv(products, csv_path)
        
        return FileResponse(
            csv_path,
            media_type='text/csv',
            filename=csv_filename
        )
    
    raise HTTPException(status_code=404, detail="No data available")


# Global progress storage for image downloads
image_download_progress: Dict[str, Dict] = {}

@app.get("/api/download/{job_id}/images")
async def download_images(job_id: str, background_tasks: BackgroundTasks):
    """
    Download all scraped images as ZIP with progress tracking
    
    Args:
        job_id: Job identifier
        
    Returns:
        JSON response with download_id for progress tracking
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    if 'result' not in job:
        raise HTTPException(status_code=404, detail="No result data found")
    
    try:
        # Initialize progress tracking
        download_id = f"{job_id}_images"
        image_download_progress[download_id] = {
            'status': 'starting',
            'message': 'Initializing image download...',
            'completed': 0,
            'total': 0,
            'percentage': 0,
            'downloaded_size': 0,
            'total_size': 0,
            'zip_path': None
        }
        
        # Start background download
        background_tasks.add_task(download_images_background, job_id, download_id)
        
        return JSONResponse({
            'status': 'started',
            'download_id': download_id,
            'message': 'Image download started in background'
        })
        
    except Exception as e:
        logger.error(f"Error starting image download: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def download_images_background(job_id: str, download_id: str):
    """Background task for downloading images with progress tracking"""
    try:
        job = jobs[job_id]
        result = job['result']
        url = job['url']
        
        # Create a new image manager instance for this background task
        from modules.image_manager import ImageManager
        bg_image_manager = ImageManager()
        
        # Create folder structure for this website
        folder_path, website_name = bg_image_manager.create_website_folder(url)
        images_folder = folder_path / 'images'
        
        # Set up progress callback
        def progress_callback(progress_data):
            try:
                image_download_progress[download_id].update(progress_data)
                image_download_progress[download_id]['status'] = 'downloading'
                logger.info(f"Progress updated for {download_id}: {progress_data['message']} ({progress_data['completed']}/{progress_data['total']})")
            except Exception as e:
                logger.error(f"Error updating progress for {download_id}: {e}")
        
        bg_image_manager.set_progress_callback(progress_callback)
        logger.info(f"Progress callback set for download {download_id}")
        
        # Update progress
        image_download_progress[download_id].update({
            'status': 'downloading',
            'message': 'Starting image downloads...'
        })
        
        # Determine if batch or single and download
        if isinstance(result, dict) and 'products' in result:
            products = result['products']
            logger.info(f"Downloading images for {len(products)} products")
            bg_image_manager.download_batch_images(products, images_folder)
        else:
            logger.info(f"Downloading images for single product")
            bg_image_manager.download_product_images_concurrent(result, images_folder)
        
        # Mark as completed (no ZIP creation)
        total_downloaded = bg_image_manager.download_stats['completed']
        total_size = bg_image_manager._format_size(bg_image_manager.download_stats['downloaded_size'])
        
        image_download_progress[download_id].update({
            'status': 'completed',
            'message': f'Download completed! {total_downloaded} images saved to Downloads folder ({total_size})',
            'folder_path': str(folder_path),
            'images_folder': str(images_folder)
        })
        logger.info(f"Image download completed for job {job_id}: {total_downloaded} images")
            
    except Exception as e:
        logger.error(f"Error in background image download: {e}")
        image_download_progress[download_id].update({
            'status': 'failed',
            'message': f'Download failed: {str(e)}'
        })


@app.get("/api/download/{download_id}/progress")
async def get_download_progress(download_id: str):
    """Get progress of image download"""
    try:
        if download_id not in image_download_progress:
            logger.warning(f"Download ID not found: {download_id}")
            raise HTTPException(status_code=404, detail="Download not found")
        
        progress = image_download_progress[download_id]
        logger.info(f"Returning progress for {download_id}: status={progress.get('status')}, completed={progress.get('completed')}, total={progress.get('total')}")
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting progress for {download_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting progress: {str(e)}")


@app.get("/api/test/progress/{test_id}")
async def test_progress_tracking(test_id: str, background_tasks: BackgroundTasks):
    """Test endpoint to verify progress tracking is working"""
    
    # Initialize test progress
    image_download_progress[test_id] = {
        'status': 'testing',
        'message': 'Starting progress test...',
        'completed': 0,
        'total': 5,
        'percentage': 0,
        'downloaded_size': 0,
        'total_size': 0
    }
    
    # Start test background task
    background_tasks.add_task(test_progress_background, test_id)
    
    return JSONResponse({
        'status': 'started',
        'test_id': test_id,
        'message': 'Progress test started'
    })


async def test_progress_background(test_id: str):
    """Background task to test progress updates"""
    import asyncio
    
    try:
        for i in range(1, 6):
            await asyncio.sleep(1)  # Simulate work
            
            image_download_progress[test_id].update({
                'status': 'testing',
                'message': f'Processing step {i}/5...',
                'completed': i,
                'total': 5,
                'percentage': (i / 5) * 100,
                'downloaded_size': i * 1024,
                'total_size': 5 * 1024
            })
            
            logger.info(f"Test progress update {i}/5 for {test_id}")
        
        # Mark as completed
        image_download_progress[test_id].update({
            'status': 'completed',
            'message': 'Progress test completed!',
            'completed': 5,
            'total': 5,
            'percentage': 100
        })
        
        logger.info(f"Progress test completed for {test_id}")
        
    except Exception as e:
        logger.error(f"Error in progress test: {e}")
        image_download_progress[test_id].update({
            'status': 'failed',
            'message': f'Test failed: {str(e)}'
        })


@app.get("/api/download/{download_id}/folder")
async def get_download_folder_info(download_id: str):
    """Get information about the download folder location"""
    if download_id not in image_download_progress:
        raise HTTPException(status_code=404, detail="Download not found")
    
    progress = image_download_progress[download_id]
    
    if progress['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Download not completed yet")
    
    folder_path = progress.get('folder_path')
    images_folder = progress.get('images_folder')
    
    return JSONResponse({
        'folder_path': folder_path,
        'images_folder': images_folder,
        'message': 'Images saved to your Downloads folder'
    })


if __name__ == '__main__':
    import uvicorn
    
    logger.info("Starting Auto-Scraper AI Tool")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

