import json
import os
import re

def update_perk_hashes():
    # Define relative paths
    script_dir = os.path.dirname(__file__)
    input_dir = os.path.join(script_dir, '..', '5th Step Holofoil', 'Json')
    item_data_path = os.path.join(script_dir, '..', '2nd Step Directory', 'DestinyInventoryItemDefinition.json')
    plug_data_path = os.path.join(script_dir, '..', '2nd Step Directory', 'DestinyPlugSetDefinition.json')
    socket_type_path = os.path.join(script_dir, '..', '2nd Step Directory', 'DestinySocketTypeDefinition.json')
    output_dir = os.path.join(script_dir, 'Json')

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

            # Split itemHash into individual hashes
            hash_list = [h.strip() for h in item_hash.split(',') if h.strip()]
            target_column1 = [p.strip() for p in weapon.get('column1', 'None').split(',') if p.strip()]
            target_column2 = [p.strip() for p in weapon.get('column2', 'None').split(',') if p.strip()]

            # Build perk map
            perk_map = {}
            column1_perks = []
            column2_perks = []
            socket_index = 0

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

            # Update weapon entry
            updated_weapon = weapon.copy()
            updated_weapon['column1'] = update_perk_field(target_column1 if target_column1 else column1_perks)
            updated_weapon['column2'] = update_perk_field(target_column2 if target_column2 else column2_perks)
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
    update_perk_hashes()