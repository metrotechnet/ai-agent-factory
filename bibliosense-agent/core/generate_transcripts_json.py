"""
Generate transcripts_chromadb.json from transcripts and documents

This script reads all .txt files from knowledge-base/agent/transcripts/
and .json files from knowledge-base/agent/documents/ and creates a single
transcripts_chromadb.json file that can be indexed to ChromaDB.

Usage:
    python generate_transcripts_json.py <path_to_knowledge_base_agent>
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime
from tqdm import tqdm


def generate_transcripts_json(agent_dir: Path):
    """Create transcripts_chromadb.json file from transcripts and JSON documents"""
    print(f"📝 Generating transcripts_chromadb.json...")
    
    transcripts_dir = agent_dir / "transcripts"
    documents_dir = agent_dir / "documents"
    output_path = agent_dir / "transcripts_chromadb.json"
    
    # Get agent ID from agent_config.json
    config_path = agent_dir / "agent_config.json"
    agent_id = "agent"
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                agent_id = config.get("agent_id", "agent")
        except Exception as e:
            print(f"⚠️  Could not read agent_id from agent_config.json: {e}")
    
    documents = []
    doc_counter = 0
    
    # Process transcript files (.txt)
    if transcripts_dir.exists():
        transcript_files = list(transcripts_dir.glob("*.txt"))
        if transcript_files:
            print(f"📄 Processing {len(transcript_files)} transcript files...")
            
            for file_path in tqdm(transcript_files, desc="Processing transcripts"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    
                    if not text.strip():
                        continue
                    
                    # Create document ID and metadata
                    doc_id = f"doc_{doc_counter:04d}_{file_path.stem}"
                    doc_counter += 1
                    
                    # Basic metadata
                    metadata = {
                        "source": file_path.name,
                        "reference": file_path.stem,
                        "type": "transcript"
                    }
                    
                    # Try to extract date from filename if present (DDMMYY format)
                    date_match = re.search(r'(\d{2})(\d{2})(\d{2})', file_path.stem)
                    if date_match:
                        day, month, year = date_match.groups()
                        metadata["date"] = f"20{year}-{month}-{day}"
                    
                    # Add to documents array
                    documents.append({
                        "id": doc_id,
                        "text": text,
                        "metadata": metadata
                    })
                    
                except Exception as e:
                    print(f"⚠️  Error processing {file_path.name}: {e}")
                    continue
    
    # Process JSON files (each entry becomes a separate document)
    if documents_dir.exists():
        json_files = list(documents_dir.glob("*.json"))
        if json_files:
            print(f"📚 Processing {len(json_files)} JSON files...")
            print(f"🐛 DEBUG MODE: Processing only first 50 entries per JSON file")
            
            max_entries_per_file = -1  # DEBUG: Limit to 50 entries per JSON file
            
            for json_file in tqdm(json_files, desc="Processing JSON files"):
                file_entry_count = 0  # Reset counter for each file
                    
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                    
                    # Handle both array and single object
                    if isinstance(json_data, list):
                        entries = json_data
                    elif isinstance(json_data, dict):
                        entries = [json_data]
                    else:
                        print(f"⚠️  Unsupported JSON structure in {json_file.name}")
                        continue
                    
                    # Create a document for each entry
                    for entry in entries:
                        if file_entry_count >= max_entries_per_file and max_entries_per_file > 0:
                            print(f"  ✋ {json_file.name}: Stopped at {max_entries_per_file} entries")
                            break
                            
                        if not isinstance(entry, dict):
                            continue
                        
                        file_entry_count += 1
                        
                        # Generate readable text from the entry
                        text_parts = []
                        
                        # Use entry's own ID if available, otherwise generate one
                        entry_id = entry.get("id", f"entry_{doc_counter}")
                        
                        # Build readable text from key fields
                        if "titre" in entry or "title" in entry:
                            title = entry.get("titre") or entry.get("title")
                            text_parts.append(f"Titre: {title}")
                        
                        if "label" in entry:
                            text_parts.append(f"Label: {entry['label']}")
                        
                        if "auteur" in entry or "author" in entry:
                            author = entry.get("auteur") or entry.get("author")
                            text_parts.append(f"Auteur: {author}")
                        
                        if "resume" in entry or "summary" in entry:
                            resume = entry.get("resume") or entry.get("summary")
                            if resume:
                                text_parts.append(f"\nRésumé: {resume}")
                        
                        if "description" in entry:
                            text_parts.append(f"\nDescription: {entry['description']}")
                        
                        if "categorie" in entry or "category" in entry:
                            cat = entry.get("categorie") or entry.get("category")
                            text_parts.append(f"\nCatégorie: {cat}")
                        
                        if "editeur" in entry or "publisher" in entry:
                            editeur = entry.get("editeur") or entry.get("publisher")
                            if editeur:
                                text_parts.append(f"Éditeur: {editeur}")
                        
                        if "parution" in entry:
                            text_parts.append(f"Parution: {entry['parution']}")
                        
                        if "pages" in entry:
                            text_parts.append(f"Pages: {entry['pages']}")
                        
                        if "langue" in entry or "language" in entry:
                            langue = entry.get("langue") or entry.get("language")
                            if langue:
                                text_parts.append(f"Langue: {langue}")
                        
                        # Combine all parts
                        text = "\n".join(text_parts)
                        
                        if not text.strip():
                            # Fallback: convert entire entry to text
                            text = "\n".join([f"{k}: {v}" for k, v in entry.items() if v and k != "classification"])
                        
                        # Create document ID
                        doc_id = f"doc_{doc_counter:04d}_{entry_id}"
                        doc_counter += 1
                        
                        # Build metadata from ALL entry fields
                        metadata = {
                            "source": json_file.name,
                            "type": entry.get("type", "json_entry"),
                            "entry_id": entry_id
                        }
                        
                        # Extract bibliotheque from filename (e.g., book_dbase_montreal.json -> montreal)
                        if "montreal" in json_file.name.lower():
                            metadata["bibliotheque"] = "montreal"
                        elif "quebec" in json_file.name.lower() or "québec" in json_file.name.lower():
                            metadata["bibliotheque"] = "quebec"
                        elif "bibliotheque" in entry:
                            metadata["bibliotheque"] = entry["bibliotheque"]
                        
                        # Add ALL fields from entry to metadata
                        for key, value in entry.items():
                            if value is not None and value != "" and key not in metadata:
                                # Convert value to string if it's a list or dict
                                if isinstance(value, (list, dict)):
                                    metadata[key] = json.dumps(value, ensure_ascii=False)
                                else:
                                    metadata[key] = str(value)
                        
                        # Add to documents array
                        documents.append({
                            "id": doc_id,
                            "text": text,
                            "metadata": metadata
                        })
                    
                except Exception as e:
                    print(f"⚠️  Error processing {json_file.name}: {e}")
                    continue
    
    if not documents:
        print("⚠️  No documents to process")
        print("   Please add .txt files to knowledge-base/agent/transcripts/")
        print("   or .json files to knowledge-base/agent/documents/")
        return False
    
    # Create the complete structure
    transcripts_data = {
        "knowledge_base": agent_id,
        "format": "chromadb",
        "total_documents": len(documents),
        "extracted_at": datetime.now().isoformat(),
        "documents": documents
    }
    
    # Save to file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(transcripts_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Created transcripts_chromadb.json with {len(documents)} documents")
        print(f"   Saved to: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving transcripts_chromadb.json: {e}")
        return False


def main():
    if len(sys.argv) != 2:
        print("Usage: python generate_transcripts_json.py <path_to_knowledge_base_agent>")
        sys.exit(1)
    
    agent_dir = Path(sys.argv[1])
    
    if not agent_dir.exists():
        print(f"❌ Directory not found: {agent_dir}")
        sys.exit(1)
    
    success = generate_transcripts_json(agent_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
