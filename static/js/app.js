// Modern Veefyed Scraper UI JavaScript

// Configuration
const API_BASE = window.location.origin;

// Global Variables
let currentJobId = null;
let statusCheckInterval = null;

// DOM Elements
const scrapeForm = document.getElementById('scrapeForm');
const urlInput = document.getElementById('urlInput');
const scrapeAllCheckbox = document.getElementById('scrapeAll');
const uploadImagesCheckbox = document.getElementById('uploadImages');
const runBtn = document.getElementById('runBtn');
const statusSection = document.getElementById('statusSection');
const statusIndicator = document.getElementById('statusIndicator');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const statusDetails = document.getElementById('statusDetails');
const closeStatusBtn = document.getElementById('closeStatusBtn');
const resultsSection = document.getElementById('resultsSection');
const resultsBadge = document.getElementById('resultsBadge');
const previewContent = document.getElementById('previewContent');
const downloadCSVBtn = document.getElementById('downloadCSVBtn');
const downloadJSONBtn = document.getElementById('downloadJSONBtn');
const downloadImagesBtn = document.getElementById('downloadImagesBtn');
const expandPreviewBtn = document.getElementById('expandPreviewBtn');
const dataPreviewModal = document.getElementById('dataPreviewModal');
const dataPreviewContent = document.getElementById('dataPreviewContent');
const closePreviewBtn = document.getElementById('closePreviewBtn');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');
const showErrorDetailsBtn = document.getElementById('showErrorDetailsBtn');
const errorDetailsModal = document.getElementById('errorDetailsModal');
const errorDetailsContent = document.getElementById('errorDetailsContent');
const closeErrorBtn = document.getElementById('closeErrorBtn');
const closeErrorDetailsBtn = document.getElementById('closeErrorDetailsBtn');
const newScrapeBtn = document.getElementById('newScrapeBtn');
const oneDriveSection = document.getElementById('oneDriveSection');
const uploadDataBtn = document.getElementById('uploadDataBtn');
const uploadImagesBtn = document.getElementById('uploadImagesBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Event listeners
    scrapeForm.addEventListener('submit', handleScrapeSubmit);
    downloadCSVBtn.addEventListener('click', () => handleDownload('csv'));
    downloadJSONBtn.addEventListener('click', () => handleDownload('json'));
    downloadImagesBtn.addEventListener('click', handleDownloadImages);
    expandPreviewBtn.addEventListener('click', handleViewData);
    closePreviewBtn.addEventListener('click', () => hideModal(dataPreviewModal));
    closeStatusBtn.addEventListener('click', () => hideElement(statusSection));
    closeErrorBtn.addEventListener('click', () => hideElement(errorSection));
    closeErrorDetailsBtn.addEventListener('click', () => hideModal(errorDetailsModal));
    showErrorDetailsBtn.addEventListener('click', showErrorDetails);
    newScrapeBtn.addEventListener('click', resetForm);
    uploadDataBtn.addEventListener('click', handleUploadData);
    uploadImagesBtn.addEventListener('click', handleUploadImages);
    
    // Update status indicator
    updateStatusIndicator('Ready', 'success');
});

// Form submission handler
async function handleScrapeSubmit(e) {
    e.preventDefault();
    
    const url = urlInput.value.trim();
    const scrapeAll = scrapeAllCheckbox.checked;
    const uploadImages = uploadImagesCheckbox.checked;
    
    if (!url) {
        showError('Please enter a valid URL');
        return;
    }
    
    try {
        // Update UI state
        setLoadingState(true);
        hideElement(errorSection);
        hideElement(resultsSection);
        showElement(statusSection);
        
        updateStatusIndicator('Scraping...', 'loading');
        updateProgress(0, 'Starting scrape...');
        
        // Submit scrape request
        const response = await fetch(`${API_BASE}/api/scrape`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: url,
                pattern: null,
                use_ai: true,
                scrape_all_products: scrapeAll,
                max_products: 999999,
                upload_images: uploadImages
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentJobId = data.job_id;
            updateProgress(10, 'Job started successfully...');
            
            // Start status checking
            startStatusChecking();
        } else {
            throw new Error(data.detail || 'Failed to start scraping');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message);
        setLoadingState(false);
        updateStatusIndicator('Error', 'error');
    }
}

