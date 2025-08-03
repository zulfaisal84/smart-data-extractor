# OCR Testing Documents

This directory contains guidelines for testing the OCR prototype with different types of documents.

## Test Document Types

### 1. **PDFs** (.pdf)
- **Text-based PDFs**: Documents with selectable text
- **Scanned PDFs**: Image-based PDFs requiring OCR
- **Mixed PDFs**: Combination of text and images

### 2. **Images** (.jpg, .jpeg, .png)
- **High-quality scans**: Clear, high-resolution documents
- **Mobile photos**: Pictures taken with phone cameras
- **Poor quality**: Blurry, dark, or low-resolution images

## Where to Get Sample Documents

### Free Document Sources:

1. **Government Forms**:
   - IRS tax forms: https://www.irs.gov/forms-pubs
   - Sample invoices and receipts from government websites

2. **Sample Business Documents**:
   - Create simple invoices using Google Docs or Word
   - Take photos of retail receipts
   - Print and scan text documents

3. **Academic Papers**:
   - ArXiv preprints: https://arxiv.org/
   - Public domain academic papers

4. **News Articles**:
   - Print web pages to PDF
   - Screenshot news articles

### Creating Your Own Test Documents:

1. **Simple Text Document**:
   ```
   Invoice #12345
   Date: August 3, 2025
   Customer: John Doe
   Amount: $150.00
   Description: Consulting Services
   ```

2. **Table-based Document**:
   Create a simple table with product names, quantities, and prices

3. **Mixed Content**:
   Combine text, numbers, and simple formatting

## Expected OCR Results

### ✅ **Should Work Well**:
- Clean, high-contrast black text on white background
- Standard fonts (Arial, Times, Helvetica)
- Font size 10pt or larger
- Straight, unrotated text
- Simple invoices and forms

### ⚠️ **May Have Issues**:
- Handwritten text (depends on clarity)
- Decorative or unusual fonts
- Small text (under 10pt)
- Low contrast (light gray text)
- Rotated or skewed text

### ❌ **Likely to Fail**:
- Heavily stylized text
- Text on patterned backgrounds
- Extremely poor image quality
- Cursive handwriting
- Text in tables with complex borders

## Testing Strategy

### 1. **Start Simple**:
- Begin with clean, typed documents
- Use high-quality scans or PDFs
- Test basic invoice formats

### 2. **Increase Complexity**:
- Add tables and formatting
- Test mobile phone photos
- Try different document types

### 3. **Edge Cases**:
- Poor quality images
- Rotated documents
- Mixed content types

### 4. **Real-world Documents**:
- Use actual business documents
- Test with customer-provided samples
- Validate against known content

## Demo Mode Testing

The interface includes a demo mode for testing without a backend:

1. Open `index.html?demo=true` in your browser
2. Upload any supported file
3. See simulated OCR results
4. Test all UI functionality

## File Size and Format Limits

- **Maximum file size**: 10MB
- **Supported formats**: PDF, JPG, JPEG, PNG
- **Recommended resolution**: 300 DPI for scanned documents
- **Image quality**: Clear, well-lit, high contrast

## Testing Checklist

### Basic Functionality:
- [ ] File upload works (drag & drop)
- [ ] File validation (type and size)
- [ ] OCR service selection
- [ ] Processing status display
- [ ] Results display correctly
- [ ] Error handling works
- [ ] History tracking functions

### Different Document Types:
- [ ] Simple text documents
- [ ] Business invoices
- [ ] Government forms
- [ ] Mobile phone photos
- [ ] Scanned PDFs
- [ ] Mixed content documents

### OCR Services:
- [ ] Tesseract processing
- [ ] Google Vision (when available)
- [ ] AWS Textract (when available)

### Error Scenarios:
- [ ] Invalid file types
- [ ] Files too large
- [ ] Network errors
- [ ] Processing timeouts
- [ ] Corrupted files

## Performance Expectations

### Processing Times:
- **Small images** (< 1MB): 2-5 seconds
- **Large PDFs** (5-10MB): 10-30 seconds
- **Complex documents**: 15-45 seconds

### Accuracy Expectations:
- **Clean typed text**: 95-99% accuracy
- **Good quality scans**: 90-95% accuracy
- **Mobile photos**: 80-90% accuracy
- **Poor quality**: 60-80% accuracy

## Troubleshooting

### Common Issues:

1. **No text extracted**:
   - Check image quality
   - Ensure text is readable to human eye
   - Try different OCR service

2. **Partial text extraction**:
   - Document may have mixed content
   - Some areas may be too low quality
   - Tables and formatting can cause issues

3. **Incorrect text**:
   - Poor image quality
   - Unusual fonts or formatting
   - Need higher resolution image

### Solutions:
- Improve image quality (lighting, focus, resolution)
- Use PDF instead of image when possible
- Try different OCR services
- Adjust document orientation

## Next Steps

After testing the prototype:

1. Document which document types work best
2. Note performance characteristics
3. Identify common failure cases
4. Gather feedback for improvements
5. Test with real user documents

---

**Note**: This is a testing prototype. Results may vary significantly based on document quality and type.