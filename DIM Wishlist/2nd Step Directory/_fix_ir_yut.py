import json
import os

def correct_weapon_names():
    # Define relative paths
    script_dir = os.path.dirname(__file__)
    input_files = [
        os.path.join(script_dir, 'DestinyCollectibleDefinition.json'),
        os.path.join(script_dir, 'DestinyInventoryItemDefinition.json')
    ]

    # Define name corrections
    name_corrections = {
        "Song of Ir Yût": "Song of Ir Yut",
        "Song of Ir Yût (Adept)": "Song of Ir Yut (Adept)",
        "Fang of Ir Yût": "Fang of Ir Yut",
        "Fang of Ir Yût (Adept)": "Fang of Ir Yut (Adept)"
    }

    # Process each file
    for input_file in input_files:
        if not os.path.exists(input_file):
            continue

        # Load JSON
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Correct names
        corrected_data = {}
        for hash_id, entry in data.items():
            corrected_entry = entry.copy()
            name = entry.get('displayProperties', {}).get('name', '').strip()
            if name in name_corrections:
                corrected_entry['displayProperties']['name'] = name_corrections[name]
            corrected_data[hash_id] = corrected_entry

        # Overwrite original JSON
        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(corrected_data, f, indent=4)

if __name__ == "__main__":
    correct_weapon_names()