#!/bin/bash
set -e

echo "Starting application initialization..."

# Initialize ChromaDB (create collection if it doesn't exist)
echo "Initializing ChromaDB..."
python init_chromadb.py

# Check if collection is empty and index if needed
echo "Checking if indexing is needed..."
NEEDS_INDEXING=$(python -c "
from query_chromadb import get_collection
try:
    collection = get_collection()
    count = collection.count()
    print(f'Collection has {count} documents')
    if count == 0:
        print('EMPTY')
    else:
        print('OK')
except Exception as e:
    print(f'Error: {e}')
    print('EMPTY')
" | tail -1)

if [ "$NEEDS_INDEXING" = "EMPTY" ]; then
    echo "Collection is empty. Running indexing..."
    if [ -d "/app/transcripts_extracted" ] && [ "$(ls -A /app/transcripts_extracted)" ]; then
        echo "Found documents in transcripts_extracted. Indexing..."
        python index_chromadb.py
        echo "Indexing complete!"
    else
        echo "Warning: No documents found in transcripts_extracted. Collection will remain empty."
    fi
else
    echo "Collection already has documents. Skipping indexing."
fi

# Start the application
echo "Starting uvicorn server..."
exec uvicorn app:app --host 0.0.0.0 --port ${PORT}
