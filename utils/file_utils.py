import json
import os
from typing import List, Dict, Any


class FileUtils:
    @staticmethod
    def load_modes_from_json(file_path: str = "config/modes.json") -> List[str]:
        """Load modes from JSON file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("modes", [])
        except Exception as e:
            raise Exception(f"Error reading JSON: {e}")

    @staticmethod
    def save_to_json(data: Dict[str, Any], file_path: str):
        """Save data to JSON file"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"Error saving to JSON: {e}")

    @staticmethod
    def ensure_directory(directory: str):
        """Ensure directory exists"""
        if not os.path.exists(directory):
            os.makedirs(directory)