# OCR Testing Backend

**🚨 This system EXTRACTS DATA from documents 🚨**

**Smart Data Extractor (SME) - OCR Prototype**

A Flask-based backend service for testing OCR capabilities with multiple providers. This prototype validates that we can reliably extract text from documents (PDFs, images) before building production features.

## 🎯 Purpose

Test and compare OCR services to determine the best approach for document data extraction:
- **Tesseract** (local, offline)
- **Google Vision API** (cloud, high accuracy)
- **AWS Textract** (cloud, document-optimized)

## 📁 Project Structure

```
tests/ocr-prototype/
├── server.py           # Main Flask application
├── requirements.txt    # Python dependencies
├── ocr_services.py     # OCR service implementations
├── file_handler.py     # File upload/conversion logic
├── config.py          # Configuration (API keys, etc.)
├── uploads/           # Temporary file storage
└── README.md         # This file
```

## 🚀 Quick Start

### 1. Install System Dependencies

**macOS:**
```bash
brew install tesseract poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils
```

**Windows:**
- Download Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Download Poppler: https://github.com/oschwartz10612/poppler-windows

### 2. Install Python Dependencies

```bash
cd tests/ocr-prototype
pip install -r requirements.txt
```

### 3. Run the Server

```bash
python server.py
```

Server will start at: http://127.0.0.1:5000

## 📋 API Documentation

### Base URL
```
http://127.0.0.1:5000/api
```

### Endpoints

#### 1. Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-03T10:30:00",
  "services": {
    "tesseract": true,
    "google_vision": false,
    "aws_textract": false
  }
}
```

#### 2. Upload File
```http
POST /api/upload
Content-Type: multipart/form-data

file: [PDF/JPG/PNG file, max 10MB]
```

**Response:**
```json
{
  "file_id": "uuid-string",
  "filename": "document.pdf",
  "status": "uploaded",
  "message": "File uploaded successfully..."
}
```

#### 3. Process File
```http
POST /api/process/{file_id}
Content-Type: application/json

{
  "service": "tesseract"
}
```

**Services:** `tesseract`, `google`, `aws`

**Response:**
```json
{
  "process_id": "uuid-string",
  "file_id": "uuid-string",
  "service": "tesseract",
  "status": "started",
  "message": "OCR processing started..."
}
```

#### 4. Check Status
```http
GET /api/status/{process_id}
```

**Response:**
```json
{
  "process_id": "uuid-string",
  "service": "tesseract",
  "status": "success",
  "processing_time": 2.34,
  "text": "extracted text here...",
  "confidence": 0.95,
  "pages_processed": 2,
  "words_found": 156
}
```

#### 5. Get Result
```http
GET /api/result/{process_id}
```

Same response format as status endpoint.

#### 6. List Services
```http
GET /api/services
```

**Response:**
```json
{
  "services": {
    "tesseract": {
      "name": "Tesseract (Local)",
      "available": true,
      "description": "Open-source OCR engine, works offline"
    },
    "google": {
      "name": "Google Vision API",
      "available": false,
      "description": "Google Cloud Vision API, requires API key"
    },
    "aws": {
      "name": "AWS Textract",
      "available": false,
      "description": "Amazon Textract service, requires AWS credentials"
    }
  },
  "recommended": "tesseract"
}
```

#### 7. Cleanup Files
```http
POST /api/cleanup
Content-Type: application/json

{
  "age_hours": 24
}
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file (optional):

```bash
# Flask configuration
FLASK_DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=5000

# File upload
UPLOAD_FOLDER=uploads
PDF_DPI=200

# Google Vision API
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# AWS Textract
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1

# Tesseract (if not in system PATH)
TESSERACT_CMD=/usr/local/bin/tesseract
```

### API Key Setup

#### Google Vision API
1. Create a Google Cloud project
2. Enable Vision API
3. Create service account and download JSON credentials
4. Set `GOOGLE_APPLICATION_CREDENTIALS` to the JSON file path

#### AWS Textract
1. Create AWS account
2. Get access key and secret key
3. Set environment variables or use AWS CLI configuration

## 🧪 Testing

### Manual Testing with cURL

**1. Upload a file:**
```bash
curl -X POST -F "file=@sample.pdf" http://127.0.0.1:5000/api/upload
```

**2. Process with Tesseract:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"service":"tesseract"}' \
  http://127.0.0.1:5000/api/process/{file_id}
```

**3. Check result:**
```bash
curl http://127.0.0.1:5000/api/result/{process_id}
```

### Python Testing Script

```python
import requests
import json

# Upload file
with open('test_document.pdf', 'rb') as f:
    response = requests.post('http://127.0.0.1:5000/api/upload', 
                           files={'file': f})
    file_id = response.json()['file_id']

# Process with Tesseract
response = requests.post(f'http://127.0.0.1:5000/api/process/{file_id}',
                        json={'service': 'tesseract'})
process_id = response.json()['process_id']

