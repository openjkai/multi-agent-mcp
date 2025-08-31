"""
PDF Processor - Advanced PDF processing and text extraction
Professional PDF handling for today's major update
"""

import logging
import io
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class PDFPage:
    """Represents a single PDF page"""
    page_number: int
    text: str
    images: List[Dict[str, Any]]
    tables: List[Dict[str, Any]]
    metadata: Dict[str, Any]

@dataclass
class PDFDocument:
    """Represents a complete PDF document"""
    filename: str
    total_pages: int
    pages: List[PDFPage]
    metadata: Dict[str, Any]
    text_content: str
    extracted_tables: List[Dict[str, Any]]
    extracted_images: List[Dict[str, Any]]

class PDFProcessor:
    """Advanced PDF processing with text extraction and analysis"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
        self.max_pages = 1000  # Safety limit
        self.text_cleanup_patterns = [
            (r'\s+', ' '),  # Multiple whitespace to single
            (r'[^\w\s\.\,\;\:\!\?\-\(\)]', ''),  # Remove special chars except basic punctuation
        ]
    
    def can_process(self, filename: str) -> bool:
        """Check if file format is supported"""
        return any(filename.lower().endswith(fmt) for fmt in self.supported_formats)
    
    async def process_pdf(self, file_content: bytes, filename: str) -> PDFDocument:
        """Process PDF content and extract information"""
        try:
            # Try PyPDF2 first (lighter weight)
            try:
                return await self._process_with_pypdf2(file_content, filename)
            except ImportError:
                logger.info("PyPDF2 not available, trying alternative methods")
            
            # Try pdfplumber for better text extraction
            try:
                return await self._process_with_pdfplumber(file_content, filename)
            except ImportError:
                logger.info("pdfplumber not available, using basic extraction")
            
            # Fallback to basic extraction
            return await self._process_basic(file_content, filename)
            
        except Exception as e:
            logger.error(f"Error processing PDF {filename}: {e}")
            raise
    
    async def _process_with_pypdf2(self, file_content: bytes, filename: str) -> PDFDocument:
        """Process PDF using PyPDF2"""
        try:
            import PyPDF2
            
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            pages = []
            all_text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                
                # Clean up text
                cleaned_text = self._clean_text(page_text)
                
                page_obj = PDFPage(
                    page_number=page_num + 1,
                    text=cleaned_text,
                    images=[],
                    tables=[],
                    metadata={"extraction_method": "PyPDF2"}
                )
                pages.append(page_obj)
                all_text += cleaned_text + "\n"
            
            # Extract metadata
            metadata = {}
            if pdf_reader.metadata:
                metadata = {
                    "title": pdf_reader.metadata.get('/Title', ''),
                    "author": pdf_reader.metadata.get('/Author', ''),
                    "subject": pdf_reader.metadata.get('/Subject', ''),
                    "creator": pdf_reader.metadata.get('/Creator', ''),
                    "producer": pdf_reader.metadata.get('/Producer', ''),
                    "creation_date": pdf_reader.metadata.get('/CreationDate', ''),
                    "modification_date": pdf_reader.metadata.get('/ModDate', '')
                }
            
            return PDFDocument(
                filename=filename,
                total_pages=len(pages),
                pages=pages,
                metadata=metadata,
                text_content=all_text,
                extracted_tables=[],
                extracted_images=[]
            )
            
        except Exception as e:
            logger.error(f"PyPDF2 processing failed: {e}")
            raise
    
    async def _process_with_pdfplumber(self, file_content: bytes, filename: str) -> PDFDocument:
        """Process PDF using pdfplumber for better text and table extraction"""
        try:
            import pdfplumber
            
            pdf_file = io.BytesIO(file_content)
            pdf = pdfplumber.open(pdf_file)
            
            pages = []
            all_text = ""
            all_tables = []
            all_images = []
            
            for page_num, page in enumerate(pdf.pages):
                # Extract text
                page_text = page.extract_text() or ""
                cleaned_text = self._clean_text(page_text)
                
                # Extract tables
                tables = page.extract_tables()
                page_tables = []
                for table_num, table in enumerate(tables):
                    if table and any(any(cell for cell in row) for row in table):
                        table_data = {
                            "table_id": f"page_{page_num + 1}_table_{table_num + 1}",
                            "data": table,
                            "page": page_num + 1,
                            "rows": len(table),
                            "columns": len(table[0]) if table else 0
                        }
                        page_tables.append(table_data)
                        all_tables.append(table_data)
                
                # Extract images (basic info)
                images = page.images if hasattr(page, 'images') else []
                page_images = []
                for img_num, img in enumerate(images):
                    img_data = {
                        "image_id": f"page_{page_num + 1}_image_{img_num + 1}",
                        "page": page_num + 1,
                        "width": img.get('width', 0),
                        "height": img.get('height', 0),
                        "type": img.get('type', 'unknown')
                    }
                    page_images.append(img_data)
                    all_images.append(img_data)
                
                page_obj = PDFPage(
                    page_number=page_num + 1,
                    text=cleaned_text,
                    images=page_images,
                    tables=page_tables,
                    metadata={"extraction_method": "pdfplumber"}
                )
                pages.append(page_obj)
                all_text += cleaned_text + "\n"
            
            pdf.close()
            
            return PDFDocument(
                filename=filename,
                total_pages=len(pages),
                pages=pages,
                metadata={},
                text_content=all_text,
                extracted_tables=all_tables,
                extracted_images=all_images
            )
            
        except Exception as e:
            logger.error(f"pdfplumber processing failed: {e}")
            raise
    
    async def _process_basic(self, file_content: bytes, filename: str) -> PDFDocument:
        """Basic PDF processing fallback"""
        # Create a minimal document structure
        page = PDFPage(
            page_number=1,
            text="PDF content could not be extracted. Please ensure the file is not corrupted.",
            images=[],
            tables=[],
            metadata={"extraction_method": "basic_fallback", "error": "Limited extraction"}
        )
        
        return PDFDocument(
            filename=filename,
            total_pages=1,
            pages=[page],
            metadata={"extraction_method": "basic_fallback"},
            text_content=page.text,
            extracted_tables=[],
            extracted_images=[]
        )
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Apply cleanup patterns
        cleaned = text
        for pattern, replacement in self.text_cleanup_patterns:
            cleaned = re.sub(pattern, replacement, cleaned)
        
        # Remove excessive whitespace
        cleaned = ' '.join(cleaned.split())
        
        return cleaned.strip()
    
    def extract_tables_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract table-like structures from text using regex patterns"""
        tables = []
        
        # Look for table patterns (rows separated by | or tabs)
        table_patterns = [
            r'(\|[^|]+\|[^|]*\n)+',  # Markdown-style tables
            r'([^\t\n]+\t[^\t\n]+\n)+',  # Tab-separated tables
        ]
        
        for pattern in table_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                table_text = match.group(0)
                rows = [row.strip() for row in table_text.split('\n') if row.strip()]
                
                if len(rows) > 1:  # At least header + one data row
                    table_data = {
                        "table_id": f"extracted_table_{len(tables) + 1}",
                        "data": [row.split('|') if '|' in row else row.split('\t') for row in rows],
                        "rows": len(rows),
                        "columns": max(len(row.split('|')) if '|' in row else len(row.split('\t')) for row in rows),
                        "extraction_method": "regex_pattern"
                    }
                    tables.append(table_data)
        
        return tables
    
    def analyze_document_structure(self, pdf_doc: PDFDocument) -> Dict[str, Any]:
        """Analyze the structure and content of the PDF document"""
        analysis = {
            "total_pages": pdf_doc.total_pages,
            "total_characters": len(pdf_doc.text_content),
            "total_words": len(pdf_doc.text_content.split()),
            "average_words_per_page": len(pdf_doc.text_content.split()) / pdf_doc.total_pages if pdf_doc.total_pages > 0 else 0,
            "tables_found": len(pdf_doc.extracted_tables),
            "images_found": len(pdf_doc.extracted_images),
            "content_density": len(pdf_doc.text_content) / pdf_doc.total_pages if pdf_doc.total_pages > 0 else 0,
            "structure_analysis": {
                "has_tables": len(pdf_doc.extracted_tables) > 0,
                "has_images": len(pdf_doc.extracted_images) > 0,
                "is_text_heavy": len(pdf_doc.text_content) > 1000,
                "is_structured": len(pdf_doc.extracted_tables) > 0 or len(pdf_doc.extracted_images) > 0
            }
        }
        
        return analysis 