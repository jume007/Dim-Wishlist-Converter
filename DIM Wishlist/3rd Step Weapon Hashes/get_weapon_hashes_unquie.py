import json
import os

def resolve_no_hash_weapons():
    # Define relative paths
    script_dir = os.path.dirname(__file__)
    no_hash_file = os.path.join(script_dir, 'Unquie Json', 'no_weapon_hashes.json')
    collectible_file = os.path.join(script_dir, '..', '2nd Step Directory', 'DestinyCollectibleDefinition.json')
    output_dir = os.path.join(script_dir, 'Json')
    output_file = os.path.join(output_dir, 'unquie.json')

    # Check for input files
    if not os.path.exists(no_hash_file) or not os.path.exists(collectible_file):
        return

    # Load input files
    with open(no_hash_file, 'r', encoding='utf-8') as f:
        no_hash_data = json.load(f)
    with open(collectible_file, 'r', encoding='utf-8') as f:
        collectible_data = json.load(f)

    # Process weapons with no hashes
    matched_weapons = []
    for weapon in no_hash_data.get('Weapons', []):
        name = weapon.get('name', '')
        if not name:
            continue

        # Handle BRAVE or RotN versions
        base_name = name
        if 'BRAVE version' in name or 'RotN version' in name:
            base_name = ' '.join(name.split()[:-2]).strip()

        # Collect all matching variants
        variants = []
        for item in collectible_data.values():
            if ('displayProperties' not in item or 'name' not in item['displayProperties'] or
                'itemHash' not in item or 'sourceString' not in item):
                continue
            json_name = item['displayProperties']['name'].lower().strip()
            source = item['sourceString'].lower().strip() if item['sourceString'] else ""
            item_hash = str(item['itemHash'])

            if 'BRAVE version' in name and json_name == base_name.lower() and 'into the light' in source:
                variants.append({
                    'name': f"{base_name} (BRAVE)",
                    'itemHash': item_hash,
                    'column1': weapon.get('column1', 'None'),
                    'column2': weapon.get('column2', 'None'),
                    'originTrait': weapon.get('originTrait', 'None')
                })
            elif 'RotN version' in name:
                if json_name == base_name.lower() and 'rite of the nine' in source and 'adept' not in json_name.lower():
                    variants.append({
                        'name': f"{base_name} (RoTn)",
                        'itemHash': item_hash,
                        'column1': weapon.get('column1', 'None'),
                        'column2': weapon.get('column2', 'None'),
                        'originTrait': weapon.get('originTrait', 'None')
                    })
                if json_name == f"{base_name.lower()} (adept)" and 'rite of the nine' in source:
                    variants.append({
                        'name': f"{base_name} (RoTn Adept)",
                        'itemHash': item_hash,
                        'column1': weapon.get('column1', 'None'),
                        'column2': weapon.get('column2', 'None'),
                        'originTrait': weapon.get('originTrait', 'None')
                    })
            elif json_name == name.lower():
                variants.append({
                    'name': item['displayProperties']['name'],
                    'itemHash': item_hash,
                    'column1': weapon.get('column1', 'None'),
                    'column2': weapon.get('column2', 'None'),
                    'originTrait': weapon.get('originTrait', 'None')
                })

        # If no variants found, keep original weapon with empty itemHash
        if not variants:
            variants.append({
                'name': name,
                'itemHash': '',
                'column1': weapon.get('column1', 'None'),
                'column2': weapon.get('column2', 'None'),
                'originTrait': weapon.get('originTrait', 'None')
            })

        matched_weapons.extend(variants)

    # Save to unquie.json
    if matched_weapons:
        os.makedirs(output_dir, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"Weapons": matched_weapons}, f, indent=4)

if __name__ == "__main__":
    resolve_no_hash_weapons()