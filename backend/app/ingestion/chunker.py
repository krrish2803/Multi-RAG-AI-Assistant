"""Text chunking for document ingestion."""

from typing import Optional


class Chunker:
    """Recursive text chunker with configurable size and overlap."""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str, metadata: dict) -> list[dict]:
        """Split text into chunks with metadata.
        
        Args:
            text: The text to chunk
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of chunk dicts with 'text' and metadata fields
        """
        if not text or len(text.strip()) == 0:
            return []

        # Simple recursive splitting by paragraphs, then sentences
        chunks = self._recursive_split(text)
        
        result = []
        for i, chunk_text in enumerate(chunks):
            chunk_text = chunk_text.strip()
            if chunk_text:
                chunk = {"text": chunk_text, "chunk_index": i}
                chunk.update(metadata)
                result.append(chunk)

        return result

    def _recursive_split(self, text: str) -> list[str]:
        """Recursively split text into chunks."""
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        separators = ["\n\n", "\n", ". ", " ", ""]
        
        for sep in separators:
            if sep == "":
                # Last resort: split by character
                for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
                    chunks.append(text[i:i + self.chunk_size])
                return chunks

            parts = text.split(sep)
            if len(parts) > 1:
                current_chunk = ""
                for part in parts:
                    if len(current_chunk) + len(sep) + len(part) <= self.chunk_size:
                        current_chunk = current_chunk + sep + part if current_chunk else part
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        if len(part) > self.chunk_size:
                            # Recursively split oversized parts
                            chunks.extend(self._recursive_split(part))
                        else:
                            current_chunk = part
                
                if current_chunk:
                    chunks.append(current_chunk)
                break

        return chunks if chunks else [text]
