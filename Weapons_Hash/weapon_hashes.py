import json
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, filename='weapon_matching.log', filemode='w',
                    format='%(levelname)s: %(message)s')

# Load Destiny 2_Endgame Analysis.json
input_path = r"E:\Windows\Documents\D2 API\Ageis_data\Destiny 2_Endgame Analysis.json"
if not os.path.exists(input_path):
    raise FileNotFoundError(f"Destiny 2_Endgame Analysis.json not found in {os.path.dirname(input_path)}")

with open(input_path, 'r', encoding='utf-8') as f:
    weapon_data = json.load(f)

# Load DestinyInventoryItemDefinition.json
item_path = r"E:\Windows\Documents\D2 API\Weapon Perks\DestinyInventoryItemDefinition.json"
if not os.path.exists(item_path):
    raise FileNotFoundError(f"DestinyInventoryItemDefinition.json not found in {os.path.dirname(item_path)}")

with open(item_path, 'r', encoding='utf-8') as f:
    item_data = json.load(f)

# Normalize name function
def normalize_name(name):
    return ''.join(c for c in name.lower() if c.isalnum() or c.isspace()).strip()

# Source identifiers for Iron Banner, Crucible, Nightfall
source_identifiers = {
    'Iron Banner': ['Iron Banner', 'sourceHash: 1821699360'],
    'Crucible': ['Crucible', 'sourceHash: 897576623'],
    'Nightfall': ['Nightfall', 'sourceHash: 1469913806']
}

# Match weapon names to hash IDs
output_data = {}
unmatched_weapons = []
for category, weapons in weapon_data.items():
    matched_weapons = []
    for weapon_entry in weapons:
        weapon_name = weapon_entry['name']
        # Extract base name and variant
        base_name = weapon_name.split(' (')[0].strip()
        is_variant = ' (' in weapon_name
        variant_suffix = weapon_name.split(' (')[1].rstrip(')') if is_variant else None

        matched = False
        # Try exact match in DestinyInventoryItemDefinition.json
        for key, item in item_data.items():
            if ('displayProperties' in item and 'name' in item['displayProperties'] and
                'damageTypeHashes' in item and len(item['damageTypeHashes']) > 0):  # Ensure it's a weapon
                json_name = item['displayProperties']['name']
                source_string = item.get('sourceString', '')
                source_hash = str(item.get('sourceHash', ''))

                # Check for Iron Banner, Crucible, Nightfall sources
                is_source_match = False
                for source, identifiers in source_identifiers.items():
                    if any(identifier in source_string or identifier == source_hash for identifier in identifiers):
                        if category.lower() == source.lower():
                            is_source_match = True
                            break

                # Exact match with source priority
                if (normalize_name(json_name) == normalize_name(weapon_name) and
                    (is_source_match or category.lower() not in ['iron banner', 'crucible', 'nightfall'])):
                    item_hash = item.get('hash')
                    if item_hash is not None:
                        matched_weapons.append({
                            'name': weapon_name,
                            'itemHash': item_hash,
                            'column1': weapon_entry['column1'],
                            'column2': weapon_entry['column2'],
                            'originTrait': weapon_entry['originTrait']
                        })
                        logging.info(f"Matched: {weapon_name} -> {item_hash} (Source: {source_string})")
                        matched = True
                        break

        # If no exact match, try base name or variant
        if not matched:
            for key, item in item_data.items():
                if ('displayProperties' in item and 'name' in item['displayProperties'] and
                    'damageTypeHashes' in item and len(item['damageTypeHashes']) > 0):
                    json_name = item['displayProperties']['name']
                    json_base_name = json_name.split(' (')[0].strip()
                    source_string = item.get('sourceString', '')
                    source_hash = str(item.get('sourceHash', ''))

                    # Check source for category
                    is_source_match = False
                    for source, identifiers in source_identifiers.items():
                        if any(identifier in source_string or identifier == source_hash for identifier in identifiers):
                            if category.lower() == source.lower():
                                is_source_match = True
                                break

                    # Match base name for non-variants
                    if (not is_variant and normalize_name(json_base_name) == normalize_name(base_name) and
                        (is_source_match or category.lower() not in ['iron banner', 'crucible', 'nightfall'])):
                        item_hash = item.get('hash')
                        if item_hash is not None:
                            matched_weapons.append({
                                'name': base_name,
                                'itemHash': item_hash,
                                'column1': weapon_entry['column1'],
                                'column2': weapon_entry['column2'],
                                'originTrait': weapon_entry['originTrait']
                            })
                            logging.info(f"Matched base: {base_name} -> {item_hash} (Source: {source_string})")
                            matched = True
                            break
                    # Match variants (Adept, Timelost, Harrowed, Craftable, BRAVE)
                    elif is_variant and variant_suffix in ['Adept', 'Timelost', 'Harrowed', 'Craftable', 'BRAVE']:
                        variant_name = f"{base_name} ({variant_suffix})"
                        if (normalize_name(json_name) == normalize_name(variant_name) and
                            (is_source_match or category.lower() not in ['iron banner', 'crucible', 'nightfall'])):
                            item_hash = item.get('hash')
                            if item_hash is not None:
                                matched_weapons.append({
                                    'name': variant_name,
                                    'itemHash': item_hash,
                                    'column1': weapon_entry['column1'],
                                    'column2': weapon_entry['column2'],
                                    'originTrait': weapon_entry['originTrait']
                                })
                                logging.info(f"Matched variant: {variant_name} -> {item_hash} (Source: {source_string})")
                                matched = True
                                break

        if not matched:
            unmatched_weapons.append(weapon_name)
            logging.warning(f"Unmatched weapon: {weapon_name}")

    if matched_weapons:
        output_data[category] = matched_weapons

# Log summary
logging.info(f"Total unmatched weapons: {len(unmatched_weapons)}")
if unmatched_weapons:
    logging.info(f"Unmatched weapons list: {unmatched_weapons}")

# Save results to JSON file
output_path = r"E:\Windows\Documents\D2 API\Weapons_Hash\WeaponHashes.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as output_file:
    json.dump(output_data, output_file, indent=4)