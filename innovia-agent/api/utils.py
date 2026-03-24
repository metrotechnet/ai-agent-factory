"""
utils.py
Utility functions and constants for API routes in the Bibliosense agent project.
"""

from pathlib import Path

# Root directory of the project
PROJECT_ROOT = Path(__file__).parent.parent
# Path to the question log JSON file
QUESTION_LOG_PATH = PROJECT_ROOT / "question_log.json"
