import json
import pandas as pd
import os

def transform_data():
    with open('data/raw_world_cup_2026.json', 'r') as f:
        raw_data = json.load(f)
        
    matches = raw_data.get('matches', [])
    match_list = []
    
    # Base structure
    players_df = pd.read_csv('data/sweepstakeplayers.csv')
    teams = players_df['Team'].unique()
    
    # Base stats dictionary
    team_stats = {team: {'goals_scored': 0, 'goals_conceded': 0, 'draws': 0, 'draw_goals_scored': 0} for team in teams}
    
    for match in matches:
        home_team = (match.get('homeTeam') or {}).get('name', 'Unknown')
        away_team = (match.get('awayTeam') or {}).get('name', 'Unknown')
        status = match.get('status')
        
        # Safely parse scores
        score_data = match.get('score') or {}
        full_time = score_data.get('fullTime') or {}
        regular_time = score_data.get('regularTime') or {}  # Extract 90-min score
        
        h_score_ft = full_time.get('home')
        a_score_ft = full_time.get('away')
        
        # Extract 90 min goals explicitly
        h_score_90 = regular_time.get('home')
        a_score_90 = regular_time.get('away')
        
        winner = score_data.get('winner')
        
        match_info = {
            'match_id': match.get('id'),
            'home_team': home_team,
            'away_team': away_team,
            'status': status,
            'home_score': h_score_ft if status == 'FINISHED' else None,
            'away_score': a_score_ft if status == 'FINISHED' else None,
            'winner': winner if status == 'FINISHED' else None,
            'utcDate': match.get('utcDate')
        }
        match_list.append(match_info)
        
        # Calculate stats strictly for completed games with valid scores
        if status == 'FINISHED' and h_score_ft is not None and a_score_ft is not None:
            h_val_ft, a_val_ft = int(h_score_ft), int(a_score_ft)
            
            # 1. Standard Goals (Uses full time, including ET goals if applicable)
            if home_team in team_stats:
                team_stats[home_team]['goals_scored'] += h_val_ft
                team_stats[home_team]['goals_conceded'] += a_val_ft
            if away_team in team_stats:
                team_stats[away_team]['goals_scored'] += a_val_ft
                team_stats[away_team]['goals_conceded'] += h_val_ft
                
            # 2. THE 90-MINUTE DRAW RULE
            # Fallback to full_time if regular_time is empty (some APIs do this for non-ET games)
            h_val_90 = int(h_score_90) if h_score_90 is not None else h_val_ft
            a_val_90 = int(a_score_90) if a_score_90 is not None else a_val_ft
            
            if h_val_90 == a_val_90:
                if home_team in team_stats:
                    team_stats[home_team]['draws'] += 1
                    team_stats[home_team]['draw_goals_scored'] += h_val_90
                if away_team in team_stats:
                    team_stats[away_team]['draws'] += 1
                    team_stats[away_team]['draw_goals_scored'] += a_val_90
                    
    os.makedirs('data', exist_ok=True)
    pd.DataFrame(match_list).to_csv('data/matches_2026.csv', index=False)
    
    stats_df = pd.DataFrame.from_dict(team_stats, orient='index').reset_index().rename(columns={'index': 'Team'})
    stats_df.to_csv('data/team_stats_2026.csv', index=False)

if __name__ == "__main__":
    transform_data()