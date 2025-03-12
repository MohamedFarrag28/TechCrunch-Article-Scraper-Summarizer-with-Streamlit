import sys
import json
from pathlib import Path
import csv

# Ensure project root is added to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

# Define feedback folder and file paths relative to the root directory
FEEDBACK_DIR = ROOT_DIR / "feedback"  # Path to the feedback folder
FEEDBACK_FILE = FEEDBACK_DIR / "user_feedback.csv"  # Path to the feedback file

# Ensure the feedback folder exists
FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)

def save_feedback(feedback_entry):
    """Save feedback entry to a CSV file efficiently."""
    file_exists = FEEDBACK_FILE.exists()

    with open(FEEDBACK_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write header only if the file is new
        if not file_exists:
            writer.writerow(["Type", "Message", "Input", "Summary"])

        # Write the new feedback entry as a row
        writer.writerow([feedback_entry["type"], feedback_entry["message"], feedback_entry.get("input", "N/A"), feedback_entry.get("summary", "N/A")])

def validate_text_input(text):
    """Validate text input and return an error message if necessary."""
    if not text.strip():
        return "❌ Input cannot be empty!"
    if len(text) < 2:
        return "⚠️ Input is too short! Please provide more details."
    return None  # No errors
