import json
import os

# Define file paths
hashes_path = r"E:\Windows\Documents\D2 API\Weapons_Hash\WeaponHashes.json"
unique_path = r"E:\Windows\Documents\D2 API\Weapons_Hash\weapon_hashes_unquie.json"
adept_path = r"E:\Windows\Documents\D2 API\Weapons_Hash\Adept_hashes.json"
output_path = r"E:\Windows\Documents\D2 API\Weapons_Hash\weapon_hashes_final.json"

# Load JSON files
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Load base data from WeaponHashes.json
merged_data = load_json(hashes_path)

# Load and add data from weapon_hashes_unquie.json
unique_data = load_json(unique_path)
for category, weapons in unique_data.items():
    if category not in merged_data:
        merged_data[category] = []
    # Append all weapons from unique_data without filtering duplicates
    merged_data[category].extend(weapons)

# Load and add data from Adept_hashes.json
adept_data = load_json(adept_path)
for category, weapons in adept_data.items():
    if category not in merged_data:
        merged_data[category] = []
    # Append all weapons from adept_data without filtering duplicates
    merged_data[category].extend(weapons)

# Write merged data to JSON file
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(merged_data, f, indent=4)