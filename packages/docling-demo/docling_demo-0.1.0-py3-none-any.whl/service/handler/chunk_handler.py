from docling_core.transforms.chunker import HierarchicalChunker
from typing import List, Dict

class ChunkerHandler:
    """Simple document chunker using Docling"""
    
    def __init__(self, max_tokens: int = 2000):
        self.chunker = HierarchicalChunker(max_tokens=max_tokens,)
    
    def chunk(self, docling_result, doc_id: str) -> List[Dict]:

        chunk_iter = self.chunker.chunk(docling_result.document)
        
        chunks = []
        for i, chunk in enumerate(chunk_iter):
            if len(chunk.text.strip()) < 50:  # Skip too short
                continue
            
            chunks.append({
                'chunk_id': f"{doc_id}_c{i}",
                'content': chunk.text
            })
        
        return chunks 
