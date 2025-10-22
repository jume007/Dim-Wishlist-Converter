import json
import os
import re

def update_heresy_hashes():
    # Define relative file paths
    script_dir = os.path.dirname(__file__)
    input_dir = os.path.join(script_dir, 'Json')
    item_data_path = os.path.join(script_dir, '..', '2nd Step Directory', 'DestinyInventoryItemDefinition.json')
    output_dir = os.path.join(script_dir, 'Unquie Json')
    output_path = os.path.join(output_dir, 'heresy.json')

    # Check for item definition file
    if not os.path.exists(item_data_path):
        return

    # Load DestinyInventoryItemDefinition.json
    with open(item_data_path, 'r', encoding='utf-8') as f:
        item_data = json.load(f)

    # Get all JSON files in input directory
    input_files = []
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.json') and os.path.isfile(os.path.join(input_dir, file_name)):
            input_files.append(file_name)

    # Initialize list for heresy weapons
    heresy_weapons = []

    for file_name in input_files:
        input_path = os.path.join(input_dir, file_name)
        # Load category JSON
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                weapon_data = json.load(f)
        except Exception:
            continue

        if 'Weapons' not in weapon_data:
            continue

        for weapon in weapon_data.get('Weapons', []):
            weapon_name = weapon.get('name', '')
            item_hash = weapon.get('itemHash', '')

            if not weapon_name or not item_hash:
                continue

            # Get existing hashes
            current_hashes = [h.strip() for h in item_hash.split(',') if h.strip()]

            # Check if weapon matches Heresy Activities source
            matches_heresy = False
            matching_hashes = []
            for hash in current_hashes:
                item = item_data.get(hash, {})
                if item.get('sourceString') == 'Source: Episode: Heresy Activities':
                    matches_heresy = True
                    break

            # If no direct hash match, check by name
            if not matches_heresy:
                for item_key, item in item_data.items():
                    if (item.get('displayProperties', {}).get('name') == weapon_name and
                        item.get('sourceString') == 'Source: Episode: Heresy Activities'):
                        matches_heresy = True
                        if item_key not in current_hashes:
                            matching_hashes.append(item_key)

            # If weapon matches Heresy Activities, update itemHash and include in output
            if matches_heresy:
                entry = weapon.copy()
                if matching_hashes:
                    entry['itemHash'] = ','.join(current_hashes + matching_hashes)
                heresy_weapons.append(entry)

    # Save to heresy.json
    if heresy_weapons:
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({"Weapons": heresy_weapons}, f, indent=4)

if __name__ == "__main__":
    update_heresy_hashes()