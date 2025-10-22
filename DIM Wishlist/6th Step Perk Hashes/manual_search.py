import json
import os
import re

def test_accrued_redemption_perks():
    # Define relative paths
    script_dir = os.path.dirname(__file__)
    input_dir = os.path.join(script_dir, '..', '2nd Step Directory')
    output_dir = os.path.join(script_dir, 'testing')
    output_path = os.path.join(output_dir, 'testing2.json')

    # Load required JSON files
    item_data_path = os.path.join(input_dir, 'DestinyInventoryItemDefinition.json')
    plug_data_path = os.path.join(input_dir, 'DestinyPlugSetDefinition.json')
    socket_type_path = os.path.join(input_dir, 'DestinySocketTypeDefinition.json')

    if not os.path.exists(item_data_path):
        return
    if not os.path.exists(plug_data_path):
        return
    if not os.path.exists(socket_type_path):
        return

    with open(item_data_path, 'r', encoding='utf-8') as f:
        item_data = json.load(f)
    with open(plug_data_path, 'r', encoding='utf-8') as f:
        plug_data = json.load(f)
    with open(socket_type_path, 'r', encoding='utf-8') as f:
        socket_type_data = json.load(f)

    # Manually specify itemHash for testing
    test_item_hash = "2063217087"  # Replace with desired hash (e.g., Accrued Redemption)

    # Initialize weapon entry
    weapon_entry = {
        'name': 'Unknown',
        'itemHash': test_item_hash,
        'isHolofoil': False,
        'variants': '',
        'column1': 'None',
        'column2': 'None',
        'originTrait': 'None',
        'nonEnhancedHash': None,
        'nonEnhancedType': None,
        'enhancedHash': None,
        'enhancedType': None
    }
    updated_weapons = []

    # Build perk map
    perk_map = {}
    column1_perks = []
    column2_perks = []
    socket_index = 0

    if test_item_hash in item_data:
        item_data_entry = item_data[test_item_hash]
        weapon_entry['name'] = item_data_entry.get('displayProperties', {}).get('name', 'Unknown')
        weapon_entry['isHolofoil'] = item_data_entry.get('isHolofoil', False)

        if 'damageTypeHashes' in item_data_entry and len(item_data_entry['damageTypeHashes']):
            if 'sockets' in item_data_entry and 'socketEntries' in item_data_entry['sockets']:
                socket_entries = item_data_entry['sockets']['socketEntries']
                for entry in socket_entries:
                    socket_type = socket_type_data.get(str(entry.get('socketTypeHash', 0)), {})
                    is_perk_socket = socket_type.get('socketCategoryHash') == 4241085061
                    if not is_perk_socket:
                        continue

                    # Collect perks for this socket
                    current_perks = []
                    # Randomized perks
                    if 'randomizedPlugSetHash' in entry:
                        plug_set = plug_data.get(str(entry['randomizedPlugSetHash']), {}).get('reusablePlugItems', [])
                        for plug_item in plug_set:
                            plug_item_hash = plug_item['plugItemHash']
                            perk_name = item_data.get(str(plug_item_hash), {}).get('displayProperties', {}).get('name', '')
                            if perk_name and plug_item_hash not in perk_map.values():
                                perk_map[perk_name] = str(plug_item_hash)
                                current_perks.append(perk_name)
                    # Fixed perks
                    if 'singleInitialItemHash' in entry:
                        plug_item_hash = entry['singleInitialItemHash']
                        perk_name = item_data.get(str(plug_item_hash), {}).get('displayProperties', {}).get('name', '')
                        if perk_name and plug_item_hash not in perk_map.values():
                            perk_map[perk_name] = str(plug_item_hash)
                            current_perks.append(perk_name)
                    # Reusable plug sets
                    if 'reusablePlugSetHash' in entry:
                        plug_set = plug_data.get(str(entry['reusablePlugSetHash']), {}).get('reusablePlugItems', [])
                        for plug_item in plug_set:
                            plug_item_hash = plug_item['plugItemHash']
                            perk_name = item_data.get(str(plug_item_hash), {}).get('displayProperties', {}).get('name', '')
                            if perk_name and plug_item_hash not in perk_map.values():
                                perk_map[perk_name] = str(plug_item_hash)
                                current_perks.append(perk_name)

                    # Assign perks to column1 or column2 based on socket order
                    if current_perks:
                        if socket_index == 0:
                            column1_perks.extend(current_perks)
                        elif socket_index == 1:
                            column2_perks.extend(current_perks)
                        socket_index += 1

    # Update column1 and column2 with perk hashes
    def update_perk_field(perks):
        if not perks:
            return 'None'
        updated_perks = []
        for perk in perks:
            if perk in perk_map:
                updated_perks.append(f"{perk} ({perk_map[perk]})")
            else:
                updated_perks.append(perk)
        return ', '.join(updated_perks) or 'None'

    weapon_entry['column1'] = update_perk_field(column1_perks)
    weapon_entry['column2'] = update_perk_field(column2_perks)

    # Add to updated weapons
    updated_weapon = {k: v for k, v in weapon_entry.items() if v is not None and (k != 'variants' or v)}
    updated_weapons.append(updated_weapon)

    # Save to testing2.json
    if updated_weapons:
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({"Weapons": updated_weapons}, f, indent=4)

if __name__ == "__main__":
    test_accrued_redemption_perks()