import os
import requests
import json  # Ensure json module is imported

# Read API key from .env file
env_path = os.path.join(os.path.dirname(__file__), '.env')
api_key = None
if os.path.exists(env_path):
    with open(env_path, 'r') as env_file:
        for line in env_file:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                if key.strip() == 'API_KEY':
                    api_key = value.strip()
                    break

if not api_key:
    raise ValueError("API_KEY not found in .env file")

def get_bungie_data():
    manifest_url = 'https://www.bungie.net/Platform/Destiny2/Manifest/'
    headers = {'X-API-Key': api_key}
    manifest_request = requests.get(manifest_url, headers=headers)
    if manifest_request.status_code != 200:
        raise Exception(f"Failed to fetch manifest: {manifest_request.status_code} - {manifest_request.text}")
    manifest_json = manifest_request.json()
    print("Manifest structure:", json.dumps(manifest_json, indent=2))  # Debug output
    
    # Extract the aggregate path for 'en' language
    content_paths = manifest_json['Response']['jsonWorldContentPaths']
    if 'en' not in content_paths:
        raise ValueError(f"Language 'en' not found in jsonWorldContentPaths. Available languages: {list(content_paths.keys())}")
    aggregate_path = content_paths['en']
    
    # Fetch the aggregate data
    aggregate_url = f'https://www.bungie.net{aggregate_path}'
    aggregate_request = requests.get(aggregate_url, headers=headers, timeout=10000)
    if aggregate_request.status_code != 200:
        raise Exception(f"Failed to fetch aggregate data: {aggregate_request.status_code} - {aggregate_request.text}")
    aggregate_data = aggregate_request.json()
    
    # Extract DestinyInventoryItemDefinition from the aggregate data
    if 'DestinyInventoryItemDefinition' not in aggregate_data:
        raise ValueError(f"DestinyInventoryItemDefinition not found in aggregate data. Available keys: {list(aggregate_data.keys())}")
    item_data = aggregate_data['DestinyInventoryItemDefinition']
    
    # Save the DestinyInventoryItemDefinition data to a fixed filename
    output_file = 'DestinyInventoryItemDefinition.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(item_data, f, indent=4)
    
    print(f"DestinyInventoryItemDefinition data saved to: {output_file}")
    return item_data

if __name__ == "__main__":
    # Execute the function and print result if run directly
    data = get_bungie_data()
    print(data)