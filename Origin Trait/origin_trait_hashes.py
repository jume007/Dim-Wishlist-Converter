import json
import os
import re

def extract_origin_traits():
    # Define relative file paths
    script_dir = os.path.dirname(__file__)
    weapon_hashes_dir = os.path.join(script_dir, '..', 'Weapons_Hash')
    perks_dir = os.path.join(script_dir, '..', 'Weapon Perks')
    output_dir = os.path.join(script_dir, '..', 'Origin Trait')
    
    # Load weapon_hashes_final.json using relative path
    hashes_path = os.path.join(weapon_hashes_dir, 'weapon_hashes_final.json')
    if not os.path.exists(hashes_path):
        raise FileNotFoundError(f"weapon_hashes_final.json not found in {weapon_hashes_dir}")

    # Load DestinyInventoryItemDefinition.json using relative path
    item_data_path = os.path.join(perks_dir, 'DestinyInventoryItemDefinition.json')
    if not os.path.exists(item_data_path):
        raise FileNotFoundError(f"DestinyInventoryItemDefinition.json not found in {perks_dir}")

    with open(hashes_path, 'r', encoding='utf-8') as f:
        weapon_data = json.load(f)
    with open(item_data_path, 'r', encoding='utf-8') as f:
        item_data = json.load(f)

    # Process weapons to extract origin traits
    origin_traits = {}
    for category, weapons in weapon_data.items():
        for weapon in weapons:
            weapon_name = weapon['name']
            item_hash = weapon['itemHash']
            origin_trait = weapon.get('originTrait', 'None')

            # Initialize entry with required fields
            entry = {'itemHash': item_hash, 'originTrait': origin_trait}

            if origin_trait == 'None':
                origin_traits[weapon_name] = entry
                continue

            # Parse origin trait name and hash
            match = re.match(r'(.+)\s\((\d+)\)', origin_trait.strip())
            if match:
                trait_name, trait_hash = match.groups()
                trait_hash = int(trait_hash)
            else:
                trait_name = origin_trait
                trait_hash = None

            # First run: Check the provided trait_hash for Common Trait
            if trait_hash is not None:
                item = item_data.get(str(trait_hash), {})
                item_type = item.get('itemTypeDisplayName')
                if item_type == 'Origin Trait':
                    entry['nonEnhancedHash'] = trait_hash
                    entry['nonEnhancedType'] = 'Common Trait'
                elif item_type == 'Enhanced Origin Trait':
                    entry['enhancedHash'] = trait_hash
                    entry['enhancedType'] = 'Uncommon Enhanced Trait'

            # Second run: Find the opposite type
            for item_key, item in item_data.items():
                if ('displayProperties' in item and
                    item['displayProperties']['name'] == trait_name):
                    item_type = item.get('itemTypeDisplayName')
                    if item_type == 'Origin Trait' and ('nonEnhancedHash' not in entry or entry['nonEnhancedHash'] != int(item_key)):
                        entry['nonEnhancedHash'] = int(item_key)
                        entry['nonEnhancedType'] = 'Common Trait'
                    elif item_type == 'Enhanced Origin Trait' and ('enhancedHash' not in entry or entry['enhancedHash'] != int(item_key)):
                        entry['enhancedHash'] = int(item_key)
                        entry['enhancedType'] = 'Uncommon Enhanced Trait'

            # Only include non-null fields
            origin_traits[weapon_name] = {k: v for k, v in entry.items() if v is not None}

    # Save results to JSON file using relative path
    output_path = os.path.join(output_dir, 'origin_traits.json')
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(origin_traits, f, indent=4)

if __name__ == "__main__":
    extract_origin_traits()