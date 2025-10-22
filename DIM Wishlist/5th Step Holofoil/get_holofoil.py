import json
import os

def update_holofoil_variants():
    # Define relative paths
    script_dir = os.path.dirname(__file__)
    input_dir = os.path.join(script_dir, '..', '4th Step Origin Trait', 'Json')
    item_data_path = os.path.join(script_dir, '..', '2nd Step Directory', 'DestinyInventoryItemDefinition.json')
    output_dir = os.path.join(script_dir, 'Json')

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

    for file_name in input_files:
        input_path = os.path.join(input_dir, file_name)
        # Load category JSON
        with open(input_path, 'r', encoding='utf-8') as f:
            category_data = json.load(f)

        updated_weapons = []
        for weapon in category_data.get('Weapons', []):
            weapon_name = weapon.get('name', '')
            item_hash = weapon.get('itemHash', '')
            if not weapon_name or not item_hash:
                continue

            # Check for holofoil versions using name
            is_holofoil = False
            holofoil_hashes = []
            base_name = weapon_name.split(' (')[0].strip()
            variant_names = [weapon_name] + [f"{base_name} ({var})" for var in ['Adept', 'Timelost', 'Harrowed']]
            for variant_name in variant_names:
                for key, value in item_data.items():
                    if ('displayProperties' in value and 'name' in value['displayProperties'] and
                        value['displayProperties']['name'].lower().strip() == variant_name.lower().strip() and
                        'damageTypeHashes' in value and len(value['damageTypeHashes']) and
                        value.get('isHolofoil', False) == True):
                        holofoil_hashes.append(str(value.get('hash', '')))
                        is_holofoil = True

            # Keep original itemHash
            variant_hashes = holofoil_hashes if holofoil_hashes else []

            # Build updated weapon entry
            updated_weapon = {
                'name': weapon_name,
                'itemHash': item_hash,  # Preserve original itemHash
                'isHolofoil': is_holofoil,
                'variants': ','.join(variant_hashes) if variant_hashes else '',
                'column1': weapon.get('column1', 'None'),
                'column2': weapon.get('column2', 'None'),
                'originTrait': weapon.get('originTrait', 'None'),
                'nonEnhancedHash': weapon.get('nonEnhancedHash', None),
                'nonEnhancedType': weapon.get('nonEnhancedType', None),
                'enhancedHash': weapon.get('enhancedHash', None),
                'enhancedType': weapon.get('enhancedType', None)
            }
            # Remove null fields and empty variants
            updated_weapon = {k: v for k, v in updated_weapon.items() if v is not None and (k != 'variants' or v)}
            updated_weapons.append(updated_weapon)

        # Save to category-specific JSON file
        if updated_weapons:
            output_filename = file_name
            output_path = os.path.join(output_dir, output_filename)
            os.makedirs(output_dir, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({"Weapons": updated_weapons}, f, indent=4)

if __name__ == "__main__":
    update_holofoil_variants()