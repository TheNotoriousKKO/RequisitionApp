import csv, json, os

CSV_FILE = "items.csv"
META_FILE = "metadata.json"

ALL_CATEGORIES = ["Armor", "Grenade", "Utility", "Other", "Pistol", "Ranged", "Heavy Ranged", "Melee", "Heavy Melee"]
WEAPON_CATEGORIES = ["Pistol", "Ranged", "Melee", "Heavy Ranged", "Heavy Melee"]

def load_items():
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def load_metadata():
    if not os.path.exists(META_FILE):
        return {"username": "Player", "personal_items": []}
    with open(META_FILE, encoding='utf-8') as f:
        return json.load(f)

def save_metadata(meta):
    with open(META_FILE, "w", encoding='utf-8') as f:
        json.dump(meta, f, indent=2)
