"""
Dataset Editor API Routes

CRUD endpoints for managing project datasets (JSON files in knowledge-base/{project}/documents/).
"""
import json
import os
import shutil
from pathlib import Path
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/datasets", tags=["datasets"])

KB_ROOT = Path(__file__).parent.parent.parent / "knowledge-base"


def _project_dir(project_name: str) -> Path:
    """Return the documents directory for a project, validating the name."""
    # Prevent path traversal
    safe = Path(project_name)
    if safe.anchor or ".." in safe.parts:
        raise HTTPException(400, "Invalid project name")
    return KB_ROOT / project_name / "documents"


def _read_json(path: Path) -> list:
    """Read a JSON dataset file. Returns a list of records."""
    with open(path, "r", encoding="utf-8") as f:
        content = json.load(f)
    if isinstance(content, list):
        return content
    if isinstance(content, dict):
        # Support {data: [...]} or {documents: [...]} wrappers
        for key in ("data", "documents", "items", "records"):
            if key in content and isinstance(content[key], list):
                return content[key]
        # Single object → wrap
        return [content]
    return []


def _write_json(path: Path, records: list):
    """Write records back as a JSON array."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


# =====================================================
# List all projects and their dataset files
# =====================================================
@router.get("")
def list_projects():
    """List all projects and their dataset files with record counts."""
    projects = []
    if not KB_ROOT.exists():
        return {"projects": projects}

    for proj_dir in sorted(KB_ROOT.iterdir()):
        if not proj_dir.is_dir():
            continue
        docs_dir = proj_dir / "documents"
        files = []
        if docs_dir.exists():
            for fpath in sorted(docs_dir.glob("*.json")):
                try:
                    records = _read_json(fpath)
                    files.append({"name": fpath.name, "records": len(records)})
                except Exception:
                    files.append({"name": fpath.name, "records": -1})
        projects.append({"name": proj_dir.name, "files": files})

    return {"projects": projects}


# =====================================================
# Create a new project
# =====================================================
@router.post("/{project_name}")
def create_project(project_name: str):
    """Create a new project directory structure."""
    docs_dir = _project_dir(project_name)
    if docs_dir.exists():
        raise HTTPException(409, f"Project '{project_name}' already exists")
    docs_dir.mkdir(parents=True, exist_ok=True)
    # Also create standard sub-directories
    (KB_ROOT / project_name / "chroma_db").mkdir(exist_ok=True)
    (KB_ROOT / project_name / "extracted_texts").mkdir(exist_ok=True)
    return {"status": "created", "project": project_name}


# =====================================================
# Delete a project
# =====================================================
@router.delete("/{project_name}")
def delete_project(project_name: str):
    """Delete a project and all its contents."""
    proj_path = KB_ROOT / project_name
    safe = Path(project_name)
    if safe.anchor or ".." in safe.parts:
        raise HTTPException(400, "Invalid project name")
    if not proj_path.exists():
        raise HTTPException(404, f"Project '{project_name}' not found")
    shutil.rmtree(proj_path)
    return {"status": "deleted", "project": project_name}


# =====================================================
# Get a dataset file
# =====================================================
@router.get("/{project_name}/{filename}")
def get_dataset(project_name: str, filename: str):
    """Return dataset records and inferred columns."""
    docs_dir = _project_dir(project_name)
    fpath = docs_dir / filename
    if not fpath.exists():
        raise HTTPException(404, f"File '{filename}' not found in project '{project_name}'")

    records = _read_json(fpath)

    # Infer columns from all records
    col_set = dict()  # preserve order
    for rec in records:
        if isinstance(rec, dict):
            for k in rec:
                col_set[k] = True
    columns = list(col_set.keys())

    return {"project": project_name, "file": filename, "columns": columns, "data": records}


# =====================================================
# Save (create or update) a dataset file
# =====================================================
@router.put("/{project_name}/{filename}")
def save_dataset(project_name: str, filename: str, records: list = Body(...)):
    """Save records to a dataset file."""
    if not filename.endswith(".json"):
        raise HTTPException(400, "Filename must end with .json")
    docs_dir = _project_dir(project_name)
    docs_dir.mkdir(parents=True, exist_ok=True)
    fpath = docs_dir / filename
    _write_json(fpath, records)
    return {"status": "saved", "project": project_name, "file": filename, "records": len(records)}


# =====================================================
# Re-index a project into ChromaDB
# =====================================================
@router.post("/{project_name}/reindex")
def reindex_project(project_name: str):
    """Re-index a project's documents into ChromaDB."""
    try:
        from api.index_chromadb import index_project
        from api.query_chromadb import reload_project_collections

        result = index_project(project_name, collection_name="gdrive_documents")
        reload_project_collections(project_name)

        return {
            "status": "success",
            "project": project_name,
            "indexed": result.get("total_documents", 0) if isinstance(result, dict) else True,
        }
    except Exception as e:
        raise HTTPException(500, f"Re-index failed: {str(e)}")
