import json
import os

# Load and process Destiny 2_Endgame Analysis.json
input_path = r"E:\Windows\Documents\D2 API\Ageis_Data\Destiny 2_Endgame Analysis.json"
if not os.path.exists(input_path):
    raise FileNotFoundError(f"Destiny 2_Endgame Analysis.json not found in {os.path.dirname(input_path)}")

with open(input_path, 'r', encoding='utf-8') as f:
    weapon_data = json.load(f)

# Load DestinyCollectibleDefinition.json from the specified directory
json_path = r"E:\Windows\Documents\D2 API\Weapon Perks\DestinyCollectibleDefinition.json"
if not os.path.exists(json_path):
    raise FileNotFoundError(f"DestinyCollectibleDefinition.json not found in {os.path.dirname(json_path)}")

with open(json_path, 'r', encoding='utf-8') as f:
    collectible_data = json.load(f)

# Match Brave and RoTn weapons to hash IDs and store in a dictionary
output_data = {}
for category, weapons in weapon_data.items():
    matched_weapons = []
    for weapon_entry in weapons:
        weapon_name = weapon_entry['name']
        # Check for BRAVE or RoTn versions in the weapon name
        if 'BRAVE version' in weapon_name or 'RotN version' in weapon_name:
            # Extract base weapon name, ignoring columns and traits
            base_name = ' '.join(weapon_name.split()[:-2]) if 'version' in weapon_name.lower() else weapon_name

            # Determine variant based on suffix
            if 'BRAVE version' in weapon_name:
                variant = 'BRAVE'
                full_weapon = f"{base_name} ({variant})"
            elif 'RotN version' in weapon_name:
                variant = 'RoTn'

            # Find the weapon hash using itemHash and sourceString
            if 'BRAVE version' in weapon_name:
                for item in collectible_data.values():
                    if ('displayProperties' in item and 'name' in item['displayProperties'] and
                        'itemHash' in item and 'sourceString' in item):
                        json_name = item['displayProperties']['name'].lower().strip()
                        source = item['sourceString'].lower().strip() if item['sourceString'] else ""
                        if json_name == base_name.lower().strip() and 'into the light' in source:
                            item_hash = item['itemHash']
                            matched_weapons.append({
                                'name': full_weapon,
                                'itemHash': item_hash,
                                'column1': weapon_entry['column1'],
                                'column2': weapon_entry['column2'],
                                'originTrait': weapon_entry['originTrait']
                            })
                            break
            elif 'RotN version' in weapon_name:
                # Check for normal RoTn variant first
                for item in collectible_data.values():
                    if ('displayProperties' in item and 'name' in item['displayProperties'] and
                        'itemHash' in item and 'sourceString' in item):
                        json_name = item['displayProperties']['name'].lower().strip()
                        source = item['sourceString'].lower().strip() if item['sourceString'] else ""
                        if json_name == base_name.lower().strip() and 'rite of the nine' in source and 'adept' not in json_name.lower():
                            item_hash = item['itemHash']
                            full_weapon = f"{base_name} (RoTn)"
                            matched_weapons.append({
                                'name': full_weapon,
                                'itemHash': item_hash,
                                'column1': weapon_entry['column1'],
                                'column2': weapon_entry['column2'],
                                'originTrait': weapon_entry['originTrait']
                            })
                            break
                # Check for RoTn Adept variant
                for item in collectible_data.values():
                    if ('displayProperties' in item and 'name' in item['displayProperties'] and
                        'itemHash' in item and 'sourceString' in item):
                        json_name = item['displayProperties']['name'].lower().strip()
                        source = item['sourceString'].lower().strip() if item['sourceString'] else ""
                        if f"{base_name.lower()} (adept)" in json_name and 'rite of the nine' in source:
                            item_hash = item['itemHash']
                            full_weapon = f"{base_name} (RoTn Adept)"
                            matched_weapons.append({
                                'name': full_weapon,
                                'itemHash': item_hash,
                                'column1': weapon_entry['column1'],
                                'column2': weapon_entry['column2'],
                                'originTrait': weapon_entry['originTrait']
                            })
                            break
    if matched_weapons:  # Only include categories with matched weapons
        output_data[category] = matched_weapons

# Save results to JSON file
output_path = r"E:\Windows\Documents\D2 API\Weapons_Hash\weapon_hashes_unquie.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as output_file:
    json.dump(output_data, output_file, indent=4)