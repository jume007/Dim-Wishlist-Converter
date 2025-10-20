import json
import os

def lookup_holofoil_weapons():
    # Define relative file paths
    script_dir = os.path.dirname(__file__)
    hashes_dir = os.path.join(script_dir, '..', 'Weapons_Hash')
    perks_dir = os.path.join(script_dir, '..', 'Weapon Perks')
    output_dir = os.path.join(script_dir, '..', 'Holofoil')
    
    # Load weapon_hashes_final.json using relative path
    hashes_path = os.path.join(hashes_dir, 'weapon_hashes_final.json')
    if not os.path.exists(hashes_path):
        raise FileNotFoundError(f"weapon_hashes_final.json not found in Weapons_Hash directory relative to the script")

    # Load DestinyInventoryItemDefinition.json using relative path
    item_data_path = os.path.join(perks_dir, 'DestinyInventoryItemDefinition.json')
    if not os.path.exists(item_data_path):
        raise FileNotFoundError(f"DestinyInventoryItemDefinition.json not found in Weapon Perks directory relative to the script")

    with open(hashes_path, 'r', encoding='utf-8') as f:
        weapon_data = json.load(f)
    with open(item_data_path, 'r', encoding='utf-8') as f:
        item_data = json.load(f)

    # Search for holofoil versions of weapons from weapon_hashes_final.json
    holofoil_data = []
    for category, weapons in weapon_data.items():
        for weapon in weapons:
            weapon_name = weapon['name']
            base_name = weapon_name.split(' (')[0].strip()
            variants = [weapon_name] + [f"{base_name} ({var})" for var in ['Adept', 'Timelost', 'Harrowed']]
            weapon_entry = None

            for variant_name in variants:
                for key, value in item_data.items():
                    if ('damageTypeHashes' in value and len(value['damageTypeHashes']) and
                        'displayProperties' in value and 'name' in value['displayProperties'] and
                        value['displayProperties']['name'].lower().strip() == variant_name.lower().strip() and
                        value.get('isHolofoil', False)):
                        if weapon_entry is None:
                            weapon_entry = {
                                'name': variant_name,
                                'itemHash': value.get('hash'),
                                'isHolofoil': True,
                                'variants': []
                            }
                        else:
                            weapon_entry['variants'].append({
                                'name': variant_name,
                                'itemHash': value.get('hash'),
                                'isHolofoil': True
                            })

            if weapon_entry:
                holofoil_data.append(weapon_entry)

    # Save results to JSON file
    output_path = os.path.join(output_dir, 'holofoil_weapons.json')
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(holofoil_data, f, indent=4)

if __name__ == "__main__":
    lookup_holofoil_weapons()