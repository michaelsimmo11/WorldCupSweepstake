import pandas as pd

def calculate_sweepstake_metrics():
    try:
        # Load core files
        players = pd.read_csv('data/sweepstakeplayers.csv')
        matches = pd.read_csv('data/matches_2026.csv')
        
        # Initialize an explicit stats dictionary for every team in the sweepstake
        teams = players['Team'].unique()
        stats = {
            team: {
                'Team': team,
                'goals_scored': 0,
                'goals_conceded': 0,
                'draws': 0,
                'draw_goals_scored': 0  # Crucial for your draws tie-breaker
            } for team in teams
        }
        
        # 1. Process match-by-match data
        finished_matches = matches[matches['status'] == 'FINISHED']
        
        for _, match in finished_matches.iterrows():
            home, away = match['home_team'], match['away_team']
            h_score = int(match['home_score'] or 0)
            a_score = int(match['away_score'] or 0)
            winner = match['winner']
            
            # Accumulate overall goals
            if home in stats:
                stats[home]['goals_scored'] += h_score
                stats[home]['goals_conceded'] += a_score
            if away in stats:
                stats[away]['goals_scored'] += a_score
                stats[away]['goals_conceded'] += h_score
                
            # Accumulate draw metrics
            if winner == 'DRAW':
                if home in stats:
                    stats[home]['draws'] += 1
                    stats[home]['draw_goals_scored'] += h_score
                if away in stats:
                    stats[away]['draws'] += 1
                    stats[away]['draw_goals_scored'] += a_score
                    
        # Convert stats into a structured DataFrame and merge with player owners
        stats_df = pd.DataFrame.from_dict(stats, orient='index')
        merged = pd.merge(players, stats_df, on='Team', how='left').fillna(0)
        
        # 2. Apply Ironclad Tie-Breakers via Multi-Column Sorting
        
        # Most Goals: Highest goals_scored, then lowest goals_conceded
        most_goals_winner = merged.sort_values(
            by=['goals_scored', 'goals_conceded'], 
            ascending=[False, True]
        ).iloc[0]
        
        # Most Conceded: Highest goals_conceded, then highest goals_scored
        most_conceded_winner = merged.sort_values(
            by=['goals_conceded', 'goals_scored'], 
            ascending=[False, False]
        ).iloc[0]
        
        # Most Draws: Highest draws, then highest goals scored within those drawn games
        most_draws_winner = merged.sort_values(
            by=['draws', 'draw_goals_scored'], 
            ascending=[False, False]
        ).iloc[0]
        
        # 3. Calculate Biggest Upset (Winner Rank - Loser Rank)
        team_to_player = dict(zip(players['Team'], players['Name']))
        team_to_rank = dict(zip(players['Team'], players['FIFA_Rank_(Jun26)']))
        
        biggest_upset_record = None
        max_rank_diff = -999  # Allows tracking even if rank difference is small or negative early on
        
        for _, match in finished_matches.iterrows():
            home, away, winner = match['home_team'], match['away_team'], match['winner']
            
            if home not in team_to_rank or away not in team_to_rank:
                continue
                
            home_rank = team_to_rank[home]
            away_rank = team_to_rank[away]
            
            # Rule: Winner Rank - Loser Rank
            if winner == 'HOME_TEAM':
                diff = home_rank - away_rank
                if diff > max_rank_diff:
                    max_rank_diff = diff
                    biggest_upset_record = {
                        'winner_team': home, 'winner_player': team_to_player[home],
                        'loser_team': away, 'loser_player': team_to_player[away],
                        'score': f"{int(match['home_score'])} - {int(match['away_score'])}",
                        'diff': diff
                    }
            elif winner == 'AWAY_TEAM':
                diff = away_rank - home_rank
                if diff > max_rank_diff:
                    max_rank_diff = diff
                    biggest_upset_record = {
                        'winner_team': away, 'winner_player': team_to_player[away],
                        'loser_team': home, 'loser_player': team_to_player[home],
                        'score': f"{int(match['away_score'])} - {int(match['home_score'])}",
                        'diff': diff
                    }
                    
        return {
            "most_goals": most_goals_winner,
            "most_conceded": most_conceded_winner,
            "most_draws": most_draws_winner,
            "biggest_upset": biggest_upset_record,
            "master_data": merged  # Passed along to keep dashboard tables flawlessly synced
        }
    except Exception as e:
        return None