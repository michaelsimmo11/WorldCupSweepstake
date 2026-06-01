import json
import os
import pandas as pd
from rapidfuzz import process, utils


class WorldCupTransformer:

    def __init__(self, season=2022):
        self.season = season
        self.raw_file = f"data/world_cup_{season}_raw.json"
        self.output_file = f"data/world_cup_{season}_matches.csv"
        self.ranking_file = f"data/FIFA Ranking.csv"

    def load_data(self):
        print(f"Loading {self.raw_file}")
        with open(self.raw_file, "r", encoding="utf-8") as file:
            return json.load(file)

    def load_fifa_rankings(self):
        print(f"Loading FIFA rankings from {self.ranking_file}...")
        if not os.path.exists(self.ranking_file):
            print(f"Warning: {self.ranking_file} not found. Proceeding without rankings.")
            return {}
            
        try:
            df_rank = pd.read_csv(self.ranking_file)
            rank_col, team_col = None, None
            
            for col in df_rank.columns:
                col_lower = col.strip().lower()
                if "rank" in col_lower:
                    rank_col = col
                elif any(keyword in col_lower for keyword in ["team", "country", "nation", "association"]):
                    team_col = col
            
            if not rank_col or not team_col:
                rank_col = df_rank.columns[0]
                team_col = df_rank.columns[1]
                
            rankings = {}
            for _, row in df_rank.dropna(subset=[rank_col, team_col]).iterrows():
                try:
                    rank_val = int(''.join(filter(str.isdigit, str(row[rank_col]))))
                    team_val = str(row[team_col]).strip()
                    rankings[team_val] = rank_val
                except ValueError:
                    continue
            return rankings
        except Exception as e:
            print(f"Error reading CSV file: {e}.")
            return {}

    def get_closest_rank(self, team_name, rankings_dict):
        if not rankings_dict:
            return None
        if team_name in rankings_dict:
            return rankings_dict[team_name]
        
        choices = list(rankings_dict.keys())
        match = process.extractOne(team_name, choices, processor=utils.default_process)
        if match and match[1] > 70:
            return rankings_dict[match[0]]
        return None

    # ----------------------------------
    # Transform fixtures
    # ----------------------------------
    def transform(self):
        fixtures = self.load_data()
        rankings = self.load_fifa_rankings()
        rows = []

        for fixture in fixtures:
            status = fixture["fixture"]["status"]["short"]
            if status not in ["FT", "AET", "PEN"]:
                continue

            # TEAMS
            home_team_id = fixture["teams"]["home"]["id"]
            home_team = fixture["teams"]["home"]["name"]
            away_team_id = fixture["teams"]["away"]["id"]
            away_team = fixture["teams"]["away"]["name"]

            # Match Rankings
            home_rank = self.get_closest_rank(home_team, rankings)
            away_rank = self.get_closest_rank(away_team, rankings)

            # SCORES & FLAGS
            home_goals = fixture["goals"]["home"]
            away_goals = fixture["goals"]["away"]
            went_to_extra_time = fixture["score"]["extratime"]["home"] is not None
            went_to_penalties = fixture["score"]["penalty"]["home"] is not None

            # ACTUAL WINNER
            home_winner_flag = fixture["teams"]["home"]["winner"]
            away_winner_flag = fixture["teams"]["away"]["winner"]

            if home_winner_flag:
                winner_actual = home_team
            elif away_winner_flag:
                winner_actual = away_team
            else:
                winner_actual = "draw"

            # 90-MIN RULE
            if went_to_extra_time or went_to_penalties:
                winner_90 = "draw"
            elif home_goals > away_goals:
                winner_90 = home_team
            elif away_goals > home_goals:
                winner_90 = away_team
            else:
                winner_90 = "draw"

            # -------------------------------------------------------
            # NEW RULE: RANK DIFFERENTIAL CALCULATION
            # -------------------------------------------------------
            rank_difference_earned = 0
            
            # Ensure both teams have a valid rank tracked from the CSV
            if home_rank is not None and away_rank is not None:
                # INTERPRETATION A: Numerically lower rank wins (The Favorite wins, e.g., Rank 3 beats Rank 15)
                # Note: To switch this to INTERPRETATION B (The Underdog wins, e.g., Rank 15 beats Rank 3), 
                # simply change the '<' symbols to '>' symbols below.
                if winner_actual == home_team and home_rank > away_rank:
                    rank_difference_earned = abs(home_rank - away_rank)
                elif winner_actual == away_team and away_rank > home_rank:
                    rank_difference_earned = abs(home_rank - away_rank)

            # -----------------------
            # STORE ROW
            # -----------------------
            rows.append({
                "fixture_id": fixture["fixture"]["id"],
                "date": fixture["fixture"]["date"],
                "round": fixture["league"]["round"],

                "home_team_id": home_team_id,
                "home_team": home_team,
                "home_fifa_rank": home_rank,
                
                "away_team_id": away_team_id,
                "away_team": away_team,
                "away_fifa_rank": away_rank,

                "home_goals": home_goals,
                "away_goals": away_goals,

                "winner_90": winner_90,
                "winner_actual": winner_actual,
                
                # New output column
                "rank_difference_earned": rank_difference_earned,

                "went_to_extra_time": went_to_extra_time,
                "went_to_penalties": went_to_penalties
            })

        return pd.DataFrame(rows)

    def save(self, df):
        df.to_csv(self.output_file, index=False)
        print(f"Saved {self.output_file}")

    def run(self):
        df = self.transform()
        self.save(df)
        return df


# ----------------------------------
# TEST
# ----------------------------------
if __name__ == "__main__":
    transformer = WorldCupTransformer(season=2022)
    matches = transformer.run()

    print("\nPreview of Rank Rule:\n")
    if not matches.empty and "rank_difference_earned" in matches.columns:
        print(matches[["home_team", "home_fifa_rank", "away_team", "away_fifa_rank", "winner_actual", "rank_difference_earned"]].head(10))
    
    print(f"\nMatches loaded: {len(matches)}")