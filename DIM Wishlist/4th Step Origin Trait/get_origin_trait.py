import json
import os
import re

def extract_origin_traits():
    # Define relative file paths
    script_dir = os.path.dirname(__file__)
    input_dir = os.path.join(script_dir, '..', '3rd Step Weapon Hashes', 'Json')
    perks_dir = os.path.join(script_dir, '..', '2nd Step Directory')
    output_dir = os.path.join(script_dir, 'Json')

    # Load DestinyInventoryItemDefinition.json using relative path
    item_data_path = os.path.join(perks_dir, 'DestinyInventoryItemDefinition.json')
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
    if not input_files:
        return

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

        updated_weapons = []
        for weapon in weapon_data.get('Weapons', []):
            weapon_name = weapon.get('name', '')
            item_hash = weapon.get('itemHash', '')
            origin_trait = weapon.get('originTrait', 'None')

            if not weapon_name or not item_hash:
                continue

            # Initialize entry with required fields
            entry = {
                'name': weapon_name,
                'itemHash': item_hash,
                'column1': weapon.get('column1', 'None'),
                'column2': weapon.get('column2', 'None'),
                'originTrait': origin_trait
            }

            # Parse existing originTrait for name and hash
            if origin_trait != 'None':
                match = re.match(r'(.+)\s*\((\d+)\)', origin_trait.strip())
                if match:
                    trait_name, trait_hash = match.groups()
                    entry['originTrait'] = f"{trait_name} ({trait_hash})"
                else:
                    # Look up originTrait in DestinyInventoryItemDefinition.json
                    for item_key, item in item_data.items():
                        if ('displayProperties' in item and
                            item.get('displayProperties', {}).get('name') == origin_trait and
                            item.get('itemTypeDisplayName') == 'Origin Trait'):
                            entry['originTrait'] = f"{origin_trait} ({item_key})"
                            break
            else:
                # If originTrait is "None", try to find a matching Origin Trait
                for item_key, item in item_data.items():
                    if ('displayProperties' in item and
                        item.get('itemTypeDisplayName') == 'Origin Trait'):
                        trait_name = item.get('displayProperties', {}).get('name', 'Unknown Origin')
                        entry['originTrait'] = f"{trait_name} ({item_key})"
                        break

            # Only include non-null fields
            updated_weapons.append({k: v for k, v in entry.items() if v is not None})

        # Save to category-specific JSON file
        if updated_weapons:
            output_filename = file_name
            output_path = os.path.join(output_dir, output_filename)
            os.makedirs(output_dir, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({"Weapons": updated_weapons}, f, indent=4)

if __name__ == "__main__":
    extract_origin_traits()