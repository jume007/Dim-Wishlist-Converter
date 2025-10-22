import requests
import json
import os
import sys
import importlib.util

# Adjust sys.path to include the parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import API_KEY from _API Key/security.py
security_path = os.path.join(os.path.dirname(__file__), '..', '_API Key', 'security.py')
if not os.path.exists(security_path):
    raise FileNotFoundError(f"security.py not found at {security_path}")

spec = importlib.util.spec_from_file_location("security", security_path)
security = importlib.util.module_from_spec(spec)
sys.modules["security"] = security
spec.loader.exec_module(security)
api_key = security.API_KEY

def export_definition_data():
    # Define relative output directory
    script_dir = os.path.dirname(__file__)
    output_dir = script_dir

    # Download manifest data
    manifest_url = 'https://www.bungie.net/Platform/Destiny2/Manifest/'
    headers = {'X-API-Key': api_key}
    manifest_request = requests.get(manifest_url, headers=headers)
    aggregate_path = manifest_request.json()['Response']['jsonWorldContentPaths']['en']
    aggregate_url = f'https://www.bungie.net{aggregate_path}'
    aggregate_request = requests.get(aggregate_url, headers=headers, timeout=10000)
    data = aggregate_request.json()

    # Save JSON files
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, 'DestinyInventoryItemDefinition.json'), 'w', encoding='utf-8') as f:
        json.dump(data['DestinyInventoryItemDefinition'], f, indent=4)

    with open(os.path.join(output_dir, 'DestinyCollectibleDefinition.json'), 'w', encoding='utf-8') as f:
        json.dump(data['DestinyCollectibleDefinition'], f, indent=4)

    with open(os.path.join(output_dir, 'DestinyPlugSetDefinition.json'), 'w', encoding='utf-8') as f:
        json.dump(data['DestinyPlugSetDefinition'], f, indent=4)

    with open(os.path.join(output_dir, 'DestinySocketTypeDefinition.json'), 'w', encoding='utf-8') as f:
        json.dump(data['DestinySocketTypeDefinition'], f, indent=4)

if __name__ == "__main__":
    export_definition_data()