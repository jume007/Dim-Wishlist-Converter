import json
import os
import re

def normalize_name(name):
    return ''.join(c for c in name.lower() if c.isalnum() or c.isspace()).strip()

# Update column1, column2, and originTrait with perk hashes
def update_perk_field(field, perk_map):
    if field == 'None':
        return 'None'
    perks = [p.strip() for p in field.split(',')]
    updated_perks = []
    for p in perks:
        match = re.match(r'(.+)\s*\((\d+)\)?', p.strip())  # Handle existing hash
        perk_name = match.group(1).strip() if match else p.strip()
        if perk_name in perk_map:
            ids = ', '.join(perk_map[perk_name])

            updated_perks.append(f"{perk_name} ({ids})")
        else:
            updated_perks.append(perk_name)
    return ', '.join(updated_perks) or 'None'


def update_perk_hashes():
    # Define relative paths
    script_dir = os.path.dirname(__file__)
    input_dir = os.path.join(script_dir, '..', '5th Step Holofoil', 'Json')
    item_data_path = os.path.join(script_dir, '..', '2nd Step Directory', 'DestinyInventoryItemDefinition.json')
    plug_set_definition_path = os.path.join(script_dir, '..', '2nd Step Directory', 'DestinyPlugSetDefinition.json')
    output_dir = os.path.join(script_dir, 'Json')

    # Check for item definition file
    if not os.path.exists(item_data_path) and os.path.exists(plug_set_definition_path):
        print("DestinyInventoryItemDefinition.json not found. Please run the 2nd Step Directory script first.")
        return

    if not os.path.exists(plug_set_definition_path):
        print("DestinyPlugSetDefinition.json not found. Please run the 2nd Step Directory script first.")
        return

    # Load DestinyInventoryItemDefinition.json
    with open(item_data_path, 'r', encoding='utf-8') as f:
        item_data = json.load(f)

    # Load DestinyPlugSetDefinition.json
    with open(plug_set_definition_path, 'r', encoding='utf-8') as f:
        plug_set_data = json.load(f)

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
            variants = weapon.get('variants', '')
            if not weapon_name or not item_hash:
                continue

            # Collect all hashes (itemHash and variants)
            hash_list = item_hash.split(',')
            if variants:
                hash_list.extend(variants.split(','))
            hash_list = [h.strip() for h in hash_list if h.strip()]

            # Build perk map from DestinyInventoryItemDefinition.json
            perk_map = {}
            for single_hash in hash_list:
                if single_hash in item_data:
                    sockets = item_data[single_hash].get('sockets', {}).get('socketEntries', [])
                    for socket in sockets:
                        plug_set = socket.get('reusablePlugItems', [])
                        for plug in plug_set:
                            plug_hash = str(plug.get('plugItemHash', ''))
                            plug_item = item_data.get(plug_hash, {})
                            plug_name = plug_item.get('displayProperties', {}).get('name', '')

                            if int(plug_hash) < 10:
                                continue

                            if plug_item['itemTypeDisplayName'] in ['Origin Trait', 'Enhanced Origin Trait']:
                                perk_map.setdefault(plug_name, set())
                                perk_map[plug_name].add(plug_hash)

                        plug_set = socket.get('randomizedPlugSetHash', None)
                        plug_item = plug_set_data.get(str(plug_set), {})
                        for each in plug_item.get('reusablePlugItems', []):
                            if each.get('currentlyCanRoll', False):
                                name = item_data.get(str(each.get('plugItemHash')), {}).get('displayProperties', {}).get('name', '')
                                hash = each.get('plugItemHash')
                                perk_map.setdefault(name, set())
                                perk_map[name].add(str(hash))

            # Build updated weapon entry
            updated_weapon = {
                'name': weapon_name,
                'itemHash': item_hash,
                'isHolofoil': weapon.get('isHolofoil', False),
                'variants': variants,
                'column1': update_perk_field(weapon.get('column1', 'None'), perk_map),
                'column2': update_perk_field(weapon.get('column2', 'None'), perk_map),
                'originTrait': update_perk_field(weapon.get('originTrait', 'None'), perk_map),
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
    update_perk_hashes()