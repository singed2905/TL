import json
import re
import os
from typing import List, Dict, Any


class MappingManager:
    def __init__(self, mapping_file: str = "config/mapping.json"):
        self.mapping_file = mapping_file
        self.mappings = self._load_mappings()

    def _load_mappings(self) -> List[Dict[str, Any]]:
        """Load mappings from JSON file"""
        if not os.path.exists(self.mapping_file):
            raise FileNotFoundError(f"Mapping file not found: {self.mapping_file}")

        with open(self.mapping_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("mappings", [])

    def encode_string(self, input_string: str) -> str:
        """Encode a string using the mapping rules"""
        input_string = input_string.replace(" ", "")
        if not input_string:
            return ""

        result = input_string
        complex_fraction_pattern = r"\\frac\{((?:\{.*?\}|[^{}])+)\}\{((?:\{.*?\}|[^{}])+)\}"

        def process_complex_fraction(match):
            num = match.group(1)
            den = match.group(2)
            num_processed = self._process_nested_content(num)
            den_processed = self._process_nested_content(den)
            return f"{num_processed}a{den_processed}"

        # Process complex fractions
        changed = True
        max_iterations = 20
        while changed and max_iterations > 0:
            new_result = re.sub(complex_fraction_pattern, process_complex_fraction, result)
            changed = new_result != result
            result = new_result
            max_iterations -= 1

        # Apply other mappings
        for rule in self.mappings:
            find = rule.get("find", "")
            replace = rule.get("replace", "")
            rule_type = rule.get("type", "literal")
            description = rule.get("description", "")

            if "frac" in description:
                continue

            if rule_type == "regex":
                try:
                    result = re.sub(find, replace, result)
                except Exception as e:
                    print(f"Regex error with pattern '{find}': {e}")
                    continue
            else:
                result = result.replace(find, replace)

        return result

    def _process_nested_content(self, content: str) -> str:
        """Process nested content with mappings"""
        result = content
        for rule in self.mappings:
            find = rule.get("find", "")
            replace = rule.get("replace", "")
            rule_type = rule.get("type", "literal")
            description = rule.get("description", "")

            if "frac" in description:
                continue

            if rule_type == "regex":
                try:
                    result = re.sub(find, replace, result)
                except Exception:
                    continue
            else:
                result = result.replace(find, replace)

        return result