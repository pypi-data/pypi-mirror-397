import fitz
from pathlib import Path
from typing import List, Dict

class PDFAnalyzer:

    def __init__(self):
        pass

    def analyze(self, pdf_path: str) -> Dict:
        """Comprehensive Report"""        
        # 1. Basic info
        basic_info = self._get_basic_info(pdf_path)
        
        # 2. Analyze pages
        pages_analysis = self._analyze_pages(pdf_path)
        
        # 3. Detect document type
        doc_type = self._detect_document_type(pages_analysis)
        
        # 4. Create summary
        summary = self._create_summary(pages_analysis)
        
        # 5. Recommend strategy
        recommendation = self._recommend_strategy(doc_type, summary)
        
        # ADD THIS RETURN STATEMENT:
        return {
            'file_path': str(pdf_path),
            'basic_info': basic_info,
            'document_type': doc_type,
            'summary': summary,
            'recommendation': recommendation,
            'pages': pages_analysis
        }

    def _get_basic_info(self, pdf_path: Path) -> Dict:
        """Get basic PDF metadata"""
        try:
            doc = fitz.open(pdf_path)
            
            info = {
                'file_name': pdf_path.name,
                'file_size_mb': round(pdf_path.stat().st_size / (1024 * 1024), 2),
                'total_pages': len(doc),
                'pdf_version': doc.metadata.get('format', 'Unknown'),
                'is_encrypted': doc.is_encrypted
            }
            
            doc.close()
            return info
            
        except Exception as e:
            return {
                'error': str(e),
                'file_name': pdf_path.name,
                'total_pages': 0
            }
        
    def _analyze_pages(self, pdf_path: Path) -> List[Dict]:
        """Analyze each page in PDF"""
        doc = fitz.open(filename=pdf_path)
        pages_analysis = []

        for page_num in range(len(doc)):
            page = doc[page_num]

            # Exctract Text
            text = page.get_text()
            text_length = len(text.strip())

            # Check for images
            images = page.get_images()
            image_count = len(images)

            # Determine page type
            has_text = text_length > 50
            has_images = image_count > 0

            if has_text and not has_images:
                page_type = "text"
            elif has_images and not has_text:
                page_type = "scanned"
            elif has_images and has_text:
                page_type = "mixed"
            else:
                page_type = "empty"
        
            pages_analysis.append({
                'page_num': page_num + 1,
                'type': page_type,
                'text_length': text_length,
                'has_text': has_text,
                'has_images': has_images,
                'image_count': image_count,
            })
        
        doc.close()
        return pages_analysis

    def _detect_document_type(self, pages_analysis: List[Dict]) -> str:
        """
        Detect document type based on page characteristics
        Returns: 'ppt', 'document', 'scan', or 'mixed'
        """
        if not pages_analysis:
            return 'unknown'
        
        total_pages = len(pages_analysis)
        
        # Calculate statistics
        avg_text_length = sum(p['text_length'] for p in pages_analysis) / total_pages
        scanned_pages = sum(1 for p in pages_analysis if p['type'] == 'scanned')
        text_pages = sum(1 for p in pages_analysis if p['type'] == 'text')
        mixed_pages = sum(1 for p in pages_analysis if p['type'] == 'mixed')
        
        scanned_ratio = scanned_pages / total_pages
        text_ratio = text_pages / total_pages
        
        # Decision logic
        if scanned_ratio > 0.8:
            # Mostly scanned
            return 'scan'
        
        elif avg_text_length < 500 and mixed_pages > total_pages * 0.3:
            # Short pages with images = likely PPT
            return 'ppt'
        
        elif text_ratio > 0.7:
            # Mostly text = document
            return 'document'
        
        else:
            # Mix of everything
            return 'mixed'        

    def _create_summary(self, pages_analysis: List[Dict]) -> Dict:
        """Create summary statistics from page analysis"""
        total_pages = len(pages_analysis)
        
        if total_pages == 0:
            return {}
        
        text_pages = sum(1 for p in pages_analysis if p['type'] == 'text')
        scanned_pages = sum(1 for p in pages_analysis if p['type'] == 'scanned')
        mixed_pages = sum(1 for p in pages_analysis if p['type'] == 'mixed')
        empty_pages = sum(1 for p in pages_analysis if p['type'] == 'empty')
        
        total_chars = sum(p['text_length'] for p in pages_analysis)
        avg_chars = total_chars // total_pages if total_pages > 0 else 0
        
        return {
            'total_pages': total_pages,
            'text_pages': text_pages,
            'scanned_pages': scanned_pages,
            'mixed_pages': mixed_pages,
            'empty_pages': empty_pages,
            'total_chars': total_chars,
            'avg_chars_per_page': avg_chars
        }

    def _recommend_strategy(self, doc_type: str, summary: Dict) -> Dict:
        """Recommend processing and chunking strategy"""
        
        scanned_ratio = summary.get('scanned_pages', 0) / summary.get('total_pages', 1)
        
        # Processing strategy
        if scanned_ratio > 0.1:
            processing = 'ocr_with_vlm'
        else:
            processing = 'text_extraction'
        
        # Chunking strategy
        if doc_type == 'ppt':
            chunking = 'page'
        else:
            chunking = 'fixed'
        
        return {
            'processing_strategy': processing,
            'chunking_strategy': chunking,
            'estimated_time_sec': summary.get('total_pages', 0) * 2,  # Rough estimate
        }