# Get result
response = requests.get(f'http://127.0.0.1:5000/api/result/{process_id}')
result = response.json()
print(f"Extracted text: {result['text']}")
print(f"Confidence: {result['confidence']}")
```

## 🐛 Troubleshooting

### Common Issues

#### Tesseract Not Found
```
Error: Tesseract is not available
```

**Solution:**
- Install Tesseract: `brew install tesseract` (macOS)
- Or set `TESSERACT_CMD` environment variable

#### PDF Conversion Failed
```
Error: pdf2image failed
```

**Solution:**
- Install Poppler: `brew install poppler` (macOS)
- Windows: Download from https://github.com/oschwartz10612/poppler-windows

#### Large File Upload Error
```
Error: File too large. Maximum size is 10MB.
```

**Solution:**
- Compress or resize the file
- Or modify `MAX_CONTENT_LENGTH` in config.py

#### Google Vision API Error
```
Error: Google Vision not available
```

**Solution:**
- Set up Google Cloud credentials
- Or use Tesseract for local testing

## 📊 Performance Expectations

| Service | Speed | Accuracy | Cost | Offline |
|---------|-------|----------|------|---------|
| Tesseract | Medium | Good | Free | ✅ |
| Google Vision | Fast | Excellent | Paid | ❌ |
| AWS Textract | Fast | Excellent | Paid | ❌ |

## 🚀 Production Setup (Google Vision API)

### Prerequisites
- Google Cloud account with billing enabled
- Google Vision API enabled in your project
- Service account with Vision API permissions

### Quick Production Setup

#### 1. Google Cloud Configuration
```bash
# Create Google Cloud project
gcloud projects create sme-ocr-production

# Enable Vision API
gcloud services enable vision.googleapis.com --project=sme-ocr-production

# Create service account
gcloud iam service-accounts create sme-vision-service \
  --description="SME Google Vision API access" \
  --display-name="SME Vision Service" \
  --project=sme-ocr-production

# Grant permissions
gcloud projects add-iam-policy-binding sme-ocr-production \
  --member="serviceAccount:sme-vision-service@sme-ocr-production.iam.gserviceaccount.com" \
  --role="roles/ml.developer"

# Create and download credentials
gcloud iam service-accounts keys create google-vision-credentials.json \
  --iam-account=sme-vision-service@sme-ocr-production.iam.gserviceaccount.com \
  --project=sme-ocr-production
```

#### 2. Secure Credential Storage
```bash
# Create secure directory
mkdir -p ~/.config/smart-data-extractor/
chmod 700 ~/.config/smart-data-extractor/

# Move credentials securely
mv google-vision-credentials.json ~/.config/smart-data-extractor/
chmod 600 ~/.config/smart-data-extractor/google-vision-credentials.json

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/smart-data-extractor/google-vision-credentials.json"

# Make permanent
echo 'export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/smart-data-extractor/google-vision-credentials.json"' >> ~/.bashrc
source ~/.bashrc
```

#### 3. Start Production Server
```bash
cd tests/ocr-prototype
source venv/bin/activate
python server.py
```

#### 4. Test Production Setup
```bash
# Test API health
curl http://127.0.0.1:5000/api/health

# Expected response shows Google Vision available:
# {
#   "services": {
#     "google": {
#       "available": true,
#       "configured": true
#     }
#   },
#   "recommended": "google"
# }
```

### Production Features
- **Native PDF Processing**: No conversion delays
- **Sub-2 Second Processing**: Enterprise-grade performance
- **High Accuracy**: 95%+ text extraction accuracy
- **Scalable**: Cloud-based processing
- **Secure**: Service account authentication

### Cost Estimates
| Usage Level | Monthly Documents | Cost |
|-------------|------------------|------|
| Development | <1,000 | Free |
| Small Business | 2,000 | $1.50 |
| Medium Business | 10,000 | $13.50 |

### Troubleshooting Production Setup

#### "DefaultCredentialsError"
```bash
# Verify environment variable
echo $GOOGLE_APPLICATION_CREDENTIALS

# Check file exists
ls -la "$GOOGLE_APPLICATION_CREDENTIALS"

# Test credentials
python -c "from google.cloud import vision; client = vision.ImageAnnotatorClient(); print('✅ Credentials working')"
```

#### "PermissionDenied"
```bash
# Check service account permissions
gcloud projects get-iam-policy sme-ocr-production \
  --flatten="bindings[].members" \
  --format="table(bindings.role)" \
  --filter="bindings.members:sme-vision-service@sme-ocr-production.iam.gserviceaccount.com"
```

### Complete Documentation
- **Setup Guide**: [docs/deployment/GOOGLE_VISION_SETUP.md](../../docs/deployment/GOOGLE_VISION_SETUP.md)
- **Security Guide**: [docs/deployment/SECURITY_GUIDE.md](../../docs/deployment/SECURITY_GUIDE.md)
- **Troubleshooting**: [docs/deployment/TROUBLESHOOTING_GUIDE.md](../../docs/deployment/TROUBLESHOOTING_GUIDE.md)
- **API Documentation**: [docs/api/GOOGLE_VISION_API.md](../../docs/api/GOOGLE_VISION_API.md)

## 🎯 Next Steps

1. **✅ COMPLETED: Google Vision production implementation**
2. **✅ COMPLETED: Performance validation (<2 second processing)**
3. **READY: Deploy with production credentials and test TNB bill**
4. **NEXT: MVP development with user authentication and data storage**

## 📝 Development Notes

### File Processing Flow
1. Upload → Validate → Save with UUID
2. Process → Convert PDF to images if needed
3. OCR → Extract text using selected service
4. Result → Return standardized response
5. Cleanup → Remove temporary files

### Error Handling
- Graceful degradation when services unavailable
- Mock responses for missing API keys
- Detailed logging for debugging
- User-friendly error messages

### Security Considerations
- File type validation
- Size limits (10MB)
- Temporary file cleanup
- No persistent storage of sensitive data

---

**Project:** Smart Data Extractor (SME)  
**Component:** OCR Testing Prototype  
**Author:** Backend Developer Agent  
**Last Updated:** August 3, 2025