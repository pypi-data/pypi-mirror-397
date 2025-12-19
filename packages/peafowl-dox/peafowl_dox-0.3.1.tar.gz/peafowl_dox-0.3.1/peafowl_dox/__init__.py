"""Peafowl Dox - Document processing utilities."""

from .core.image_utils import multipart_to_array, resize_image, preprocess_image
from .core.pdf_converter import pdf_to_images
from .core.document_processor import DocumentProcessor
from .exceptions import PeafowlDoxError, ImageProcessingError, PDFConversionError, OneDriveIntegrationError
from .core.onedrive_provider import OneDriveProvider

__version__ = "0.3.1"
__all__ = [
    "multipart_to_array",
    "resize_image", 
    "preprocess_image",
    "pdf_to_images",
    "DocumentProcessor",
    "PeafowlDoxError",
    "ImageProcessingError", 
    "PDFConversionError",
    "OneDriveIntegrationError",
    "OneDriveProvider"
]
