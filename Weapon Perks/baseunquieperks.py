import json
import os

def extract_rotn_brave_perk_sockets():
    # Define file paths
    weapon_hash_path = r"E:\Windows\Documents\D2 API\Weapons_Hash\weapon_hashes_unquie.json"
    item_data_path = r"E:\Windows\Documents\D2 API\Weapon Perks\DestinyInventoryItemDefinition.json"
    socket_type_path = r"E:\Windows\Documents\D2 API\Weapon Perks\DestinySocketTypeDefinition.json"
    plug_data_path = r"E:\Windows\Documents\D2 API\Weapon Perks\DestinyPlugSetDefinition.json"
    output_path = r"E:\Windows\Documents\D2 API\Weapon Perks\baseunquieperks.json"

    # Load JSON files
    with open(weapon_hash_path, 'r', encoding='utf-8') as f:
        weapon_hash_data = json.load(f)
    with open(item_data_path, 'r', encoding='utf-8') as f:
        item_data = json.load(f)
    with open(socket_type_path, 'r', encoding='utf-8') as f:
        socket_type_data = json.load(f)
    with open(plug_data_path, 'r', encoding='utf-8') as f:
        plug_data = json.load(f)

    # Extract RoTn and BRAVE weapon names from weapon_hashes_unquie.json
    weapons = []
    for category, weapon_entries in weapon_hash_data.items():
        for weapon_entry in weapon_entries:
            source_string = weapon_entry.get('sourceString', '').lower()
            if 'rite of the nine' in source_string or 'brave' in source_string:
                weapons.append(weapon_entry['name'])

    # Process perks
    weapon_perks = {}
    
    for weapon in weapons:
        weapon_perks[weapon] = {
            'perks': []
        }
        for item in item_data.values():  # Using item_data directly, assuming it contains name-to-hash mappings
            if item.get('displayProperties', {}).get('name', '').lower().strip() == weapon.lower().strip():
                item_hash = item.get('hash')
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

    # Wrap output in expected structure
    output_data = {"WeaponPerks": weapon_perks}

    # Save results to JSON file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4)

if __name__ == "__main__":
    extract_rotn_brave_perk_sockets()