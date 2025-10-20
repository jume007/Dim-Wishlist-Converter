import json
import os
import re

def normalize_name(name):
    return ''.join(c for c in name.lower() if c.isalnum() or c.isspace()).strip()

def update_perk_hashes():
    # Define absolute file paths
    hashes_path = r"E:\Windows\Documents\D2 API\Weapons_Hash\weapon_hashes_final.json"
    perks_path = r"E:\Windows\Documents\D2 API\Weapon Perks\BaseWeaponPerks.json"
    output_path = r"E:\Windows\Documents\D2 API\Weapon Perks\weapon_perks_final.json"

    # Load JSON files
    with open(hashes_path, 'r', encoding='utf-8') as f:
        hashes_data = json.load(f)
    with open(perks_path, 'r', encoding='utf-8') as f:
        perks_data = json.load(f)

    # Initialize output structure
    updated_data = {"WeaponPerks": {}}

    # Process weapons from weapon_hashes_final.json
    for category, weapons in hashes_data.items():
        updated_data["WeaponPerks"][category] = []
        for weapon in weapons:
            name = weapon['name']
            item_hash = str(weapon['itemHash'])
            base_name = name.split(' (')[0].strip() if ' (' in name else name

            # Find matching weapon in perks_data
            perk_entry = None
            for perk_weapon, entry in perks_data.get('WeaponPerks', {}).items():
                if normalize_name(perk_weapon) == normalize_name(base_name):
                    perk_entry = entry
                    break

            # Update column1 and column2 from perks_data
            def update_perk_field(field, perk_map):
                if field == 'None':
                    return 'None'
                perks = [p.strip() for p in field.split(',')]
                updated_perks = []
                for p in perks:
                    match = re.match(r'(.+)\s*\((\d+)\)?', p.strip())  # Handle optional hash
                    perk_name = match.group(1).strip() if match else p.strip()
                    if perk_name in perk_map:
                        updated_perks.append(f"{perk_name} ({perk_map[perk_name]})")
                    else:
                        updated_perks.append(perk_name)
                return ', '.join(updated_perks) or 'None'

            # Update originTrait from perks_data
            def update_origin_field(field, perk_map):
                if field == 'None':
                    return 'None'
                
                match = re.match(r'(.+)\s*\((\d+)\)?', field.strip())
                if match:
                    return field  # Already has hash
                
                if field in perk_map:
                    return f"{field} ({perk_map[field]})"
                return field

            # Build perk map from BaseWeaponPerks.json
            perk_map = {}
            if perk_entry:
                perk_map = {p['perkName']: p['plugItemHash'] for p in perk_entry.get('perks', [])}

            # Build updated weapon entry
            updated_weapon = {
                'name': name,
                'itemHash': item_hash,
                'column1': update_perk_field(weapon.get('column1', 'None'), perk_map),
                'column2': update_perk_field(weapon.get('column2', 'None'), perk_map),
                'originTrait': update_origin_field(weapon.get('originTrait', 'None'), perk_map)
            }

            updated_data["WeaponPerks"][category].append(updated_weapon)

    # Remove empty categories
    updated_data["WeaponPerks"] = {k: v for k, v in updated_data["WeaponPerks"].items() if v}

    # Save results to JSON file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=4)

if __name__ == "__main__":
    update_perk_hashes()