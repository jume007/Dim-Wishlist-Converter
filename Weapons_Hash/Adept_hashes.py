import json
import os

def normalize_name(name):
    return ''.join(c for c in name.lower() if c.isalnum() or c.isspace()).strip()

def find_variant_hashes():
    # Define file paths
    input_path = r"E:\Windows\Documents\D2 API\Ageis_data\Destiny 2_Endgame Analysis.json"
    item_path = r"E:\Windows\Documents\D2 API\Weapon Perks\DestinyInventoryItemDefinition.json"
    output_path = r"E:\Windows\Documents\D2 API\Weapons_Hash\Adept_hashes.json"

    # Load JSON files
    with open(input_path, 'r', encoding='utf-8') as f:
        weapon_data = json.load(f)
    with open(item_path, 'r', encoding='utf-8') as f:
        item_data = json.load(f)

    # Initialize output data
    output_data = {}

    # Process each category in Destiny 2_Endgame Analysis.json
    for category, weapons in weapon_data.items():
        matched_weapons = []
        for weapon_entry in weapons:
            weapon_name = weapon_entry['name']
            # Extract base name and variant
            base_name = weapon_name.split(' (')[0].strip()
            is_variant = ' (' in weapon_name
            variant_suffix = weapon_name.split(' (')[1].rstrip(')') if is_variant else None

            # Skip RoTN and BRAVE variants
            if is_variant and variant_suffix in ['RoTN', 'BRAVE']:
                continue

            # Try matching Timelost, Adept, Harrowed variants
            for variant in ['Timelost', 'Adept', 'Harrowed']:
                variant_name = f"{base_name} ({variant})"
                for key, item in item_data.items():
                    if ('displayProperties' in item and 'name' in item['displayProperties'] and
                        'damageTypeHashes' in item and len(item['damageTypeHashes']) > 0):  # Ensure it's a weapon
                        json_name = item['displayProperties']['name']
                        if normalize_name(json_name) == normalize_name(variant_name):
                            item_hash = item.get('hash')
                            if item_hash is not None:
                                matched_weapons.append({
                                    'name': variant_name,
                                    'itemHash': item_hash,
                                    'column1': weapon_entry['column1'],
                                    'column2': weapon_entry['column2'],
                                    'originTrait': weapon_entry['originTrait']
                                })
                                break

        # Add category to output if matches found
        if matched_weapons:
            output_data[category] = matched_weapons

    # Save results to JSON file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as output_file:
        json.dump(output_data, output_file, indent=4)

if __name__ == "__main__":
    find_variant_hashes()