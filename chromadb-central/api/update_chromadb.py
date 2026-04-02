"""
Update ChromaDB Pipeline
========================
Downloads all files from Google Drive to the project's documents folder,
then uses the general index_chromadb module to rebuild the ChromaDB
collection from all supported file types (PDF, DOCX, TXT, JSON).

Usage (called from the /update route or directly):
    from api.update_chromadb import run_update_pipeline
    run_update_pipeline(project_name="nutria", folder_id="...")
"""

import os
from pathlib import Path
from tqdm import tqdm

from api.update_gdrive import (
    authenticate_gdrive,
    list_files_in_folder,
    download_file,
    get_agent_paths,
    gdrive_authenticated,
)
from api.index_chromadb import index_project
from api.query_chromadb import reload_project_collections

PROJECT_ROOT = Path(__file__).parent.parent


def download_all_files(folder_id, documents_dir, limit=None):
    """Download all supported files from a Google Drive folder.

    Returns a list of dicts with file metadata and local path.
    """
    files = list_files_in_folder(folder_id, limit)
    if not files:
        print("⚠️  No documents found in Google Drive folder")
        return []

    downloaded = []
    for file_info in tqdm(files, desc="Downloading files"):
        local_path = download_file(
            file_info["id"],
            file_info["name"],
            file_info["mimeType"],
            documents_dir,
        )
        if local_path:
            downloaded.append({**file_info, "local_path": local_path})
        else:
            print(f"⚠️  Skipped (download failed): {file_info['name']}")

    print(f"📥 Downloaded {len(downloaded)}/{len(files)} files")
    return downloaded


def run_update_pipeline(project_name, collection_name, folder_id, limit=None):
    """Full pipeline: download from GDrive → index with general indexer.

    Args:
        project_name: Knowledge base identifier (e.g. "nutria", "bibliosense").
        collection_name: ChromaDB collection name.
        folder_id: Google Drive folder ID containing source documents.
        limit: Max number of files to download (None = all).

    Returns:
        dict with status information.
    """
    if not gdrive_authenticated:
        print("❌ Google Drive not authenticated, attempting auth...")
        if not authenticate_gdrive():
            return {"error": "Google Drive authentication failed", "authenticated": False}

    paths = get_agent_paths(project_name)
    kb_path = paths["kb_path"]
    documents_dir = paths["documents_dir"]

    os.makedirs(documents_dir, exist_ok=True)

    print(f"📦 Starting update pipeline for: {project_name}")
    print(f"   KB path: {kb_path}")
    print(f"   Folder ID: {folder_id}")

    # Step 1: Download all files from GDrive
    downloaded = download_all_files(folder_id, documents_dir, limit)
    if not downloaded:
        return {"error": "No files downloaded", "authenticated": True, "downloaded": 0}

    # Step 2: Index with the general indexer
    result = index_project(project_name, collection_name)

    # Step 3: Reload preloaded collection cache so queries use the new data
    reload_project_collections(project_name, collection_name)

    return {
        "authenticated": True,
        "downloaded": len(downloaded),
        "indexed": result.get("indexed", False),
        "documents": result.get("documents", 0),
    }
