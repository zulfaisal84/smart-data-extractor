// OCR Testing Interface JavaScript
// If opening index.html as file://, the API defaults to http://127.0.0.1:5000
// Or use ?api=http://your-server:port to specify a different backend
class OCRTester {
    constructor() {
        // Allow override via URL parameter or default to same origin
        const urlParams = new URLSearchParams(window.location.search);
        this.apiBaseUrl = urlParams.get('api') ||
                          (window.location.protocol === 'file:' ? 'http://127.0.0.1:5000' : '');

        this.currentFile = null;
        this.processingStartTime = null;
        this.history = JSON.parse(localStorage.getItem('ocrHistory') || '[]');
        this.initializeElements();
        this.bindEvents();
        this.loadHistory();
    }

    initializeElements() {
        // Upload elements
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.fileInfo = document.getElementById('fileInfo');
        this.fileName = document.getElementById('fileName');
        this.fileSize = document.getElementById('fileSize');
        this.fileType = document.getElementById('fileType');
        this.removeFile = document.getElementById('removeFile');

        // Service selector
        this.ocrService = document.getElementById('ocrService');

        // Action buttons
        this.processBtn = document.getElementById('processBtn');
        this.clearBtn = document.getElementById('clearBtn');

        // Results elements
        this.resultsSection = document.getElementById('resultsSection');
        this.processingStatus = document.getElementById('processingStatus');
        this.resultContent = document.getElementById('resultContent');
        this.errorContent = document.getElementById('errorContent');
        this.processingTime = document.getElementById('processingTime');
        this.confidenceScore = document.getElementById('confidenceScore');
        this.extractedText = document.getElementById('extractedText');
        this.errorText = document.getElementById('errorText');

        // History
        this.historyList = document.getElementById('historyList');
    }

