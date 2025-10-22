import json
import os
import itertools

def normalize_name(name):
    return ''.join(c for c in name.lower() if c.isalnum() or c.isspace()).strip()

def generate_wishlist():
    # Define relative paths
    script_dir = os.path.dirname(__file__)
    input_dir = os.path.join(script_dir, '..', '6th Step Perk Hashes', 'Json')
    output_dir = os.path.join(script_dir, 'Text Files')

    # Get all JSON files in input directory
    input_files = []
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.json') and os.path.isfile(os.path.join(input_dir, file_name)):
            input_files.append(file_name)

    for file_name in input_files:
        input_path = os.path.join(input_dir, file_name)
        # Load category JSON
        with open(input_path, 'r', encoding='utf-8') as f:
            weapon_perks_data = json.load(f)

        # Initialize wishlist entries for this category
        category_entries = []
        category = os.path.splitext(file_name)[0]  # Use JSON filename as category (e.g., 'Swords', 'Other')

        for weapon in weapon_perks_data.get('Weapons', []):
            name = weapon.get('name', '')
            item_hash = weapon.get('itemHash', '')
            column1 = weapon.get('column1', 'None')
            column2 = weapon.get('column2', 'None')
            origin_trait = weapon.get('originTrait', 'None')
            variants = weapon.get('variants', '')
            non_enhanced_hash = weapon.get('nonEnhancedHash', None)
            non_enhanced_type = weapon.get('nonEnhancedType', None)

            if not name or not item_hash:
                continue

            # Parse perks from column1, column2, and originTrait
            def parse_perks(field):
                if field == 'None':
                    return []
                perks = []
                # Split perks carefully to handle commas in hash lists
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

                parsed_perks = []
                for p in perks:
                    if '(' not in p or ')' not in p:
                        continue
                    perk_name = p[:p.rindex('(')].strip()
                    hash_str = p[p.rindex('(')+1:p.rindex(')')].strip()
                    hash_list = [h.strip() for h in hash_str.split(',') if h.strip()]
                    for perk_hash in hash_list:
                        try:
                            parsed_perks.append((perk_name, int(perk_hash)))
                        except ValueError:
                            continue
                return parsed_perks

            column1_perks = parse_perks(column1)
            column2_perks = parse_perks(column2)
            origin_perks = parse_perks(origin_trait)

            # Use nonEnhancedHash as originTrait if originTrait is "None" and nonEnhancedType is "Common Trait"
            if origin_trait == 'None' and non_enhanced_type == 'Common Trait' and non_enhanced_hash:
                origin_perks = [("Unknown Origin", int(non_enhanced_hash))]

            # Generate perk combinations (1/1, 1/2, 1/3, 2/1, 2/2, 2/3, 3/1, 3/2, 3/3)
            combinations = []
            has_combinations = False

            if column1_perks or column2_perks:
                if column1_perks and column2_perks:
                    for p1_count in range(1, min(4, len(column1_perks) + 1)):
                        for p2_count in range(1, min(4, len(column2_perks) + 1)):
                            p1_combos = list(itertools.combinations(column1_perks, p1_count))
                            p2_combos = list(itertools.combinations(column2_perks, p2_count))
                            for p1_combo in p1_combos:
                                for p2_combo in p2_combos:
                                    combinations.append((list(p1_combo), list(p2_combo)))
                                    has_combinations = True
                elif column1_perks:
                    for count in range(1, min(4, len(column1_perks) + 1)):
                        p1_combos = list(itertools.combinations(column1_perks, count))
                        for p1_combo in p1_combos:
                            combinations.append((list(p1_combo), []))
                            has_combinations = True
                elif column2_perks:
                    for count in range(1, min(4, len(column2_perks) + 1)):
                        p2_combos = list(itertools.combinations(column2_perks, count))
                        for p2_combo in p2_combos:
                            combinations.append(([], list(p2_combo)))
                            has_combinations = True

            # List of all item hashes (itemHash + variants)
            item_hashes = [h.strip() for h in item_hash.split(',') if h.strip()]
            if variants:
                item_hashes.extend([h.strip() for h in variants.split(',') if h.strip()])

            # Generate wishlist entries for each item hash
            for item_hash in item_hashes:
                if origin_perks:
                    for origin in origin_perks:
                        for p1_perks, p2_perks in combinations:
                            perk_names = [p[0] for p in p1_perks] + [p[0] for p in p2_perks] + [origin[0]]
                            perk_hashes = [p[1] for p in p1_perks] + [p[1] for p in p2_perks] + [origin[1]]
                            comment = f"//{category}: {name}, {', '.join(perk_names)}"
                            entry = f"dimwishlist:item={item_hash}&perks={','.join(map(str, perk_hashes))}"
                            category_entries.append((name, len(perk_hashes), comment, entry))
                else:
                    for p1_perks, p2_perks in combinations:
                        perk_names = [p[0] for p in p1_perks] + [p[0] for p in p2_perks]
                        perk_hashes = [p[1] for p in p1_perks] + [p[1] for p in p2_perks]
                        if perk_hashes:
                            comment = f"//{category}: {name}, {', '.join(perk_names)}"
                            entry = f"dimwishlist:item={item_hash}&perks={','.join(map(str, perk_hashes))}"
                            category_entries.append((name, len(perk_hashes), comment, entry))

            # Add weapon with no perks if no valid combinations
            if not has_combinations and item_hashes:
                for item_hash in item_hashes:
                    comment = f"//{category}: {name}, No Perks"
                    entry = f"dimwishlist:item={item_hash}"
                    category_entries.append((name, 0, comment, entry))

        # Sort entries by weapon name, then by perk count (descending)
        if category_entries:
            category_entries.sort(key=lambda x: (x[0], -x[1]))
            # Write to category-specific .txt file
            output_filename = f"{category}.txt"
            output_path = os.path.join(output_dir, output_filename)
            os.makedirs(output_dir, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"//{category}:\n")
                for _, _, comment, entry in category_entries:
                    f.write(f"{comment}\n{entry}\n")
                f.write("\n")

if __name__ == "__main__":
    generate_wishlist()