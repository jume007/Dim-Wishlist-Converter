import json
import os

def add_weapon_hashes():
    # Define relative paths
    script_dir = os.path.dirname(__file__)
    input_dir = os.path.join(script_dir, '..', '1st Step Convert', 'Json')
    collectible_file = os.path.join(script_dir, '..', '2nd Step Directory', 'DestinyCollectibleDefinition.json')
    output_dir = os.path.join(script_dir, 'Json')
    no_hash_dir = os.path.join(script_dir, 'Unquie Json')

    # Check for collectible file
    if not os.path.exists(collectible_file):
        return

    # Load DestinyCollectibleDefinition.json
    with open(collectible_file, 'r', encoding='utf-8') as f:
        collectible_data = json.load(f)

    # Build weapon hash map (group hashes by exact name and variants)
    weapon_hash_map = {}
    variant_suffixes = ['Adept', 'Timelost', 'Harrowed']
    for collectible in collectible_data.values():
        name = collectible.get('displayProperties', {}).get('name', '').strip()
        item_hash = str(collectible.get('itemHash', ''))
        if name:
            # Store by exact name
            if name.lower() not in weapon_hash_map:
                weapon_hash_map[name.lower()] = []
            weapon_hash_map[name.lower()].append((name, item_hash))
            # Also store by base name for variant lookup
            base_name = name.split(' (')[0].strip().lower()
            if base_name not in weapon_hash_map:
                weapon_hash_map[base_name] = []
            weapon_hash_map[base_name].append((name, item_hash))

    # Process category JSON files
    weapon_sheets = ['Autos', 'Bows', 'HCs', 'Pulses', 'Scouts', 'Sidearms', 'SMGs', 'BGLs', 'Fusions', 'Glaives', 'Shotguns', 'Snipers', 'HGLs', 'LFRs', 'LMGs', 'Rockets', 'Swords', 'Other', 'Rocket Sidearms', 'Traces']
    no_hash_weapons = []

    for sheet_name in weapon_sheets:
        input_path = os.path.join(input_dir, f"{sheet_name}.json")
        if not os.path.exists(input_path):
            continue

        # Load category JSON
        with open(input_path, 'r', encoding='utf-8') as f:
            category_data = json.load(f)

        updated_weapons = []
        seen_entries = set()  # Track unique (name, itemHash) pairs to avoid duplicates

        for weapon in category_data.get('Weapons', []):
            name = weapon.get('name', '')
            if not name:
                continue

            # Try exact match first
            matches = weapon_hash_map.get(name.lower(), [])
            # Try base name to include variants
            base_name = name.split(' (')[0].strip().lower()
            if not matches:
                matches = weapon_hash_map.get(base_name, [])

            if not matches:
                no_hash_weapons.append({
                    'name': name,
                    'itemHash': '',
                    'column1': weapon.get('column1', 'None'),
                    'column2': weapon.get('column2', 'None'),
                    'originTrait': weapon.get('originTrait', 'None')
                })
                continue

            # Create an entry for each matching itemHash
            for matched_name, item_hash in matches:
                if (matched_name, item_hash) not in seen_entries:
                    updated_weapon = {
                        'name': matched_name,  # Preserve full name with (Adept), (Harrowed), (Timelost)
                        'itemHash': item_hash,
                        'column1': weapon.get('column1', 'None'),
                        'column2': weapon.get('column2', 'None'),
                        'originTrait': weapon.get('originTrait', 'None')
                    }
                    updated_weapons.append(updated_weapon)
                    seen_entries.add((matched_name, item_hash))

        # Save to category-specific JSON file
        if updated_weapons:
            output_filename = f"{sheet_name}.json"
            output_path = os.path.join(output_dir, output_filename)
            os.makedirs(output_dir, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({"Weapons": updated_weapons}, f, indent=4)

    # Save weapons with no hashes to a single JSON file
    if no_hash_weapons:
        no_hash_path = os.path.join(no_hash_dir, 'no_weapon_hashes.json')
        os.makedirs(no_hash_dir, exist_ok=True)
        with open(no_hash_path, 'w', encoding='utf-8') as f:
            json.dump({"Weapons": no_hash_weapons}, f, indent=4)

if __name__ == "__main__":
    add_weapon_hashes()