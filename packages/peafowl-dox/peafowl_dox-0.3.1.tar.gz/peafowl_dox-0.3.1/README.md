# Peafowl Dox

![Peafowl Dox Logo](https://i.postimg.cc/YqtjKKSq/peafowl-dox-logo.png)

A utility library for image and document processing. Essential tools for handling multipart uploads, PDF conversion, and preparing documents for OCR and ML pipelines.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- API Reference
        - [Image Upload Processing](#image-upload-processing)
        - [PDF Conversion](#pdf-conversion)
        - [Image Resizing](#image-resizing)
        - [Image Preprocessing](#image-preprocessing)
        - [Document Processor Class](#document-processor-class)
        - [OneDrive & SharePoint Integration](#onedrive--sharepoint-integration)
- [Error Handling](#error-handling)
- [Dependencies](#dependencies)
- [Changelog](#changelog)

---

## Installation

```bash
pip install peafowl-dox
```

**Note:** Package name uses hyphens for pip, but imports use underscores:

```python
import peafowl_dox  # underscore in import!
```

---

## Quick Start

```python
from fastapi import UploadFile
from peafowl_dox import multipart_to_array

@app.post("/upload/")
async def upload_image(file: UploadFile):
                image_array = multipart_to_array(file.file)
                print(f"Image shape: {image_array.shape}")
                return {"message": "Image processed successfully"}
```

---

## API Reference

### Image Upload Processing

Convert multipart file uploads to numpy arrays.

```python
from peafowl_dox import multipart_to_array

array = multipart_to_array(file.file)
```

**Returns:** `np.ndarray` with shape `(height, width, channels)`

---

### PDF Conversion

Convert PDF pages to image arrays.

```python
from peafowl_dox import pdf_to_images

images = pdf_to_images("document.pdf", dpi=150)
```

---

### Image Resizing

Resize images with aspect ratio preservation.

```python
from peafowl_dox import resize_image
resized = resize_image(image, 1024)
```

---

### Image Preprocessing

```python
from peafowl_dox import preprocess_image
ocr_ready = preprocess_image(image)
```

---

### Document Processor Class

```python
from peafowl_dox import DocumentProcessor
processor = DocumentProcessor()
image = processor.process_image("image.jpg")
```

---

### OneDrive & SharePoint Integration

Manage files in Microsoft OneDrive and SharePoint using Microsoft Graph API.

```python
from peafowl_dox import OneDriveClient

client = OneDriveClient(
                client_id="AZURE_CLIENT_ID",
                client_secret="AZURE_CLIENT_SECRET",
                tenant_id="AZURE_TENANT_ID",
                target_resource_id="SHAREPOINT_SITE_ID_OR_USER_EMAIL",
                is_sharepoint=True
)
```

Supported features:

- Upload files (auto-create folders)
- Download files or folders (recursive)
- List contents
- Delete files
- Safe or recursive folder deletion

---

## Error Handling

```python
from peafowl_dox import (
                PeafowlDoxError,
                ImageProcessingError,
                PDFConversionError,
                OneDriveIntegrationError
)
```

---

## Dependencies

- Python >= 3.8
- numpy >= 2.2.6
- Pillow >= 11.1.0
- opencv-python >= 4.8.0
- PyMuPDF >= 1.23.0
- O365 >= 2.0.35

---

## Changelog

### [0.3.0] - 2025-12-17

- Added OneDriveClient for Microsoft Graph API integration
- Added OneDriveIntegrationError to exception handling

### [0.2.0] - 2025-11-06

- Renamed `prepare_for_ocr` to `preprocess_image`
- Renamed `ImageProcessor` to `DocumentProcessor`

### [0.1.0] - 2025-11-06

- Initial release