// Status checking
function startStatusChecking() {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
    
    statusCheckInterval = setInterval(checkJobStatus, 2000);
    checkJobStatus(); // Check immediately
}

async function checkJobStatus() {
    if (!currentJobId) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/status/${currentJobId}`);
        const data = await response.json();
        
        if (response.ok) {
            updateJobStatus(data);
        } else {
            throw new Error(data.detail || 'Failed to check status');
        }
    } catch (error) {
        console.error('Status check error:', error);
        clearInterval(statusCheckInterval);
        showError('Failed to check job status');
        setLoadingState(false);
    }
}

function updateJobStatus(data) {
    const status = data.status;
    const progress = getProgressPercentage(status);
    
    updateProgress(progress, getStatusMessage(data));
    
    if (status === 'completed') {
        clearInterval(statusCheckInterval);
        setLoadingState(false);
        hideElement(statusSection);
        showResults(data);
        updateStatusIndicator('Completed', 'success');
    } else if (status === 'failed') {
        clearInterval(statusCheckInterval);
        setLoadingState(false);
        hideElement(statusSection);
        showError(data.error || 'Scraping failed');
        updateStatusIndicator('Failed', 'error');
    }
}

function getProgressPercentage(status) {
    switch (status) {
        case 'pending': return 20;
        case 'running': return 60;
        case 'completed': return 100;
        case 'failed': return 0;
        default: return 10;
    }
}

function getStatusMessage(data) {
    if (data.is_batch) {
        return `Batch scraping: ${data.products_scraped || 0} products found`;
    } else {
        return data.status === 'running' ? 'Extracting product data...' : 'Processing...';
    }
}

// Results display
function showResults(data) {
    showElement(resultsSection);
    
    // Update results badge
    if (data.status === 'completed') {
        resultsBadge.textContent = '✅ Success';
        resultsBadge.className = 'results-badge success';
    }
    
    // Show preview
    if (data.is_batch && data.result.products) {
        showBatchPreview(data.result.products);
    } else if (data.result) {
        showSinglePreview(data.result);
    }
    
    // Show OneDrive section if images were uploaded
    if (uploadImagesCheckbox.checked) {
        showElement(oneDriveSection);
    }
}

function showSinglePreview(product) {
    previewContent.innerHTML = `
        <div class="preview-grid">
            <div class="preview-item">
                <span class="preview-label">Product Name:</span>
                <span class="preview-value">${product.product_name || 'N/A'}</span>
            </div>
            <div class="preview-item">
                <span class="preview-label">Brand:</span>
                <span class="preview-value">${product.brand_name || 'N/A'}</span>
            </div>
            <div class="preview-item">
                <span class="preview-label">Category:</span>
                <span class="preview-value">${product.category || 'N/A'}</span>
            </div>
            <div class="preview-item">
                <span class="preview-label">Product ID:</span>
                <span class="preview-value">${product.product_id || 'N/A'}</span>
            </div>
        </div>
    `;
}

function showBatchPreview(products) {
    const count = products.length;
    const sampleProducts = products.slice(0, 3);
    
    previewContent.innerHTML = `
        <div class="batch-summary">
            <div class="batch-count">
                <span class="count-number">${count}</span>
                <span class="count-label">Products Scraped</span>
            </div>
            <div class="sample-products">
                <h4>Sample Products:</h4>
                ${sampleProducts.map(p => `
                    <div class="sample-item">
                        <strong>${p.product_name || 'Unnamed Product'}</strong>
                        <span>${p.brand_name || 'Unknown Brand'}</span>
                    </div>
                `).join('')}
                ${count > 3 ? `<div class="more-indicator">+${count - 3} more products</div>` : ''}
            </div>
        </div>
    `;
}

// Download handlers
async function handleDownload(format) {
    if (!currentJobId) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/download/${currentJobId}/${format}`);
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `scraped_data_${currentJobId.substring(0, 8)}.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            updateStatusIndicator('Downloaded', 'success');
        } else {
            throw new Error('Download failed');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to download file');
    }
}

async function handleDownloadImages() {
    if (!currentJobId) return;
    
    try {
        // Start the download process
        const response = await fetch(`${API_BASE}/api/download/${currentJobId}/images`);
        
        if (response.ok) {
            const data = await response.json();
            const downloadId = data.download_id;
            
            // Show progress modal
            showImageDownloadProgress(downloadId);
            
        } else {
            const errorData = await response.json();
            showError(errorData.detail || 'Failed to start image download');
        }
    } catch (error) {
        showError('Failed to start image download: ' + error.message);
    }
}

// Image download progress modal
function showImageDownloadProgress(downloadId) {
    // Create progress modal if it doesn't exist
    let progressModal = document.getElementById('imageProgressModal');
    
    if (!progressModal) {
        progressModal = document.createElement('div');
        progressModal.id = 'imageProgressModal';
        progressModal.className = 'modal';
        progressModal.innerHTML = `
            <div class="modal-content" style="max-width: 500px;">
                <div class="modal-header">
                    <h3>📥 Downloading Images</h3>
                    <button class="close-btn" onclick="closeImageProgressModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="progress-container">
                        <div class="progress-bar">
                            <div id="imageProgressFill" class="progress-fill" style="width: 0%"></div>
                        </div>
                        <div id="imageProgressText" class="progress-text">Initializing...</div>
                        <div id="imageProgressStats" class="progress-stats"></div>
                    </div>
                    <div id="imageDownloadComplete" class="download-complete" style="display: none;">
                        <div class="success-message">✅ Download completed!</div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(progressModal);
    }
    
    // Show modal
    progressModal.style.display = 'flex';
    
    // Start polling for progress
    pollImageDownloadProgress(downloadId);
}

