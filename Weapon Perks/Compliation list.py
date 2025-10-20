import json
import os
import re

def normalize_name(name):
    return ''.join(c for c in name.lower() if c.isalnum() or c.isspace()).strip()

def update_perk_hashes():
    # Define relative file paths
    script_dir = os.path.dirname(__file__)
    hashes_path = os.path.join(script_dir, '..', 'Weapons_Hash', 'weapon_hashes_final.json')
    perks_path = os.path.join(script_dir, '..', 'Weapon Perks', 'WeaponPerks.json')
    origin_traits_path = os.path.join(script_dir, '..', 'Origin Trait', 'origin_traits.json')
    holofoil_path = os.path.join(script_dir, '..', 'Holofoil', 'holofoil_weapons.json')
    output_path = os.path.join(script_dir, '..', 'Weapon Perks', 'weapon_perks_final.json')

    # Check if input files exist
    for path in [hashes_path, perks_path, origin_traits_path, holofoil_path]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

    # Load JSON files
    with open(hashes_path, 'r', encoding='utf-8') as f:
        hashes_data = json.load(f)
    with open(perks_path, 'r', encoding='utf-8') as f:
        perks_data = json.load(f)
    with open(origin_traits_path, 'r', encoding='utf-8') as f:
        origin_traits_data = json.load(f)
    with open(holofoil_path, 'r', encoding='utf-8') as f:
        holofoil_data = json.load(f)

    # Process weapons
    updated_data = {"WeaponPerks": {}}
    for category, weapons in hashes_data.items():
        updated_data["WeaponPerks"][category] = []
        for weapon in weapons:
            name = weapon['name']
            item_hash = str(weapon['itemHash'])

            # Find matching weapon in perks_data
            perk_entry = None
            for perk_category in perks_data.get('WeaponPerks', {}).values():
                for entry in perk_category:
                    if normalize_name(entry['name']) == normalize_name(name) and str(entry['itemHash']) == item_hash:
                        perk_entry = entry
                        break
                if perk_entry:
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

            # Update originTrait from origin_traits_data
            def update_origin_field(field, weapon_name):
                if field == 'None':
                    return 'None'
                
                match = re.match(r'(.+)\s*\((\d+)\)?', field.strip())
                if match:
                    return field  # Already has hash
                
                # Handle different origin_traits_data structures
                trait_hash = None
                if isinstance(origin_traits_data, dict):
                    # If dictionary, try to find by weapon name
                    weapon_traits = origin_traits_data.get(weapon_name) or origin_traits_data.get(name.split(' (')[0].strip())
                    if weapon_traits:
                        if isinstance(weapon_traits, dict):
                            trait_hash = weapon_traits.get('plugItemHash') or weapon_traits.get('nonEnhancedHash') or weapon_traits.get('enhancedHash')
                            field = weapon_traits.get('name', field)
                        elif isinstance(weapon_traits, str):
                            trait_hash = weapon_traits
                elif isinstance(origin_traits_data, list):
                    # If list, search for matching trait name
                    for trait in origin_traits_data:
                        if isinstance(trait, dict) and normalize_name(trait.get('name', '')) == normalize_name(field):
                            trait_hash = trait.get('plugItemHash') or trait.get('nonEnhancedHash') or trait.get('enhancedHash')
                            break
                
                if trait_hash:
                    return f"{field} ({trait_hash})"
                return field

            # Check for holofoil versions
            is_holofoil = False
            holofoil_variants = []
            for holofoil_entry in holofoil_data:
                if normalize_name(holofoil_entry['name']) == normalize_name(name) and holofoil_entry.get('isHolofoil'):
                    is_holofoil = True
                    if str(holofoil_entry['itemHash']) != item_hash:
                        holofoil_variants.append({
                            'name': holofoil_entry['name'],
                            'itemHash': holofoil_entry['itemHash']
                        })
                for variant in holofoil_entry.get('variants', []):
                    if normalize_name(variant['name']) == normalize_name(name) and variant.get('isHolofoil'):
                        is_holofoil = True
                        if str(variant['itemHash']) != item_hash:
                            holofoil_variants.append({
                                'name': variant['name'],
                                'itemHash': variant['itemHash']
                            })

            # Build updated weapon entry
            updated_weapon = {
                'name': name,
                'itemHash': item_hash,
                'isHolofoil': is_holofoil,
                'holofoilVariants': holofoil_variants
            }

            # Apply perk updates if found
            if perk_entry:
                perk_map = {p['perkName']: p['plugItemHash'] for p in perk_entry.get('perks', [])}
                updated_weapon.update({
                    'column1': update_perk_field(weapon.get('column1', 'None'), perk_map),
                    'column2': update_perk_field(weapon.get('column2', 'None'), perk_map),
                    'originTrait': update_origin_field(weapon.get('originTrait', 'None'), name)
                })
            else:
                updated_weapon.update({
                    'column1': weapon.get('column1', 'None'),
                    'column2': weapon.get('column2', 'None'),
                    'originTrait': update_origin_field(weapon.get('originTrait', 'None'), name)
                })

            updated_data["WeaponPerks"][category].append(updated_weapon)

    # Remove empty categories
    updated_data["WeaponPerks"] = {k: v for k, v in updated_data["WeaponPerks"].items() if v}

    # Save results to JSON file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, indent=4)

if __name__ == "__main__":
    update_perk_hashes()