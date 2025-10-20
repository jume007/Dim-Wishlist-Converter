import json
import os

def extract_weapon_perks():
    # Define relative file paths
    script_dir = os.path.dirname(__file__)
    input_dir = os.path.join(script_dir, '..', 'Weapon Perks')
    output_dir = os.path.join(script_dir, '..', 'Testing')
    
    # Load existing JSON files
    item_data_path = os.path.join(input_dir, 'DestinyInventoryItemDefinition.json')
    collectible_data_path = os.path.join(input_dir, 'DestinyCollectibleDefinition.json')
    plug_data_path = os.path.join(input_dir, 'DestinyPlugSetDefinition.json')
    socket_type_path = os.path.join(input_dir, 'DestinySocketTypeDefinition.json')

    if not os.path.exists(item_data_path):
        raise FileNotFoundError(f"DestinyInventoryItemDefinition.json not found in Weapon Perks directory relative to the script")
    if not os.path.exists(collectible_data_path):
        raise FileNotFoundError(f"DestinyCollectibleDefinition.json not found in Weapon Perks directory relative to the script")
    if not os.path.exists(plug_data_path):
        raise FileNotFoundError(f"DestinyPlugSetDefinition.json not found in Weapon Perks directory relative to the script")
    if not os.path.exists(socket_type_path):
        raise FileNotFoundError(f"DestinySocketTypeDefinition.json not found in Weapon Perks directory relative to the script")

    with open(item_data_path, 'r', encoding='utf-8') as f:
        item_data = json.load(f)
    with open(collectible_data_path, 'r', encoding='utf-8') as f:
        collectible_data = json.load(f)
    with open(plug_data_path, 'r', encoding='utf-8') as f:
        plug_data = json.load(f)
    with open(socket_type_path, 'r', encoding='utf-8') as f:
        socket_type_data = json.load(f)

    # Process Accrued Redemption perks
    weapons = ['Reckless Oracle']
    weapon_perks = {}
    
    for weapon in weapons:
        weapon_perks[weapon] = {
            'perks': []
        }
        for item in collectible_data.values():
            if item['displayProperties']['name'].lower().strip() == weapon.lower().strip():
                item_hash = item.get('itemHash')
                if item_hash is None:
                    continue
                # Validate itemHash has non-empty damageTypeHashes
                item_data_entry = item_data.get(str(item_hash), {})
                if not ('damageTypeHashes' in item_data_entry and len(item_data_entry['damageTypeHashes'])):
                    continue
                weapon_perks[weapon]['itemHash'] = item_hash

                if 'sockets' in item_data_entry and 'socketEntries' in item_data_entry['sockets']:
                    socket_entries = item_data_entry['sockets']['socketEntries']
                    for entry in socket_entries:
                        # Check if socket is a perk socket
                        socket_type = socket_type_data.get(str(entry.get('socketTypeHash', 0)), {})
                        is_perk_socket = socket_type.get('socketCategoryHash') == 4241085061
                        if not is_perk_socket:
                            continue

                        # Randomized perks
                        if 'randomizedPlugSetHash' in entry:
                            plug_set = plug_data.get(str(entry['randomizedPlugSetHash']), {}).get('reusablePlugItems', [])
                            for plug_item in plug_set:
                                plug_item_hash = plug_item['plugItemHash']
                                perk_name = item_data.get(str(plug_item_hash), {}).get('displayProperties', {}).get('name', 'Unknown')
                                if not any(p['plugItemHash'] == plug_item_hash for p in weapon_perks[weapon]['perks']):
                                    weapon_perks[weapon]['perks'].append({
                                        'plugItemHash': plug_item_hash,
                                        'perkName': perk_name
                                    })
                        # Fixed perks
                        if 'singleItemHash' in entry:
                            plug_item_hash = entry['singleItemHash']
                            perk_name = item_data.get(str(plug_item_hash), {}).get('displayProperties', {}).get('name', 'Unknown')
                            if not any(p['plugItemHash'] == plug_item_hash for p in weapon_perks[weapon]['perks']):
                                weapon_perks[weapon]['perks'].append({
                                    'plugItemHash': plug_item_hash,
                                    'perkName': perk_name
                                })
                        # Reusable plug sets (e.g., origin traits)
                        if 'reusablePlugSetHash' in entry:
                            plug_set = plug_data.get(str(entry['reusablePlugSetHash']), {}).get('reusablePlugItems', [])
                            for plug_item in plug_set:
                                plug_item_hash = plug_item['plugItemHash']
                                perk_name = item_data.get(str(plug_item_hash), {}).get('displayProperties', {}).get('name', 'Unknown')
                                if not any(p['plugItemHash'] == plug_item_hash for p in weapon_perks[weapon]['perks']):
                                    weapon_perks[weapon]['perks'].append({
                                        'plugItemHash': plug_item_hash,
                                        'perkName': perk_name
                                    })

    # Save results to JSON file
    output_path = os.path.join(output_dir, 'AccruedRedemptionPerks.json')
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(weapon_perks, f, indent=4)

if __name__ == "__main__":
    extract_weapon_perks()