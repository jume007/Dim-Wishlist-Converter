import os
from collections import defaultdict

def parse_wishlist(text):
    # Group entries by weapon hash and collect comments
    entries = defaultdict(list)
    current_comment = ""
    lines = text.splitlines()
    
    for i, line in enumerate(lines):
        if line.startswith("//"):
            current_comment = line
        elif line.startswith("dimwishlist:item="):
            if current_comment:
                # Extract weapon hash and perks
                parts = line.split("&perks=")
                item_hash = parts[0].replace("dimwishlist:item=", "")
                # Check if perks exist
                if len(parts) > 1 and parts[1].strip():
                    perks = parts[1].split(",")
                    entries[item_hash].append((current_comment, line, perks))
                else:
                    # Log invalid line (optional: print for debugging)
                    print(f"Skipping invalid line: {line}")
    
    return entries

def compile_entries(entries):
    compiled = []
    
    for item_hash, items in entries.items():
        # Extract weapon name from the first comment
        first_comment = items[0][0]
        weapon_name = first_comment.split(":")[1].split(",")[0].strip()
        
        # Collect all unique perks across all entries for this hash
        all_perks = set()
        for _, _, perks in items:
            all_perks.update(perks)
        
        # Create a comment with all unique perks
        perk_names = []
        for _, comment, _ in items:
            if comment.startswith("//Fusions:") or comment.startswith("//Bows:") or comment.startswith("//HCs:") or comment.startswith("//Rockets:") or comment.startswith("//LFRs:"):
                perk_part = comment.split(",", 1)[1].strip()
                perk_names.extend([p.strip() for p in perk_part.split(",")])
        perk_names = sorted(set(perk_names))  # Remove duplicates and sort
        
        # Generate compiled comment
        compiled_comment = f"//{weapon_name}, {', '.join(perk_names)}"
        
        # Sort items by number of perks (descending) and remove duplicates
        unique_items = []
        seen_perks = set()
        for comment, line, perks in sorted(items, key=lambda x: len(x[2]), reverse=True):
            perk_str = ",".join(perks)
            if perk_str not in seen_perks:
                unique_items.append((comment, line, perks))
                seen_perks.add(perk_str)
        
        # Add compiled comment followed by unique item lines
        compiled.append(compiled_comment)
        for _, line, _ in unique_items:
            compiled.append(line)
    
    return compiled

def compile_wishlist(input_path, output_path):
    # Read input wishlist
    with open(input_path, 'r') as f:
        text = f.read()
    
    # Parse and compile entries
    entries = parse_wishlist(text)
    compiled_lines = compile_entries(entries)
    
    # Write to output file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        for line in compiled_lines:
            f.write(line + '\n')

# File paths
input_path = os.path.join('8th Step Get info', 'updated_missing.txt')
output_path = os.path.join('8th Step Get info', 'compiled_wishlist.txt')

# Run compilation
compile_wishlist(input_path, output_path)