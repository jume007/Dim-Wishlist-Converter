import json
import os

def find_missing_perks():
    # Define relative paths
    script_dir = os.path.dirname(__file__)
    input_dir = os.path.join(script_dir, 'Json')
    output_dir = os.path.join(script_dir, 'testing')
    output_path = os.path.join(output_dir, 'missingperks.json')

    # Get all JSON files in input directory
    input_files = []
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.json') and os.path.isfile(os.path.join(input_dir, file_name)):
            input_files.append(file_name)

    # Initialize list for weapons with missing perk hashes
    missing_perk_weapons = []

    for file_name in input_files:
        input_path = os.path.join(input_dir, file_name)
        # Load category JSON
        with open(input_path, 'r', encoding='utf-8') as f:
            category_data = json.load(f)

        for weapon in category_data.get('Weapons', []):
            weapon_name = weapon.get('name', '')
            if not weapon_name:
                continue

            # Check column1 and column2 for perks without hashes
            has_missing_perk = False
            for field in [weapon.get('column1', 'None'), weapon.get('column2', 'None')]:
                if field == 'None':
                    continue
                # Split perks, preserving commas in hash lists
                perks = []
                current_perk = ''
                paren_count = 0
                for char in field:
                    if char == ',' and paren_count == 0:
                        if current_perk.strip():
                            perks.append(current_perk.strip())
                        current_perk = ''
                    else:
                        current_perk += char
                        if char == '(':
                            paren_count += 1
                        elif char == ')':
                            paren_count -= 1
                if current_perk.strip():
                    perks.append(current_perk.strip())

                # Check each perk for missing hash
                for perk in perks:
                    if '(' not in perk or ')' not in perk:
                        has_missing_perk = True
                        break
                    hash_str = perk[perk.rindex('(')+1:perk.rindex(')')].strip()
                    if not hash_str or not all(h.strip().isdigit() for h in hash_str.split(',')):
                        has_missing_perk = True
                        break
                if has_missing_perk:
                    break

            # If missing perk hashes, add weapon to list
            if has_missing_perk:
                updated_weapon = weapon.copy()
                updated_weapon = {k: v for k, v in updated_weapon.items() if v is not None and (k != 'variants' or v)}
                missing_perk_weapons.append(updated_weapon)

    # Save to missingperks.json
    if missing_perk_weapons:
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({"Weapons": missing_perk_weapons}, f, indent=4)

if __name__ == "__main__":
    find_missing_perks()