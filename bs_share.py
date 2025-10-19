import json
import os

# Load DestinyInventoryItemDefinition.json from the current directory
json_path = os.path.join(os.path.dirname(__file__), 'DestinyInventoryItemDefinition.json')
if not os.path.exists(json_path):
    raise FileNotFoundError(f"DestinyInventoryItemDefinition.json not found in {json_path}")

with open(json_path, 'r', encoding='utf-8') as f:
    inventory_data = json.load(f)
    print(f"Loaded {len(inventory_data)} entries from {json_path}")  # Keep initial load message

data = bungie_data['DestinyInventoryItemDefinition']

# Perk name to search for
perk_name = "Physic"

# Find hash IDs for the perk and its enhanced variant
item_hash_non_enhanced = None
item_hash_enhanced = None
physic_count = 0  # To track how many "Physic" entries are found
for item_hash, item in data.items():
    if ('displayProperties' in item and 'name' in item['displayProperties'] and 'hash' in item):
        json_name = item['displayProperties']['name'].lower().strip()
        if json_name == perk_name.lower().strip():
            physic_count += 1
            if 'tooltipNotifications' in item and any("improves perk duration" in notif['displayString'].lower() for notif in item.get('tooltipNotifications', [])):
                item_hash_enhanced = item_hash  # Use the dictionary key as the hash
            else:
                item_hash_non_enhanced = item_hash  # Use the dictionary key as the hash
            print(item_hash_enhanced, item_hash_non_enhanced)

# Output the perk with its hash IDs and debug info
# output_path = os.path.join(os.path.dirname(__file__), 'PerkHashPhysic.txt')
# with open(output_path, 'w', encoding='utf-8') as output_file:  # 'w' mode overwrites existing file
#     output_file.write(f"Found {physic_count} entries for {perk_name}\n")
#     output_file.write(f"{perk_name} (Non-Enhanced), {item_hash_non_enhanced if item_hash_non_enhanced else 'Not Found'}\n")
#     output_file.write(f"{perk_name} (Enhanced), {item_hash_enhanced if item_hash_enhanced else 'Not Found'}\n")
