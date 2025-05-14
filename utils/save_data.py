# utils/save_data.py
import json
import os

def save_to_json(data, filename):
    os.makedirs("data", exist_ok=True)
    with open(f"data/{filename}", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
