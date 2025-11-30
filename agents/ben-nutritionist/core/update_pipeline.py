"""
Update Pipeline for Ben Nutritionist Agent
Processes new nutrition documents and updates the ChromaDB knowledge base
"""
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
import asyncio
from docx import Document
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NutritionUpdatePipeline:
    """Pipeline for updating nutrition knowledge base"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.chroma_dir = Path("agents/ben-nutritionist/chroma_db")
        self.documents_dir = Path("agents/ben-nutritionist/documents")
        self.processed_files_log = self.documents_dir / "processed_files.txt"
        
        # Ensure directories exist
        self.chroma_dir.mkdir(parents=True, exist_ok=True)
        self.documents_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup ChromaDB with same config as query_chromadb.py
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.chroma_dir),
            settings=chromadb.Settings(
                anonymized_telemetry=False,
                allow_reset=False
            )
        )
        
        # Use the same collection name as the existing setup
        try:
            self.collection = self.chroma_client.get_collection(name="transcripts")
        except:
            # Create collection if it doesn't exist
            self.collection = self.chroma_client.create_collection(name="transcripts")
        
    def get_processed_files(self) -> set:
        """Get list of already processed files"""
        if not self.processed_files_log.exists():
            return set()
        
        with open(self.processed_files_log, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f.readlines())
    
    def mark_file_processed(self, filename: str):
        """Mark a file as processed"""
        with open(self.processed_files_log, 'a', encoding='utf-8') as f:
            f.write(f"{filename}\n")
    
    def extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from Word document"""
        try:
            doc = Document(file_path)
            text = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text.strip())
            
            return "\n".join(text)
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return ""
    
    def extract_text_from_txt(self, file_path: Path) -> str:
        """Extract text from plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to end at a sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                if last_period > chunk_size // 2:  # Don't make chunks too small
                    chunk = chunk[:last_period + 1]
                    end = start + len(chunk)
            
            chunks.append(chunk.strip())
            start = end - overlap
            
        return chunks
    
    def enhance_text_with_ai(self, text: str) -> str:
        """Enhance text with AI to improve nutrition context"""
        try:
            prompt = f"""
            Enhance this nutrition text by adding relevant context and making it more searchable.
            Add nutrition-related keywords and concepts that would help users find this information.
            Keep the original content but make it more comprehensive for nutrition queries.
            
            Original text: {text[:2000]}...
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            
            enhanced = response.choices[0].message.content
            return f"{text}\n\nEnhanced context: {enhanced}"
        except Exception as e:
            logger.warning(f"Failed to enhance text with AI: {e}")
            return text
    
    def process_new_documents(self, limit: int = 10, enhance_with_ai: bool = False) -> Dict:
        """Process new documents and add them to ChromaDB"""
        processed_files = self.get_processed_files()
        new_files = []
        
        # Find new documents
        supported_extensions = ['.docx', '.txt', '.md']
        for ext in supported_extensions:
            for file_path in self.documents_dir.glob(f"*{ext}"):
                if file_path.name not in processed_files:
                    new_files.append(file_path)
        
        # Limit the number of files to process
        new_files = new_files[:limit]
        
        results = {
            "processed_files": 0,
            "new_documents": 0,
            "errors": []
        }
        
        for file_path in new_files:
            try:
                logger.info(f"Processing: {file_path.name}")
                
                # Extract text based on file type
                if file_path.suffix == '.docx':
                    text = self.extract_text_from_docx(file_path)
                elif file_path.suffix in ['.txt', '.md']:
                    text = self.extract_text_from_txt(file_path)
                else:
                    continue
                
                if not text.strip():
                    logger.warning(f"No text extracted from {file_path.name}")
                    continue
                
                # Enhance with AI if requested
                if enhance_with_ai:
                    text = self.enhance_text_with_ai(text)
                
                # Chunk the text
                chunks = self.chunk_text(text)
                
                # Add chunks to ChromaDB with embeddings
                for i, chunk in enumerate(chunks):
                    document_id = f"{file_path.stem}_chunk_{i}"
                    
                    # Generate embedding for the chunk
                    try:
                        embedding_response = self.openai_client.embeddings.create(
                            model="text-embedding-3-large",
                            input=chunk
                        )
                        embedding = embedding_response.data[0].embedding
                        
                        self.collection.add(
                            documents=[chunk],
                            embeddings=[embedding],
                            metadatas=[{
                                "source": file_path.name,
                                "chunk_index": i,
                                "total_chunks": len(chunks),
                                "file_type": file_path.suffix,
                                "enhanced": enhance_with_ai
                            }],
                            ids=[document_id]
                        )
                    except Exception as e:
                        logger.error(f"Failed to add chunk {document_id}: {e}")
                        continue
                
                # Mark file as processed
                self.mark_file_processed(file_path.name)
                results["processed_files"] += 1
                results["new_documents"] += len(chunks)
                
                logger.info(f"Successfully processed {file_path.name} - {len(chunks)} chunks added")
                
            except Exception as e:
                error_msg = f"Error processing {file_path.name}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        # Persist changes
        try:
            # ChromaDB automatically persists changes in newer versions
            logger.info("ChromaDB changes persisted")
        except Exception as e:
            logger.warning(f"Failed to persist ChromaDB: {e}")
        
        logger.info(f"Update complete: {results['processed_files']} files, {results['new_documents']} new documents")
        return results
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the current collection"""
        try:
            count = self.collection.count()
            
            # Get sample metadata to understand the collection
            if count > 0:
                sample = self.collection.peek(limit=5)
                sources = set()
                file_types = set()
                
                for metadata in sample.get('metadatas', []):
                    if metadata:
                        sources.add(metadata.get('source', 'unknown'))
                        file_types.add(metadata.get('file_type', 'unknown'))
                
                return {
                    "total_documents": count,
                    "sample_sources": list(sources),
                    "file_types": list(file_types),
                    "collection_name": self.collection.name
                }
            else:
                return {
                    "total_documents": 0,
                    "sample_sources": [],
                    "file_types": [],
                    "collection_name": self.collection.name
                }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}

# Main pipeline function for use in the API
async def run_update_pipeline(limit: int = 10, enhance_with_ai: bool = False) -> Dict:
    """
    Run the nutrition document update pipeline
    
    Args:
        limit: Maximum number of new files to process
        enhance_with_ai: Whether to enhance documents with AI
        
    Returns:
        Dict with processing results
    """
    try:
        pipeline = NutritionUpdatePipeline()
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            pipeline.process_new_documents, 
            limit, 
            enhance_with_ai
        )
        
        # Add collection stats to result
        stats = pipeline.get_collection_stats()
        result["collection_stats"] = stats
        
        return result
    
    except Exception as e:
        logger.error(f"Update pipeline failed: {e}")
        return {
            "processed_files": 0,
            "new_documents": 0,
            "errors": [str(e)],
            "status": "failed"
        }

# CLI function for manual updates
def main():
    """Command line interface for manual updates"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Update Ben Nutritionist knowledge base")
    parser.add_argument("--limit", type=int, default=10, help="Max files to process")
    parser.add_argument("--enhance", action="store_true", help="Enhance documents with AI")
    parser.add_argument("--stats", action="store_true", help="Show collection statistics")
    
    args = parser.parse_args()
    
    pipeline = NutritionUpdatePipeline()
    
    if args.stats:
        stats = pipeline.get_collection_stats()
        print("Collection Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    else:
        result = pipeline.process_new_documents(args.limit, args.enhance)
        print("Update Results:")
        for key, value in result.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    main()