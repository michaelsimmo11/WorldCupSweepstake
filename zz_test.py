import requests

# 1. Define your API key and headers
# Replace 'YOUR_API_KEY_HERE' with your actual API-Football token
API_KEY = "fb754d332cf4c51c9940300fe4b20398"

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "v3.football.api-sports.io"
}

# 2. Define the parameters specified in the API-Sports guide
# league=1 represents the FIFA World Cup, and season=2026 covers the 2026 edition.
url = "https://v3.football.api-sports.io/fixtures"
params = {
    "league": "1",
    "season": "2026"
}

try:
    # 3. Make the GET request
    print("Fetching World Cup 2026 fixtures from API-Sports...")
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()  # Check for HTTP request errors
    
    data = response.json()
    
    # Check if the API returned an error message in its body
    if data.get("errors"):
        print("API Error:", data["errors"])
    else:
        fixtures = data.get("response", [])
        print(f"Successfully retrieved {len(fixtures)} fixtures.\n")
        
        # 4. Loop through and print the match details
        for fixture_data in fixtures:
            fixture_info = fixture_data.get("fixture", {})
            league_info = fixture_data.get("league", {})
            teams = fixture_data.get("teams", {})
            goals = fixture_data.get("goals", {})
            
            # Extract relevant details
            match_id = fixture_info.get("id")
            match_date = fixture_info.get("date")  # Returned in UTC format
            stage = league_info.get("round")       # E.g., "Group Stage - 1" or "Round of 32"
            venue = fixture_info.get("venue", {}).get("name", "Unknown Venue")
            city = fixture_info.get("venue", {}).get("city", "Unknown City")
            
            home_team = teams.get("home", {}).get("name", "TBD")
            away_team = teams.get("away", {}).get("name", "TBD")
            
            home_goals = goals.get("home")
            away_goals = goals.get("away")
            
            # Format score if the match has already been played or is live
            score_str = f"{home_goals} - {away_goals}" if home_goals is not None else "vs"
            
            print(f"ID: {match_id} | Stage: {stage}")
            print(f"Date (UTC): {match_date} | Location: {venue}, {city}")
            print(f"Match: {home_team} {score_str} {away_team}")
            print("-" * 50)

except requests.exceptions.RequestException as e:
    print(f"An error occurred while making the request: {e}")