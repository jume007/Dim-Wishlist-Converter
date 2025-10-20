import requests
import json
import os

from security import API_KEY as api_key

def download_related_json_files():
    # Define relative output directory
    script_dir = os.path.dirname(__file__)
    output_dir = os.path.join(script_dir, '..', 'Weapon Perks')
    
    manifest_url = 'https://www.bungie.net/Platform/Destiny2/Manifest/'
    headers = {'X-API-Key': api_key}
    manifest_request = requests.get(manifest_url, headers=headers)

    aggregate_path = manifest_request.json()['Response']['jsonWorldContentPaths']['en']
    aggregate_url = f'https://www.bungie.net{aggregate_path}'

    print('Getting data from online')
    aggregate_request = requests.get(aggregate_url, headers=headers, timeout=10000)
    data = aggregate_request.json()
    print('Data loaded')
    print()

    # Save JSON files
    os.makedirs(output_dir, exist_ok=True)

    print('Saving Item Definition to file')
    with open(os.path.join(output_dir, 'DestinyInventoryItemDefinition.json'), 'w', encoding='utf-8') as f:
        json.dump(data['DestinyInventoryItemDefinition'], f, indent=4)
        print('Saved Item Definition')
    print()

    print('Saving Collectible Definition to file')
    with open(os.path.join(output_dir, 'DestinyCollectibleDefinition.json'), 'w', encoding='utf-8') as f:
        json.dump(data['DestinyCollectibleDefinition'], f, indent=4)
        print('Saved Collectible Definition')
    print()

    print('Saving Plug Set Definition to file')
    with open(os.path.join(output_dir, 'DestinyPlugSetDefinition.json'), 'w', encoding='utf-8') as f:
        json.dump(data['DestinyPlugSetDefinition'], f, indent=4)
        print('Saved Plug Set Definition')
    print()

    print('Saving Socket Type Definition to file')
    with open(os.path.join(output_dir, 'DestinySocketTypeDefinition.json'), 'w', encoding='utf-8') as f:
        json.dump(data['DestinySocketTypeDefinition'], f, indent=4)
        print('Saved Socket Type Definition')
    print()

if __name__ == "__main__":
    download_related_json_files()