    bindEvents() {
        // File upload events
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        this.uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        this.uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        this.fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        this.removeFile.addEventListener('click', this.clearFile.bind(this));

        // Action button events
        this.processBtn.addEventListener('click', this.processDocument.bind(this));
        this.clearBtn.addEventListener('click', this.clearAll.bind(this));

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });

        // Highlight drop area
        ['dragenter', 'dragover'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, () => this.uploadArea.classList.add('highlight'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, () => this.uploadArea.classList.remove('highlight'), false);
        });
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    handleDragOver(e) {
        e.preventDefault();
    }

    handleDrop(e) {
        e.preventDefault();
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.handleFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.handleFile(files[0]);
        }
    }

    handleFile(file) {
        // Validate file type
        const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
        if (!allowedTypes.includes(file.type)) {
            this.showError('Invalid file type. Please upload PDF, JPG, or PNG files only.');
            return;
        }

        // Validate file size (10MB limit)
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            this.showError('File too large. Please upload files smaller than 10MB.');
            return;
        }

        this.currentFile = file;
        this.displayFileInfo(file);
        this.processBtn.disabled = false;
        this.hideResults();
    }

    displayFileInfo(file) {
        this.fileName.textContent = file.name;
        this.fileSize.textContent = this.formatFileSize(file.size);
        this.fileType.textContent = file.type;
        this.fileInfo.style.display = 'flex';
        this.uploadArea.classList.add('has-file');
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    clearFile() {
        this.currentFile = null;
        this.fileInput.value = '';
        this.fileInfo.style.display = 'none';
        this.uploadArea.classList.remove('has-file');
        this.processBtn.disabled = true;
        this.hideResults();
    }

    clearAll() {
        this.clearFile();
        this.ocrService.value = 'google';  // Changed default from tesseract to google
    }

    async processDocument() {
        if (!this.currentFile) return;

        this.processingStartTime = Date.now();
        this.showProcessing();

        try {
            // Step 1: Upload file
            const fileId = await this.uploadFile();
            
            // Step 2: Start processing
            const processId = await this.startProcessing(fileId);
            
            // Step 3: Poll for results
            const result = await this.pollForResults(processId);
            
            // Step 4: Display results
            this.showResults(result);
            
            // Step 5: Add to history
            this.addToHistory(result);

        } catch (error) {
            console.error('Processing error:', error);
            this.showError(error.message || 'Failed to process document');
        }
    }

    async uploadFile() {
        const formData = new FormData();
        formData.append('file', this.currentFile);

        const response = await fetch(this.apiBaseUrl + '/api/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Failed to upload file');
        }

        const data = await response.json();
        return data.file_id;
    }

    async startProcessing(fileId) {
        const response = await fetch(`${this.apiBaseUrl}/api/process/${fileId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                service: this.ocrService.value
            })
        });

        if (!response.ok) {
            throw new Error('Failed to start processing');
        }

        const data = await response.json();
        return data.process_id;
    }

    async pollForResults(processId) {
        const maxAttempts = 120; // 2 minutes maximum
        let attempts = 0;

        while (attempts < maxAttempts) {
            try {
                const statusResponse = await fetch(`${this.apiBaseUrl}/api/status/${processId}`);
                const statusData = await statusResponse.json();

                if (statusData.status === 'completed') {
                    const resultResponse = await fetch(`${this.apiBaseUrl}/api/result/${processId}`);
                    return await resultResponse.json();
                } else if (statusData.status === 'failed') {
                    throw new Error(statusData.error || 'Processing failed');
                }

                // Wait 1 second before next poll
                await new Promise(resolve => setTimeout(resolve, 1000));
                attempts++;

            } catch (error) {
                if (attempts === maxAttempts - 1) {
                    throw error;
                }
                await new Promise(resolve => setTimeout(resolve, 1000));
                attempts++;
            }
        }

        throw new Error('Processing timeout - took longer than expected');
    }

    showProcessing() {
        this.resultsSection.style.display = 'block';
        this.processingStatus.style.display = 'block';
        this.resultContent.style.display = 'none';
        this.errorContent.style.display = 'none';
        this.processBtn.disabled = true;
    }

    showResults(result) {
        const processingTime = Date.now() - this.processingStartTime;
        
        this.processingStatus.style.display = 'none';
        this.resultContent.style.display = 'block';
        this.errorContent.style.display = 'none';
        
        this.processingTime.textContent = `Processing time: ${(processingTime / 1000).toFixed(2)}s`;
        this.confidenceScore.textContent = result.confidence ? `Confidence: ${(result.confidence * 100).toFixed(1)}%` : '';
        this.extractedText.value = result.text || 'No text extracted';
        
        this.processBtn.disabled = false;
    }

    showError(message) {
        this.resultsSection.style.display = 'block';
        this.processingStatus.style.display = 'none';
        this.resultContent.style.display = 'none';
        this.errorContent.style.display = 'block';
        
        this.errorText.textContent = message;
        this.processBtn.disabled = false;
    }

    hideResults() {
        this.resultsSection.style.display = 'none';
    }

    addToHistory(result) {
        const historyItem = {
            fileName: this.currentFile.name,
            fileSize: this.formatFileSize(this.currentFile.size),
            service: this.ocrService.value,
            timestamp: new Date().toLocaleString(),
            processingTime: ((Date.now() - this.processingStartTime) / 1000).toFixed(2) + 's',
            textPreview: (result.text || '').substring(0, 100) + '...',
            fullText: result.text || '',
            confidence: result.confidence
        };

        this.history.unshift(historyItem);
        
        // Keep only last 5 items
        if (this.history.length > 5) {
            this.history = this.history.slice(0, 5);
        }

        localStorage.setItem('ocrHistory', JSON.stringify(this.history));
        this.loadHistory();
    }

    loadHistory() {
        this.historyList.innerHTML = '';

        if (this.history.length === 0) {
            this.historyList.innerHTML = '<p class="no-history">No documents processed yet</p>';
            return;
        }

        this.history.forEach((item, index) => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            historyItem.innerHTML = `
                <div class="history-info">
                    <div class="history-filename">${item.fileName}</div>
                    <div class="history-meta">
                        ${item.timestamp} • ${item.service} • ${item.processingTime}
                        ${item.confidence ? ` • ${(item.confidence * 100).toFixed(1)}%` : ''}
                    </div>
                    <div class="history-preview">${item.textPreview}</div>
                </div>
                <button class="view-result" onclick="ocrTester.showHistoryResult(${index})">View</button>
            `;
            this.historyList.appendChild(historyItem);
        });
    }

    showHistoryResult(index) {
        const item = this.history[index];
        this.resultsSection.style.display = 'block';
        this.processingStatus.style.display = 'none';
        this.resultContent.style.display = 'block';
        this.errorContent.style.display = 'none';
        
        this.processingTime.textContent = `Processing time: ${item.processingTime}`;
        this.confidenceScore.textContent = item.confidence ? `Confidence: ${(item.confidence * 100).toFixed(1)}%` : '';
        this.extractedText.value = item.fullText;
    }
}

// Initialize the OCR Tester when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.ocrTester = new OCRTester();
});

// Fallback for testing without backend (demo mode)
if (window.location.search.includes('demo=true')) {
    // Override API calls for demo
    OCRTester.prototype.uploadFile = async function() {
        await new Promise(resolve => setTimeout(resolve, 500));
        return 'demo-file-123';
    };

    OCRTester.prototype.startProcessing = async function(fileId) {
        await new Promise(resolve => setTimeout(resolve, 300));
        return 'demo-process-456';
    };

    OCRTester.prototype.pollForResults = async function(processId) {
        await new Promise(resolve => setTimeout(resolve, 2000));
        return {
            text: `Demo extracted text from ${this.currentFile.name}:\n\nThis is sample text that would be extracted from your document. In a real implementation, this would be the actual text extracted by the OCR service.\n\nThe document processing was successful and this text represents what would be found in your uploaded file.`,
            confidence: 0.95
        };
    };

    console.log('Running in demo mode - no backend required');
}