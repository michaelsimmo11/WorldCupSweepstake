import pandas as pd


class SweepstakeEngine:

    def __init__(self, season=2022):
        self.season = season
        self.team_stats_file = f"data/world_cup_{season}_team_stats.csv"
        self.matches_file = f"data/world_cup_{season}_matches.csv"

    # ----------------------------------
    # Load data
    # ----------------------------------
    def load_data(self):
        stats = pd.read_csv(self.team_stats_file, index_col=0)
        matches = pd.read_csv(self.matches_file)
        return stats, matches

    # ----------------------------------
    # Helper: Safely Extract Team Names
    # ----------------------------------
    def _extract_team_names(self, df_subset):
        """
        Safely extracts team names whether they live in the index 
        or a designated 'team'/'name' column, preventing TypeErrors.
        """
        # Look for a column containing 'team' or 'name'
        team_cols = [col for col in df_subset.columns if 'team' in col.lower() or 'name' in col.lower()]
        
        if team_cols:
            return df_subset[team_cols[0]].astype(str).tolist()
        
        # Fallback to dataframe index, explicitly forcing items to strings
        return df_subset.index.astype(str).tolist()

    # ----------------------------------
    # Tournament Winner
    # ----------------------------------
    def find_champion(self, matches):
        final = matches[matches["round"] == "Final"]
        if len(final) == 0:
            return "No final found"
        final = final.iloc[0]
        return final["winner_actual"]
    
    # ----------------------------------
    # Most Goals Scored (Handles Ties Safely)
    # ----------------------------------
    def most_goals_scored(self, stats):
        max_goals = stats["goals_scored"].max()
        tied_rows = stats[stats["goals_scored"] == max_goals]
        
        tied_teams = self._extract_team_names(tied_rows)
        teams_str = ", ".join(tied_teams)
        return teams_str, max_goals

    # ----------------------------------
    # Most Goals Conceded (Handles Ties Safely)
    # ----------------------------------
    def most_goals_conceded(self, stats):
        max_conceded = stats["goals_conceded"].max()
        tied_rows = stats[stats["goals_conceded"] == max_conceded]
        
        tied_teams = self._extract_team_names(tied_rows)
        teams_str = ", ".join(tied_teams)
        return teams_str, max_conceded

    # ----------------------------------
    # Most Draws (Handles Tie-Breaker Ties Safely)
    # ----------------------------------
    def most_draws(self, stats):
        max_draws = stats["draws"].max()
        tied_rows = stats[stats["draws"] == max_draws]

        # Your rule: Highest scoring team settles tie
        max_goals_among_tied = tied_rows["goals_scored"].max()
        final_rows = tied_rows[tied_rows["goals_scored"] == max_goals_among_tied]
        
        tied_teams = self._extract_team_names(final_rows)
        teams_str = ", ".join(tied_teams)
        return teams_str, max_draws

    # ----------------------------------
    # Biggest Upset
    # ----------------------------------
    def biggest_upset(self, matches):
        if "rank_difference_earned" not in matches.columns or matches["rank_difference_earned"].max() == 0:
            return "No recorded upsets", 0

        max_upset_idx = matches["rank_difference_earned"].idxmax()
        upset_match = matches.loc[max_upset_idx]

        winner = upset_match["winner_actual"]
        loser = upset_match["away_team"] if winner == upset_match["home_team"] else upset_match["home_team"]
        rank_diff = int(upset_match["rank_difference_earned"])

        match_summary = f"{winner} def. {loser}"
        return match_summary, rank_diff

    # ----------------------------------
    # Run
    # ----------------------------------
    def run(self):
        stats, matches = self.load_data()

        champion = self.find_champion(matches)
        top_scorers, goals = self.most_goals_scored(stats)
        worst_defences, conceded = self.most_goals_conceded(stats)
        draw_teams, draws = self.most_draws(stats)
        upset_match, rank_diff = self.biggest_upset(matches)

        print()
        print("=" * 40)
        print("WORLD CUP SWEEPSTAKE")
        print("=" * 40)

        print()
        print(f"£120 Winner:         {champion}")
        print(f"£30 Most Goals:      {top_scorers} ({goals})")
        print(f"£30 Most Conceded:   {worst_defences} ({conceded})")
        print(f"£30 Most Draws:      {draw_teams} ({draws})")
        print(f"£30 Biggest Upset:   {upset_match} (Gap: {rank_diff})")

        print()
        print("=" * 40)


if __name__ == "__main__":
    engine = SweepstakeEngine(season=2022)
    engine.run()