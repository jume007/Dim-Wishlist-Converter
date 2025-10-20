import os
import requests
import json

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

def get_plugset_data():
    manifest_url = 'https://www.bungie.net/Platform/Destiny2/Manifest/'
    headers = {'X-API-Key': api_key}
    manifest_request = requests.get(manifest_url, headers=headers)
    if manifest_request.status_code != 200:
        raise Exception(f"Failed to fetch manifest: {manifest_request.status_code} - {manifest_request.text}")
    manifest_json = manifest_request.json()
    
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
    
    # Extract DestinyPlugSetDefinition from the aggregate data
    if 'DestinyPlugSetDefinition' not in aggregate_data:
        raise ValueError(f"DestinyPlugSetDefinition not found in aggregate data. Available keys: {list(aggregate_data.keys())}")
    plugset_data = aggregate_data['DestinyPlugSetDefinition']
    
    # Save the DestinyPlugSetDefinition data to a fixed filename
    output_file = r"E:\Windows\Documents\D2 API\D2 Wishlist\Weapons\DestinyPlugSetDefinition.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(plugset_data, f, indent=4)
    
    return plugset_data

if __name__ == "__main__":
    get_plugset_data()