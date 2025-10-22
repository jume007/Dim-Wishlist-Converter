import json
import os
import re

def test_perk_hashes_by_hash():
    # Define relative paths
    script_dir = os.path.dirname(__file__)
    input_dir = os.path.join(script_dir, '..', '5th Step Holofoil', 'Json')
    item_data_path = os.path.join(script_dir, '..', '2nd Step Directory', 'DestinyInventoryItemDefinition.json')
    plug_data_path = os.path.join(script_dir, '..', '2nd Step Directory', 'DestinyPlugSetDefinition.json')
    socket_type_path = os.path.join(script_dir, '..', '2nd Step Directory', 'DestinySocketTypeDefinition.json')
    output_dir = os.path.join(script_dir, 'testing')
    output_path = os.path.join(output_dir, 'testing2.json')

    # Check for required files
    if not os.path.exists(item_data_path):
        return
    if not os.path.exists(plug_data_path):
        return
    if not os.path.exists(socket_type_path):
        return

    # Load JSON files
    with open(item_data_path, 'r', encoding='utf-8') as f:
        item_data = json.load(f)
    with open(plug_data_path, 'r', encoding='utf-8') as f:
        plug_data = json.load(f)
    with open(socket_type_path, 'r', encoding='utf-8') as f:
        socket_type_data = json.load(f)

    # Manually specify itemHash for testing
    test_item_hash = "4095896073,3621336854"  # Replace with desired hash (e.g., Accrued Redemption)

    # Initialize updated weapons
    updated_weapons = []

    # Find matching weapon in input JSON
    weapon_entry = None
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.json') and os.path.isfile(os.path.join(input_dir, file_name)):
            input_path = os.path.join(input_dir, file_name)
            with open(input_path, 'r', encoding='utf-8') as f:
                category_data = json.load(f)
            for weapon in category_data.get('Weapons', []):
                if test_item_hash == weapon.get('itemHash', ''):
                    weapon_entry = weapon.copy()
                    break
            if weapon_entry:
                break

    if not weapon_entry:
        return

    # Split itemHash into individual hashes
    hash_list = [h.strip() for h in test_item_hash.split(',') if h.strip()]
    target_column1 = [p.strip() for p in weapon_entry.get('column1', 'None').split(',') if p.strip()]
    target_column2 = [p.strip() for p in weapon_entry.get('column2', 'None').split(',') if p.strip()]

    # Build perk map
    perk_map = {}
    for item_hash in hash_list:
        if item_hash in item_data:
            item_data_entry = item_data[item_hash]
            if 'damageTypeHashes' not in item_data_entry or not len(item_data_entry['damageTypeHashes']):
                continue

            if 'sockets' in item_data_entry and 'socketEntries' in item_data_entry['sockets']:
                socket_entries = item_data_entry['sockets']['socketEntries']
                for entry in socket_entries:
                    socket_type = socket_type_data.get(str(entry.get('socketTypeHash', 0)), {})
                    is_perk_socket = socket_type.get('socketCategoryHash') == 4241085061
                    if not is_perk_socket:
                        continue

                    # Randomized perks
                    if 'randomizedPlugSetHash' in entry:
                        plug_set = plug_data.get(str(entry['randomizedPlugSetHash']), {}).get('reusablePlugItems', [])
                        for plug_item in plug_set:
                            plug_item_hash = plug_item['plugItemHash']
                            perk_name = item_data.get(str(plug_item_hash), {}).get('displayProperties', {}).get('name', '')
                            if perk_name and plug_item_hash not in perk_map.values():
                                perk_map[perk_name] = str(plug_item_hash)
                    # Fixed perks
                    if 'singleInitialItemHash' in entry:
                        plug_item_hash = entry['singleInitialItemHash']
                        perk_name = item_data.get(str(plug_item_hash), {}).get('displayProperties', {}).get('name', '')
                        if perk_name and plug_item_hash not in perk_map.values():
                            perk_map[perk_name] = str(plug_item_hash)
                    # Reusable plug sets
                    if 'reusablePlugSetHash' in entry:
                        plug_set = plug_data.get(str(entry['reusablePlugSetHash']), {}).get('reusablePlugItems', [])
                        for plug_item in plug_set:
                            plug_item_hash = plug_item['plugItemHash']
                            perk_name = item_data.get(str(plug_item_hash), {}).get('displayProperties', {}).get('name', '')
                            if perk_name and plug_item_hash not in perk_map.values():
                                perk_map[perk_name] = str(plug_item_hash)

    # Update column1 and column2 with perk hashes
    def update_perk_field(field, perk_map):
        if field == 'None':
            return 'None'
        perks = [p.strip() for p in field.split(',')]
        updated_perks = []
        for p in perks:
            match = re.match(r'(.+)\s*\((\d+)\)?', p.strip())  # Handle existing hash
            perk_name = match.group(1).strip() if match else p.strip()
            if perk_name in perk_map:
                updated_perks.append(f"{perk_name} ({perk_map[perk_name]})")
            else:
                updated_perks.append(perk_name)
        return ', '.join(updated_perks) or 'None'

    # Update weapon entry
    updated_weapon = weapon_entry.copy()
    updated_weapon['itemHash'] = test_item_hash  # Keep original itemHash string
    updated_weapon['column1'] = update_perk_field(weapon_entry.get('column1', 'None'), perk_map)
    updated_weapon['column2'] = update_perk_field(weapon_entry.get('column2', 'None'), perk_map)
    updated_weapon = {k: v for k, v in updated_weapon.items() if v is not None and (k != 'variants' or v)}
    updated_weapons.append(updated_weapon)

    # Save to testing2.json
    if updated_weapons:
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({"Weapons": updated_weapons}, f, indent=4)

if __name__ == "__main__":
    test_perk_hashes_by_hash()