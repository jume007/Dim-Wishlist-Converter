import json
import os

def merge_weapon_hashes():
    # Define relative paths
    script_dir = os.path.dirname(__file__)
    input_dir = os.path.join(script_dir, 'Json')

    # Get all JSON files in input directory
    input_files = []
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.json') and os.path.isfile(os.path.join(input_dir, file_name)):
            input_files.append(file_name)

    for file_name in input_files:
        input_path = os.path.join(input_dir, file_name)
        # Load JSON
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Merge entries with matching names
        merged_weapons = {}
        for weapon in data.get('Weapons', []):
            name = weapon.get('name', '')
            if not name:
                continue

            # Initialize entry if name not seen
            if name not in merged_weapons:
                merged_weapons[name] = {
                    'name': name,
                    'itemHash': [],
                    'column1': weapon.get('column1', 'None'),
                    'column2': weapon.get('column2', 'None'),
                    'originTrait': weapon.get('originTrait', 'None')
                }

            # Add itemHash to the list
            item_hash = str(weapon.get('itemHash', ''))
            if item_hash and item_hash not in merged_weapons[name]['itemHash']:
                merged_weapons[name]['itemHash'].append(item_hash)

        # Convert itemHash lists to comma-separated strings
        updated_weapons = []
        for weapon in merged_weapons.values():
            updated_weapon = {
                'name': weapon['name'],
                'itemHash': ','.join(weapon['itemHash']) if weapon['itemHash'] else '',
                'column1': weapon['column1'],
                'column2': weapon['column2'],
                'originTrait': weapon['originTrait']
            }
            updated_weapons.append(updated_weapon)

        # Overwrite original JSON file
        if updated_weapons:
            output_path = os.path.join(input_dir, file_name)
            os.makedirs(input_dir, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({"Weapons": updated_weapons}, f, indent=4)

if __name__ == "__main__":
    merge_weapon_hashes()