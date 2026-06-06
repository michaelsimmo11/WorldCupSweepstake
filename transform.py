import json
import pandas as pd
import os

def transform_data():
    with open('data/raw_world_cup_2026.json', 'r') as f:
        raw_data = json.load(f)
        
    matches = raw_data.get('matches', [])
    match_list = []
    
    # Updated path to the data folder
    players_df = pd.read_csv('data/sweepstakeplayers.csv')
    teams = players_df['Team'].unique()
    team_stats = {team: {'goals_scored': 0, 'goals_conceded': 0, 'draws': 0} for team in teams}
    
    for match in matches:
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        status = match['status']
        
        match_info = {
            'match_id': match['id'],
            'home_team': home_team,
            'away_team': away_team,
            'status': status,
            'home_score': match['score']['fullTime']['home'] if status == 'FINISHED' else None,
            'away_score': match['score']['fullTime']['away'] if status == 'FINISHED' else None,
            'winner': match['score']['winner'] if status == 'FINISHED' else None,
            'utcDate': match['utcDate']
        }
        match_list.append(match_info)
        
        if status == 'FINISHED':
            h_score = int(match_info['home_score'] or 0)
            a_score = int(match_info['away_score'] or 0)
            
            if home_team in team_stats:
                team_stats[home_team]['goals_scored'] += h_score
                team_stats[home_team]['goals_conceded'] += a_score
            if away_team in team_stats:
                team_stats[away_team]['goals_scored'] += a_score
                team_stats[away_team]['goals_conceded'] += h_score
                
            if match_info['winner'] == 'DRAW':
                if home_team in team_stats:
                    team_stats[home_team]['draws'] += 1
                if away_team in team_stats:
                    team_stats[away_team]['draws'] += 1
                    
    os.makedirs('data', exist_ok=True)
    pd.DataFrame(match_list).to_csv('data/matches_2026.csv', index=False)
    
    stats_df = pd.DataFrame.from_dict(team_stats, orient='index').reset_index().rename(columns={'index': 'Team'})
    stats_df.to_csv('data/team_stats_2026.csv', index=False)
    print("Data structures updated successfully.")

if __name__ == "__main__":
    transform_data()