async function pollImageDownloadProgress(downloadId) {
    const progressFill = document.getElementById('imageProgressFill');
    const progressText = document.getElementById('imageProgressText');
    const progressStats = document.getElementById('imageProgressStats');
    const downloadComplete = document.getElementById('imageDownloadComplete');
    
    const poll = async () => {
        try {
            const response = await fetch(`${API_BASE}/api/download/${downloadId}/progress`);
            
            if (!response.ok) {
                progressText.textContent = `❌ Error checking progress: ${response.status}`;
                return;
            }
            
            const progress = await response.json();
            
            // Update progress bar
            const percentage = Math.round(progress.percentage || 0);
            progressFill.style.width = `${percentage}%`;
            
            // Update text
            progressText.textContent = progress.message || 'Processing...';
            
            // Update stats
            if (progress.total > 0) {
                const downloadedSize = formatFileSize(progress.downloaded_size || 0);
                const totalSize = formatFileSize(progress.total_size || 0);
                progressStats.innerHTML = `
                    <div>Images: ${progress.completed}/${progress.total}</div>
                    <div>Size: ${downloadedSize} / ${totalSize}</div>
                    ${progress.failed > 0 ? `<div style="color: var(--error);">Failed: ${progress.failed}</div>` : ''}
                `;
            }
            
            // Check if completed
            if (progress.status === 'completed') {
                progressText.textContent = progress.message;
                
                // Show completion message
                const completionInfo = document.createElement('div');
                completionInfo.style.cssText = 'margin: 1rem 0; padding: 1rem; background: var(--gray-50); border-radius: var(--radius-md); font-size: 0.875rem;';
                completionInfo.innerHTML = `
                    <div style="margin-bottom: 0.5rem; color: var(--success);"><strong>✅ Images Downloaded Successfully!</strong></div>
                    <div style="margin-bottom: 0.5rem;"><strong>📁 Location:</strong></div>
                    <div style="color: var(--primary); font-family: monospace; background: white; padding: 0.5rem; border-radius: var(--radius-sm); word-break: break-all;">
                        ~/Downloads/ScrapedImages/
                    </div>
                    <div style="margin-top: 0.5rem; color: var(--gray-600); font-size: 0.8rem;">
                        Open your Downloads folder and look for the "ScrapedImages" folder
                    </div>
                `;
                
                // Add close button
                const closeButton = document.createElement('button');
                closeButton.textContent = '✅ Close';
                closeButton.className = 'action-btn';
                closeButton.style.cssText = 'width: 100%; margin-top: 1rem; background: var(--success); color: white; border-color: var(--success);';
                closeButton.onclick = () => closeImageProgressModal();
                completionInfo.appendChild(closeButton);
                
                downloadComplete.appendChild(completionInfo);
                downloadComplete.style.display = 'block';
                
                return; // Stop polling
            } else if (progress.status === 'failed') {
                progressText.textContent = `❌ ${progress.message}`;
                progressStats.innerHTML = '<div style="color: var(--error);">Download failed</div>';
                return; // Stop polling
            }
            
            // Continue polling if still in progress
            setTimeout(poll, 1000);
            
        } catch (error) {
            console.error('Error polling progress:', error);
            progressText.textContent = '❌ Error checking progress';
        }
    };
    
    poll();
}

