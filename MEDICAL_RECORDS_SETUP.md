# Medical Records OCR Setup

## Tesseract OCR Installation

The medical records feature requires Tesseract OCR to be installed on your system.

### Windows Installation

1. **Download Tesseract:**
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download the latest installer (e.g., `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)

2. **Install Tesseract:**
   - Run the installer
   - **Important:** During installation, note the installation path (default: `C:\Program Files\Tesseract-OCR`)
   - Make sure to check "Add to PATH" option if available

3. **Configure Python to find Tesseract:**
   
   Open `cancer_treatment_system/settings.py` and add:
   ```python
   # Tesseract OCR Configuration
   TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

4. **Update views.py:**
   
   In `authentication/views.py`, add this line at the top of the `process_ocr()` function:
   ```python
   import pytesseract
   from django.conf import settings
   
   def process_ocr(record_id):
       pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
       # ... rest of the function
   ```

### Linux Installation

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install tesseract-ocr

# Fedora/RHEL
sudo dnf install tesseract
```

### macOS Installation

```bash
brew install tesseract
```

## Verification

Test if Tesseract is installed correctly:

```bash
tesseract --version
```

You should see output like:
```
tesseract 5.3.3
 leptonica-1.83.1
```

## Additional Language Support

By default, Tesseract includes English. For other languages:

**Windows:**
- Download language data files from: https://github.com/tesseract-ocr/tessdata
- Place `.traineddata` files in: `C:\Program Files\Tesseract-OCR\tessdata\`

**Linux/macOS:**
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr-[lang]

# Example for Hindi
sudo apt-get install tesseract-ocr-hin
```

## Python Dependencies

Already installed via requirements.txt:
- pytesseract==0.3.13
- pdf2image==1.17.0
- PyPDF2==3.0.1
- Pillow (included)

## Poppler (Required for PDF processing)

### Windows:
1. Download from: https://github.com/oschwartz10612/poppler-windows/releases
2. Extract to `C:\Program Files\poppler`
3. Add to PATH or configure in settings:
   ```python
   POPPLER_PATH = r'C:\Program Files\poppler\Library\bin'
   ```
4. Update views.py:
   ```python
   from pdf2image import convert_from_path
   images = convert_from_path(pdf_path, poppler_path=settings.POPPLER_PATH)
   ```

### Linux:
```bash
sudo apt-get install poppler-utils
```

### macOS:
```bash
brew install poppler
```

## Troubleshooting

### Error: "tesseract is not installed or not in your PATH"
- Verify Tesseract installation
- Check PATH environment variable
- Set `pytesseract.pytesseract.tesseract_cmd` explicitly

### Error: "Unable to get page count. Is poppler installed?"
- Install Poppler (see above)
- Configure POPPLER_PATH in settings.py

### Low OCR Accuracy
- Ensure document images are high quality (300+ DPI recommended)
- Check document language matches Tesseract language data
- Pre-process images (deskew, denoise) for better results

## Features

✅ **Automated OCR**: Extracts text from PDF and image files
✅ **Intelligent Data Extraction**: Uses regex patterns to extract:
   - Patient name, age, gender
   - Report date
   - Hospital and doctor names
   - Test results (key-value pairs)
✅ **Background Processing**: OCR runs in daemon thread to avoid blocking
✅ **Status Tracking**: Monitor processing status (processing/completed/failed)
✅ **Confidence Scoring**: OCR confidence percentage
✅ **Multiple Formats**: Supports PDF, JPG, JPEG, PNG

## Usage

1. Navigate to Patient Dashboard
2. Click "Upload Medical Records" or "View Medical Records"
3. Upload a medical report (PDF or image)
4. Wait for OCR processing (usually 5-30 seconds)
5. View extracted information on the detail page

## File Structure

```
authentication/
├── models.py           # MedicalRecord model
├── forms.py            # MedicalRecordForm with validation
├── views.py            # OCR processing logic
├── urls.py             # Medical records routes
└── templates/
    └── authentication/
        ├── medical_records_list.html
        ├── upload_medical_record.html
        └── medical_record_detail.html
```

## Next Steps

- [ ] Install Tesseract OCR (see above)
- [ ] Install Poppler (for PDF support)
- [ ] Configure paths in settings.py
- [ ] Test with sample medical reports
- [ ] Optimize regex patterns for your report formats
- [ ] Add record deletion functionality
- [ ] Implement record editing
