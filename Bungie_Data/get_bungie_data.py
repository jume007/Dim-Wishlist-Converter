import json
import os

# Define paths
current_dir = os.path.dirname(__file__)

# Load definition files
collectible_path = os.path.join(current_dir, 'DestinyCollectibleDefinition.json')
collectible_data = {}
if os.path.exists(collectible_path):
    with open(collectible_path, 'r', encoding='utf-8') as f:
        collectible_data = json.load(f)

inventory_path = os.path.join(current_dir, 'DestinyInventoryItemDefinition.json')
inventory_data = {}
if os.path.exists(inventory_path):
    with open(inventory_path, 'r', encoding='utf-8') as f:
        inventory_data = json.load(f)

plugset_path = os.path.join(current_dir, 'DestinyPlugSetDefinition.json')
plugset_data = {}
if os.path.exists(plugset_path):
    with open(plugset_path, 'r', encoding='utf-8') as f:
        plugset_data = json.load(f)

socket_category_path = os.path.join(current_dir, 'DestinySocketCategoryDefinition-e657f3aa-0149-4d40-88f1-bd36d1c80375.json')
socket_category_data = {}
if os.path.exists(socket_category_path):
    with open(socket_category_path, 'r', encoding='utf-8') as f:
        socket_category_data = json.load(f)

socket_type_path = os.path.join(current_dir, 'DestinySocketTypeDefinition-e657f3aa-0149-4d40-88f1-bd36d1c80375.json')
socket_type_data = {}
if os.path.exists(socket_type_path):
    with open(socket_type_path, 'r', encoding='utf-8') as f:
        socket_type_data = json.load(f)

trait_path = os.path.join(current_dir, 'DestinyTraitDefinition-e657f3aa-0149-4d40-88f1-bd36d1c80375.json')
trait_data = {}
if os.path.exists(trait_path):
    with open(trait_path, 'r', encoding='utf-8') as f:
        trait_data = json.load(f)

# Combine into bungie_data
bungie_data = {
    'DestinyCollectibleDefinition': collectible_data,
    'DestinyInventoryItemDefinition': inventory_data,
    'DestinyPlugSetDefinition': plugset_data,
    'DestinySocketCategoryDefinition': socket_category_data,
    'DestinySocketTypeDefinition': socket_type_data,
    'DestinyTraitDefinition': trait_data
}

# Extract RandomizedPlugSetHashes
randomized_plugset_hashes = {}
for item_hash, item in inventory_data.items():
    if 'sockets' in item and 'socketCategories' in item:
        socket_entries = item['sockets'].get('socketEntries', [])
        socket_categories = item['sockets'].get('socketCategories', [])
        perk_category = next((cat for cat in socket_categories if cat.get('socketCategoryHash') == 4241085061), None)
        if perk_category:
            perk_indexes = perk_category.get('socketIndexes', [])
            for index in perk_indexes:
                if 0 <= index < len(socket_entries):
                    socket = socket_entries[index]
                    if 'randomizedPlugSetHash' in socket:
                        plug_set_hash = socket['randomizedPlugSetHash']
                        if str(plug_set_hash) in plugset_data:
                            plug_set = plugset_data[str(plug_set_hash)]
                            reusable_plugs = plug_set.get('reusablePlugItems', [])
                            perk_count = len([item for item in reusable_plugs if item.get('currentlyCanRoll', True)])
                            randomized_plugset_hashes[plug_set_hash] = {
                                'itemHash': item_hash,
                                'socketTypeHash': socket.get('socketTypeHash'),
                                'perkCount': perk_count
                            }

# Save RandomizedPlugSetHashes to a new JSON file
randomized_plugset_output_path = os.path.join(current_dir, 'RandomizedPlugSetHashes.json')
with open(randomized_plugset_output_path, 'w', encoding='utf-8') as f:
    json.dump(randomized_plugset_hashes, f, indent=4)

# Save the full bungie_data.json (optional, for reference)
output_path = os.path.join(current_dir, 'bungie_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(bungie_data, f, indent=4)

# Print summary (optional)
print(f"Generated RandomizedPlugSetHashes.json with {len(randomized_plugset_hashes)} entries.")