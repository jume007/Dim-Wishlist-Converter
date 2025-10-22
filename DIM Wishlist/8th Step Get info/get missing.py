import os

def extract_items_with_comments(text):
    items = {}
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("dimwishlist:item="):
            # Look for the previous line if it’s a comment
            comment = lines[i-1] if i > 0 and lines[i-1].startswith("//") else ""
            items[line.strip()] = comment
    return items

def find_missing(final_path, ref_path, output_path):
    # Read final wishlist
    with open(final_path, 'r') as f:
        final_text = f.read()
    
    # Read reference wishlist
    with open(ref_path, 'r') as f:
        ref_text = f.read()
    
    # Extract items with their comments
    final_items = extract_items_with_comments(final_text)
    ref_items = extract_items_with_comments(ref_text)
    
    # Find items in final but not in reference
    missing_items = set(final_items.keys()) - set(ref_items.keys())
    
    # Write missing items with their comments to output file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        for item in sorted(missing_items):
            if final_items[item]:  # Write comment if it exists
                f.write(final_items[item] + '\n')
            f.write(item + '\n')
    
    return sorted(missing_items)

# File paths
final_path = os.path.join('7th Step Dimwishlist', 'dimwishlist_final.txt')
ref_path = os.path.join('8th Step Get info', 'reference dimwishlist.txt')
output_path = os.path.join('8th Step Get info', 'updated_missing.txt')

# Run comparison
missing = find_missing(final_path, ref_path, output_path)