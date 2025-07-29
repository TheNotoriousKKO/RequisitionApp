import csv, json, os, requests, io

CSV_FILE = "items.csv"
META_FILE = "metadata.json"

ALL_CATEGORIES = ["Armor", "Grenade", "Utility", "Other", "Pistol", "Ranged", "Heavy Ranged", "Melee", "Heavy Melee"]
WEAPON_CATEGORIES = ["Pistol", "Ranged", "Melee", "Heavy Ranged", "Heavy Melee"]

def load_items():
    meta = load_metadata()
    csv_url = meta.get("csv_url")
    if csv_url:
        try:
            print("Fetching latest items CSV from Google Drive...")
            r = requests.get(csv_url, timeout=10)
            r.raise_for_status()
            data = r.content.decode("utf-8")
            return list(csv.DictReader(io.StringIO(data)))
        except Exception as e:
            print(f"Could not download cloud CSV, using local file. Error: {e}")

    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def load_metadata():
    if not os.path.exists(META_FILE):
        return {"username": "Player", "personal_items": [], "csv_url": ""}
    with open(META_FILE, encoding='utf-8') as f:
        return json.load(f)

def save_metadata(meta):
    with open(META_FILE, "w", encoding='utf-8') as f:
        json.dump(meta, f, indent=2)

