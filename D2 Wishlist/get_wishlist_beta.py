import json
import os
import re
import itertools

def normalize_name(name):
    return ''.join(c for c in name.lower() if c.isalnum() or c.isspace()).strip()

def generate_wishlist():
    # Define file paths
    script_dir = os.path.dirname(__file__)
    weapon_perks_path = os.path.join(script_dir, '..', 'Weapon Perks', 'weapon_perks_final.json')
    output_dir = os.path.join(script_dir, '..', 'D2 Wishlist')
    output_path = os.path.join(output_dir, 'wishlist.txt')

    # Load JSON file
    with open(weapon_perks_path, 'r', encoding='utf-8') as f:
        weapon_perks_data = json.load(f)

    # Initialize wishlist entries
    wishlist_entries = []

    # Process each category in weapon_perks_final.json
    for category in sorted(weapon_perks_data.get('WeaponPerks', {}).keys()):
        category_entries = []
        for weapon in weapon_perks_data['WeaponPerks'][category]:
            name = weapon['name']
            item_hash = str(weapon['itemHash'])
            column1 = weapon.get('column1', 'None')
            column2 = weapon.get('column2', 'None')
            origin_trait = weapon.get('originTrait', 'None')

            # Parse perks from column1, column2, and originTrait
            def parse_perks(field):
                if field == 'None':
                    return []
                perks = []
                for p in field.split(','):
                    match = re.match(r'(.+)\s*\((\d+)\)', p.strip())
                    if match:
                        perk_name, perk_hash = match.groups()
                        perks.append((perk_name.strip(), int(perk_hash)))
                    else:
                        perks.append((p.strip(), None))
                return [p for p in perks if p[1] is not None]  # Only include perks with hashes

            column1_perks = parse_perks(column1)
            column2_perks = parse_perks(column2)
            origin_perks = parse_perks(origin_trait)

            # Generate perk combinations (1-3 perks per column)
            combinations = []
            has_combinations = False

            # Handle cases where at least one column has valid perks
            if column1_perks or column2_perks:
                for p1_count in ([1, 2, 3] if column1_perks else [0]):
                    for p2_count in ([1, 2, 3] if column2_perks else [0]):
                        p1_combos = (itertools.combinations(column1_perks, p1_count) if p1_count > 0 else [()])
                        p2_combos = (itertools.combinations(column2_perks, p2_count) if p2_count > 0 else [()])
                        for p1_combo in p1_combos:
                            for p2_combo in p2_combos:
                                if p1_combo or p2_combo:  # Ensure at least one perk
                                    combinations.append((list(p1_combo), list(p2_combo)))
                                    has_combinations = True

            # Generate wishlist entries
            for p1_perks, p2_perks in combinations:
                if origin_perks:
                    for origin in origin_perks:
                        perk_names = [p[0] for p in p1_perks] + [p[0] for p in p2_perks] + [origin[0]]
                        perk_hashes = [p[1] for p in p1_perks] + [p[1] for p in p2_perks] + [origin[1]]
                        comment = f"//{name}, {', '.join(perk_names)}"
                        entry = f"dimwishlist:item={item_hash}&perks={','.join(map(str, perk_hashes))}"
                        category_entries.append((name, len(perk_hashes), comment, entry))
                else:
                    perk_names = [p[0] for p in p1_perks] + [p[0] for p in p2_perks]
                    perk_hashes = [p[1] for p in p1_perks] + [p[1] for p in p2_perks]
                    if perk_hashes:  # Only add if there are valid perks
                        comment = f"//{name}, {', '.join(perk_names)}"
                        entry = f"dimwishlist:item={item_hash}&perks={','.join(map(str, perk_hashes))}"
                        category_entries.append((name, len(perk_hashes), comment, entry))

            # Add weapon with no perks if no valid combinations
            if not has_combinations:
                comment = f"//{name}, No Perks"
                entry = f"dimwishlist:item={item_hash}"
                category_entries.append((name, 0, comment, entry))

        # Sort entries by weapon name, then by perk count (descending)
        if category_entries:
            category_entries.sort(key=lambda x: (x[0], -x[1]))
            wishlist_entries.append((category, category_entries))

    # Write to wishlist.txt
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for category, entries in wishlist_entries:
            f.write(f"//{category}:\n")
            for _, _, comment, entry in entries:
                f.write(f"{comment}\n{entry}\n")
            f.write("\n")

if __name__ == "__main__":
    generate_wishlist()