function closeImageProgressModal() {
    const modal = document.getElementById('imageProgressModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// View full data - User-friendly view
async function handleViewData() {
    if (!currentJobId) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/status/${currentJobId}`);
        const data = await response.json();
        
        if (response.ok && data.result) {
            // Check if batch or single product
            if (data.is_batch && data.result.products) {
                renderBatchProductDetails(data.result.products);
            } else {
                renderSingleProductDetails(data.result);
            }
            showModal(dataPreviewModal);
        } else {
            showError('No data available to preview');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to load data preview');
    }
}

// Render single product details
function renderSingleProductDetails(product) {
    const mainImage = product.product_image_url || product.product_images?.[0] || '';
    const galleryImages = product.product_images || [];
    
    let html = `
        <div class="product-details-view">
            <div class="product-details-main">
                ${mainImage ? `
                    <div class="product-details-image">
                        <img src="${mainImage}" alt="${product.product_name || 'Product Image'}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%27250%27 height=%27250%27%3E%3Crect fill=%27%23f3f4f6%27 width=%27250%27 height=%27250%27/%3E%3Ctext x=%2750%25%27 y=%2750%25%27 text-anchor=%27middle%27 dy=%27.3em%27 fill=%27%239ca3af%27 font-family=%27sans-serif%27 font-size=%2714%27%3ENo Image%3C/text%3E%3C/svg%3E'">
                    </div>
                ` : ''}
                
                <div class="product-details-info">
                    ${renderInfoItem('Product Name', product.product_name)}
                    ${renderInfoItem('Brand', product.brand_name)}
                    ${renderInfoItem('Product ID', product.product_id)}
                    ${renderInfoItem('SKU', product.barcode || product.product_id)}
                    ${renderInfoItem('Category', product.category)}
                    ${renderInfoItem('Subcategory', product.subcategory)}
                    ${renderInfoItem('Product Type', product.product_type)}
                    ${renderInfoItem('Price', product.price || 'N/A')}
                    ${renderInfoItem('Rating', product.rating ? `${product.rating} ⭐ (${product.review_count || 0} reviews)` : 'N/A')}
                    ${renderInfoItem('Stock Status', product.stock_quantity || 'N/A')}
                    ${renderInfoItem('Country of Origin', product.country_of_origin)}
                    ${renderInfoItem('Color', product.product_colour)}
                </div>
            </div>
            
            ${product.product_description ? `
                <div class="info-item full-width" style="margin-top: var(--space-6);">
                    <div class="info-label">Description</div>
                    <div class="info-value">${escapeHtml(product.product_description)}</div>
                </div>
            ` : ''}
            
            ${product.ingredients ? `
                <div class="info-item full-width" style="margin-top: var(--space-4);">
                    <div class="info-label">Ingredients</div>
                    <div class="info-value">${escapeHtml(product.ingredients)}</div>
                </div>
            ` : ''}
            
            ${product.benefits ? `
                <div class="info-item full-width" style="margin-top: var(--space-4);">
                    <div class="info-label">Benefits</div>
                    <div class="info-value">${escapeHtml(product.benefits)}</div>
                </div>
            ` : ''}
            
            ${product.use_instructions ? `
                <div class="info-item full-width" style="margin-top: var(--space-4);">
                    <div class="info-label">How to Use</div>
                    <div class="info-value">${escapeHtml(product.use_instructions)}</div>
                </div>
            ` : ''}
            
            ${galleryImages.length > 0 ? `
                <div class="product-gallery">
                    <h4>Product Gallery (${galleryImages.length} images)</h4>
                    <div class="gallery-grid">
                        ${galleryImages.map(img => `
                            <div class="gallery-item">
                                <img src="${img}" alt="Product Image" onerror="this.style.display='none'">
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
    
    dataPreviewContent.innerHTML = html;
}

// Render batch product details with accordion
function renderBatchProductDetails(products) {
    let html = `
        <div class="product-accordion">
            <div style="margin-bottom: var(--space-4); padding-bottom: var(--space-4); border-bottom: 2px solid var(--gray-200);">
                <h3 style="font-size: 1.5rem; font-weight: 600; color: var(--gray-800); margin-bottom: var(--space-2);">
                    ${products.length} Products
                </h3>
                <p style="color: var(--gray-600);">Click on any product to view details</p>
            </div>
    `;
    
    products.forEach((product, index) => {
        const mainImage = product.product_image_url || product.product_images?.[0] || '';
        
        html += `
            <div class="accordion-item" data-index="${index}">
                <button class="accordion-header" onclick="toggleAccordion(${index})">
                    <div style="display: flex; align-items: center; gap: var(--space-4); flex: 1;">
                        ${mainImage ? `
                            <img src="${mainImage}" 
                                 alt="${product.product_name || 'Product'}" 
                                 style="width: 60px; height: 60px; object-fit: cover; border-radius: var(--radius-md); border: 1px solid var(--gray-200);"
                                 onerror="this.style.display='none'">
                        ` : ''}
                        <div style="text-align: left;">
                            <div class="accordion-title">${product.product_name || 'Unnamed Product'}</div>
                            <div style="font-size: 0.875rem; color: var(--gray-600); margin-top: var(--space-1);">
                                ${product.brand_name || 'Unknown Brand'} • ${product.category || 'Uncategorized'}
                            </div>
                        </div>
                    </div>
                    <span class="accordion-icon">+</span>
                </button>
                <div class="accordion-content">
                    <div class="product-details-view compact">
                        ${renderProductDetailsContent(product)}
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    dataPreviewContent.innerHTML = html;
}

// Render product details content (reusable for accordion items)
function renderProductDetailsContent(product) {
    const mainImage = product.product_image_url || product.product_images?.[0] || '';
    const galleryImages = product.product_images || [];
    
    return `
        <div class="product-details-main">
            ${mainImage ? `
                <div class="product-details-image">
                    <img src="${mainImage}" alt="${product.product_name || 'Product Image'}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%27120%27 height=%27120%27%3E%3Crect fill=%27%23f3f4f6%27 width=%27120%27 height=%27120%27/%3E%3Ctext x=%2750%25%27 y=%2750%25%27 text-anchor=%27middle%27 dy=%27.3em%27 fill=%27%239ca3af%27 font-family=%27sans-serif%27 font-size=%2712%27%3ENo Image%3C/text%3E%3C/svg%3E'">
                </div>
            ` : ''}
            
            <div class="product-details-info">
                ${renderInfoItem('Product Name', product.product_name)}
                ${renderInfoItem('Brand', product.brand_name)}
                ${renderInfoItem('Product ID', product.product_id)}
                ${renderInfoItem('SKU', product.barcode || product.product_id)}
                ${renderInfoItem('Category', product.category)}
                ${renderInfoItem('Subcategory', product.subcategory)}
                ${renderInfoItem('Product Type', product.product_type)}
                ${renderInfoItem('Price', product.price || 'N/A')}
                ${renderInfoItem('Rating', product.rating ? `${product.rating} ⭐` : 'N/A')}
                ${renderInfoItem('Stock', product.stock_quantity || 'N/A')}
                ${renderInfoItem('Country', product.country_of_origin)}
                ${renderInfoItem('Color', product.product_colour)}
            </div>
        </div>
        
        ${product.product_description ? `
            <div class="info-item full-width" style="margin-top: var(--space-4);">
                <div class="info-label">Description</div>
                <div class="info-value">${escapeHtml(product.product_description)}</div>
            </div>
        ` : ''}
        
        ${product.ingredients ? `
            <div class="info-item full-width" style="margin-top: var(--space-4);">
                <div class="info-label">Ingredients</div>
                <div class="info-value">${escapeHtml(product.ingredients)}</div>
            </div>
        ` : ''}
        
        ${galleryImages.length > 0 ? `
            <div class="product-gallery" style="margin-top: var(--space-6);">
                <h4>Gallery (${galleryImages.length} images)</h4>
                <div class="gallery-grid">
                    ${galleryImages.map(img => `
                        <div class="gallery-item">
                            <img src="${img}" alt="Product Image" onerror="this.style.display='none'">
                        </div>
                    `).join('')}
                </div>
            </div>
        ` : ''}
    `;
}

// Helper function to render info items
function renderInfoItem(label, value) {
    if (!value || value === 'N/A' || value === '') return '';
    
    return `
        <div class="info-item">
            <div class="info-label">${label}</div>
            <div class="info-value">${escapeHtml(String(value))}</div>
        </div>
    `;
}

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Toggle accordion item
function toggleAccordion(index) {
    const item = document.querySelector(`.accordion-item[data-index="${index}"]`);
    const content = item.querySelector('.accordion-content');
    const isActive = item.classList.contains('active');
    
    // Close all other items
    document.querySelectorAll('.accordion-item').forEach(otherItem => {
        if (otherItem !== item) {
            otherItem.classList.remove('active');
            const otherContent = otherItem.querySelector('.accordion-content');
            otherContent.style.maxHeight = '0';
        }
    });
    
    // Toggle current item
    if (isActive) {
        item.classList.remove('active');
        content.style.maxHeight = '0';
    } else {
        item.classList.add('active');
        content.style.maxHeight = content.scrollHeight + 'px';
    }
}

// Make toggleAccordion available globally
window.toggleAccordion = toggleAccordion;

// Upload handlers (placeholders)
async function handleUploadData() {
    showError('OneDrive upload not configured. Please set up your credentials.');
}

async function handleUploadImages() {
    showError('OneDrive upload not configured. Please set up your credentials.');
}

// Error handling
function showError(message, details = null) {
    errorMessage.textContent = message;
    
    if (details) {
        errorDetailsContent.innerHTML = `<pre>${details}</pre>`;
        showElement(showErrorDetailsBtn);
    } else {
        hideElement(showErrorDetailsBtn);
    }
    
    showElement(errorSection);
    updateStatusIndicator('Error', 'error');
}

function showErrorDetails() {
    showModal(errorDetailsModal);
}

// UI utility functions
function showElement(element) {
    if (element) element.style.display = 'block';
}

function hideElement(element) {
    if (element) element.style.display = 'none';
}

function showModal(modal) {
    if (modal) modal.style.display = 'flex';
}

function hideModal(modal) {
    if (modal) modal.style.display = 'none';
}

function setLoadingState(loading) {
    if (loading) {
        runBtn.disabled = true;
        runBtn.querySelector('.btn-text').textContent = 'Scraping...';
        runBtn.querySelector('.btn-loader').style.display = 'block';
        runBtn.querySelector('.btn-icon').style.display = 'none';
    } else {
        runBtn.disabled = false;
        runBtn.querySelector('.btn-text').textContent = 'Start Scraping';
        runBtn.querySelector('.btn-loader').style.display = 'none';
        runBtn.querySelector('.btn-icon').style.display = 'block';
    }
}

function updateStatusIndicator(text, type) {
    const indicator = statusIndicator.querySelector('span');
    const dot = statusIndicator.querySelector('.status-dot');
    
    if (indicator) indicator.textContent = text;
    
    if (dot) {
        dot.className = 'status-dot';
        if (type === 'loading') {
            dot.style.background = 'var(--warning)';
            dot.style.animation = 'pulse 1s infinite';
        } else if (type === 'success') {
            dot.style.background = 'var(--success)';
            dot.style.animation = 'none';
        } else if (type === 'error') {
            dot.style.background = 'var(--error)';
            dot.style.animation = 'none';
        }
    }
}

function updateProgress(percentage, message) {
    if (progressFill) {
        progressFill.style.width = `${percentage}%`;
    }
    if (progressText) {
        progressText.textContent = message;
    }
}

function resetForm() {
    // Clear form
    urlInput.value = '';
    scrapeAllCheckbox.checked = false;
    uploadImagesCheckbox.checked = false;
    
    // Reset state
    currentJobId = null;
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
    
    // Hide sections
    hideElement(statusSection);
    hideElement(resultsSection);
    hideElement(errorSection);
    hideElement(oneDriveSection);
    
    // Reset UI
    setLoadingState(false);
    updateStatusIndicator('Ready', 'success');
    updateProgress(0, 'Ready to scrape');
}

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Global functions for modal close buttons
window.closeImageProgressModal = closeImageProgressModal;