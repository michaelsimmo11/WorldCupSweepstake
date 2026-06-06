import pandas as pd

def calculate_sweepstake_metrics():
    try:
        team_stats = pd.read_csv('data/team_stats_2026.csv')
        matches = pd.read_csv('data/matches_2026.csv')
        # Updated path to the data folder
        players = pd.read_csv('data/sweepstakeplayers.csv')
        
        merged_stats = pd.merge(players, team_stats, on='Team', how='left').fillna(0)
        
        metrics = {
            "most_goals": merged_stats.loc[merged_stats['goals_scored'].idxmax()],
            "most_conceded": merged_stats.loc[merged_stats['goals_conceded'].idxmax()],
            "most_draws": merged_stats.loc[merged_stats['draws'].idxmax()],
            "biggest_upset": None
        }
        
        team_to_player = dict(zip(players['Team'], players['Name']))
        team_to_rank = dict(zip(players['Team'], players['FIFA_Rank_(Jun26)']))
        
        max_rank_diff = 0
        finished_matches = matches[matches['status'] == 'FINISHED']
        
        for _, match in finished_matches.iterrows():
            home, away, winner = match['home_team'], match['away_team'], match['winner']
            
            if home not in team_to_rank or away not in team_to_rank:
                continue
                
            home_rank = team_to_rank[home]
            away_rank = team_to_rank[away]
            
            if winner == 'HOME_TEAM' and (home_rank - away_rank) > max_rank_diff:
                max_rank_diff = home_rank - away_rank
                metrics["biggest_upset"] = {
                    'winner_team': home, 'winner_player': team_to_player[home],
                    'loser_team': away, 'loser_player': team_to_player[away],
                    'score': f"{int(match['home_score'])} - {int(match['away_score'])}",
                    'diff': max_rank_diff
                }
            elif winner == 'AWAY_TEAM' and (away_rank - home_rank) > max_rank_diff:
                max_rank_diff = away_rank - home_rank
                metrics["biggest_upset"] = {
                    'winner_team': away, 'winner_player': team_to_player[away],
                    'loser_team': home, 'loser_player': team_to_player[home],
                    'score': f"{int(match['away_score'])} - {int(match['home_score'])}",
                    'diff': max_rank_diff
                }
                
        return metrics
    except Exception as e:
        return None