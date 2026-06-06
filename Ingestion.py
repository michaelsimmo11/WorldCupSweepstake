import requests
import json
import os

API_KEY = "94df9afd8d1a4c92b2de563647f64f1f"
BASE_URL = 'https://api.football-data.org/v4/competitions/WC/matches'

def fetch_world_cup_data():
    headers = {'X-Auth-Token': API_KEY}
    response = requests.get(BASE_URL, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        # Ensure the data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Save the raw data
        with open('data/raw_world_cup_2026.json', 'w') as f:
            json.dump(data, f, indent=4)
        print("Data successfully ingested!")
    else:
        print(f"Error fetching data: {response.status_code}")

if __name__ == "__main__":
    fetch_world_cup_data()