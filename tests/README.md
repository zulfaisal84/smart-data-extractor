# Smart Data Extractor - AI Testing Suite

This directory contains all testing infrastructure for validating AI extraction capabilities before building the UI.

## 📁 Directory Structure

```
tests/
├── ai-mockup/           # AI service testing code
│   ├── test-runner.py   # Main test execution script
│   ├── configs/         # Test configuration files
│   └── results/         # Test results (auto-generated)
│
├── test-documents/      # Sample documents for testing
│   ├── invoices/        # Invoice samples
│   ├── receipts/        # Receipt samples
│   ├── purchase-orders/ # PO samples
│   ├── mixed-batches/   # Mixed document sets
│   └── edge-cases/      # Problematic documents
│
└── AI_TESTING_CHECKLIST.md  # Comprehensive testing guide
```

## 🚀 Quick Start

1. **Set up test documents** (you need to add real PDFs/images):
   ```bash
   # Add sample documents to appropriate folders
   cp your_invoice.pdf tests/test-documents/invoices/clear/invoice_001.pdf
   ```

2. **Configure API keys** (create this file):
   ```bash
   # tests/ai-mockup/configs/api_keys.json
   {
     "google_document_ai": "your-api-key",
     "openai": "your-api-key",
     "aws": {
       "access_key": "your-key",
       "secret_key": "your-secret"
     }
   }
   ```

3. **Run basic test suite**:
   ```bash
   cd tests/ai-mockup
   python test-runner.py
   ```

## 🧪 Available Test Suites

### 1. Basic Test Suite (`basic_test_suite.json`)
- Tests field extraction accuracy
- Compares AI services
- Validates confidence scoring

### 2. Pattern Learning Test (`pattern_learning_test.json`)
- Tests correction learning
- Validates pattern application
- Measures improvement over time

### 3. Batch Processing Test (`batch_processing_test.json`)
- Tests multiple document handling
- Validates classification accuracy
- Measures processing speed

### 4. Edge Cases Test (`edge_cases_test.json`)
- Tests problematic documents
- Validates error handling
- Ensures graceful failures

## 📊 Test Metrics

Each test run generates metrics for:
- **Accuracy**: % of fields correctly extracted
- **Speed**: Processing time per document
- **Cost**: Estimated API costs
- **Confidence**: Correlation with accuracy
- **Errors**: Types and recovery

## 🔍 What We're Testing

### Core Questions:
1. Can we achieve 85%+ accuracy on clear documents?
2. Which AI service works best for each document type?
3. Does pattern learning actually improve accuracy?
4. Can we handle poor quality documents gracefully?
5. Is batch processing fast enough for user experience?
6. Are confidence scores meaningful?
7. What's our real cost per document?

### Critical Validations:
- Document type detection accuracy
- Field extraction precision
- Learning effectiveness
- Error recovery
- Performance under load
- Cost optimization potential

## 📈 Success Criteria

Before proceeding with UI development, we need:

✅ **Accuracy**: 85%+ on standard documents  
✅ **Speed**: <5 seconds per document  
✅ **Cost**: <$0.10 per document average  
✅ **Reliability**: Graceful error handling  
✅ **Learning**: Demonstrable improvement  

## 🛠️ Adding New Tests

1. Create test configuration in `configs/`
2. Add test documents to appropriate folders
3. Update test-runner.py if needed
4. Document results and learnings

## 📝 Test Document Naming Convention

- Clear quality: `{type}_clear_{number}.{ext}`
- Poor quality: `{type}_poor_{number}.{ext}`
- Edge cases: `{type}_edge_{description}.{ext}`

Example: `invoice_clear_001.pdf`, `receipt_poor_005.jpg`

## ⚠️ Important Notes

1. **Real Documents**: Use actual documents (with sensitive data removed)
2. **Variety**: Include documents from different sources
3. **Quality Range**: Test with various quality levels
4. **Edge Cases**: Don't forget unusual scenarios
5. **Cost Tracking**: Monitor API usage during tests

## 🔗 Next Steps

After successful testing:
1. Choose optimal AI services
2. Finalize extraction approach
3. Design pattern learning system
4. Build confidence scoring
5. Implement batch processing
6. Create UI with confidence

---

Remember: **Test thoroughly now to avoid DE's fate!**