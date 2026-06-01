import pandas as pd


class WorldCupMetrics:

    def __init__(self, season=2022):

        self.season = season

        self.input_file = (
            f"data/world_cup_{season}_matches.csv"
        )

        self.output_file = (
            f"data/world_cup_{season}_team_stats.csv"
        )

    # ----------------------------------
    # LOAD MATCHES
    # ----------------------------------

    def load_matches(self):

        print(f"Loading {self.input_file}")

        return pd.read_csv(self.input_file)

    # ----------------------------------
    # BUILD TEAM STATS (WITH TEAM ID)
    # ----------------------------------

    def build_team_stats(self, matches):

        # Create mapping of teams
        team_lookup = {}

        for _, row in matches.iterrows():

            team_lookup[row["home_team_id"]] = row["home_team"]
            team_lookup[row["away_team_id"]] = row["away_team"]

        team_ids = set(matches["home_team_id"]).union(
            set(matches["away_team_id"])
        )

        stats = pd.DataFrame(index=sorted(team_ids))

        # Basic metrics
        stats["team_name"] = stats.index.map(team_lookup)
        stats["played"] = 0
        stats["wins"] = 0
        stats["draws"] = 0
        stats["goals_scored"] = 0
        stats["goals_conceded"] = 0

        # ----------------------------------
        # LOOP MATCHES
        # ----------------------------------

        for _, match in matches.iterrows():

            home_id = match["home_team_id"]
            away_id = match["away_team_id"]

            hg = match["home_goals"]
            ag = match["away_goals"]

            winner = match["winner_90"]

            # Played
            stats.loc[home_id, "played"] += 1
            stats.loc[away_id, "played"] += 1

            # Goals
            stats.loc[home_id, "goals_scored"] += hg
            stats.loc[home_id, "goals_conceded"] += ag

            stats.loc[away_id, "goals_scored"] += ag
            stats.loc[away_id, "goals_conceded"] += hg

            # Results
            if winner == "draw":

                stats.loc[home_id, "draws"] += 1
                stats.loc[away_id, "draws"] += 1

            elif winner == match["home_team"]:

                stats.loc[home_id, "wins"] += 1

            elif winner == match["away_team"]:

                stats.loc[away_id, "wins"] += 1

        # Goal difference
        stats["goal_difference"] = (
            stats["goals_scored"]
            - stats["goals_conceded"]
        )

        return stats.sort_values(
            by=["wins", "goal_difference"],
            ascending=False
        )

    # ----------------------------------
    # SAVE
    # ----------------------------------

    def save(self, stats):

        stats.to_csv(self.output_file)

        print(f"Saved {self.output_file}")

    # ----------------------------------
    # RUN
    # ----------------------------------

    def run(self):

        matches = self.load_matches()

        stats = self.build_team_stats(matches)

        self.save(stats)

        return stats


# ----------------------------------
# TEST
# ----------------------------------

if __name__ == "__main__":

    metrics = WorldCupMetrics(season=2022)

    team_stats = metrics.run()

    print("\nTOP 10:\n")
    print(team_stats.head(10))