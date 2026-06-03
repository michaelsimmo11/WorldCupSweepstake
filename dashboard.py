import streamlit as st
import pandas as pd
import os

# ----------------------------------
# Page Setup
# ----------------------------------
st.set_page_config(page_title="World Cup Sweepstake", page_icon="🏆", layout="wide")
st.title("🏆 World Cup 2022 Sweepstake Dashboard")

# ----------------------------------
# Data Loading & Dynamic Mapping Bridge
# ----------------------------------
@st.cache_data
def load_and_map_data():
    stats_path = "data/team_stats_2022.csv"
    matches_path = "data/matches_2022.csv"
    
    if not os.path.exists(stats_path) or not os.path.exists(matches_path):
        st.error("⚠️ Data files not found! Run your ingestion/transform pipelines first.")
        return None, None

    stats = pd.read_csv(stats_path, index_col=0)
    matches = pd.read_csv(matches_path)
    
    # Clean whitespace from column headers
    stats.columns = stats.columns.str.strip()
    matches.columns = matches.columns.str.strip()

    # DYNAMIC BRIDGE: Build a Team ID -> Team Name dictionary from match history
    id_to_name = {}
    if "home_team_id" in matches.columns and "home_team" in matches.columns:
        id_to_name.update(dict(zip(matches["home_team_id"], matches["home_team"])))
    if "away_team_id" in matches.columns and "away_team" in matches.columns:
        id_to_name.update(dict(zip(matches["away_team_id"], matches["away_team"])))

    # Inject actual names into the stats dataframe using the bridge
    # Checks if IDs live in the index or a dedicated column
    if "team_name" not in stats.columns and "team" not in stats.columns:
        if stats.index.name == "team_id" or stats.index.dtype in ["int64", "int32"]:
            stats["team_name"] = stats.index.map(id_to_name)
        elif "team_id" in stats.columns:
            stats["team_name"] = stats["team_id"].map(id_to_name)
        else:
            # Fallback string conversion if no match is found
            stats["team_name"] = stats.index.astype(str)
    else:
        # If a name column already exists, standardize its header name
        existing_col = "team" if "team" in stats.columns else "team_name"
        stats["team_name"] = stats[existing_col].astype(str)

    # Fill any remaining blank names with their raw string IDs to avoid graphing blanks
    stats["team_name"] = stats["team_name"].fillna(stats.index.to_series().astype(str))
    
    return stats, matches

stats_df, matches_df = load_and_map_data()

# Only render if data loaded successfully
if stats_df is not None and matches_df is not None:

    # ----------------------------------
    # Dynamic Metric Calculations
    # ----------------------------------
    # 1. Tournament Winner
    final_match = matches_df[matches_df["round"] == "Final"]
    champion = final_match.iloc[0]["winner_actual"] if len(final_match) > 0 else "TBD"

    # 2. Most Goals Scored
    max_goals = stats_df["goals_scored"].max()
    top_scorers = ", ".join(stats_df[stats_df["goals_scored"] == max_goals]["team_name"])

    # 3. Most Goals Conceded
    max_conceded = stats_df["goals_conceded"].max()
    worst_defences = ", ".join(stats_df[stats_df["goals_conceded"] == max_conceded]["team_name"])

    # 4. Biggest Upset
    if "rank_difference_earned" in matches_df.columns and matches_df["rank_difference_earned"].max() > 0:
        max_upset_idx = matches_df["rank_difference_earned"].idxmax()
        upset_row = matches_df.loc[max_upset_idx]
        winner = upset_row["winner_actual"]
        loser = upset_row["away_team"] if winner == upset_row["home_team"] else upset_row["home_team"]
        upset_text = f"{winner} def. {loser}"
        upset_gap = f"Gap: {int(upset_row['rank_difference_earned'])}"
    else:
        upset_text = "None"
        upset_gap = "Gap: 0"

    # ----------------------------------
    # Top Level Metrics Display
    # ----------------------------------
    st.header("Prize Winners 💰")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="Tournament Winner (£120)", value=champion)
    with col2:
        st.metric(label="Most Goals (£30)", value=top_scorers, delta=f"{max_goals} Goals")
    with col3:
        st.metric(label="Most Conceded (£30)", value=worst_defences, delta=f"{max_conceded} Goals", delta_color="inverse")
    with col4:
        st.metric(label="Biggest Upset (£30)", value=upset_text, delta=upset_gap)

    st.divider()

    # ----------------------------------
    # Dynamic Bar Chart (With Names)
    # ----------------------------------
    st.header("Team Statistics")

    available_metrics = [col for col in ["goals_scored", "goals_conceded", "draws"] if col in stats_df.columns]
    
    if available_metrics:
        sort_by = st.selectbox("Sort teams by:", available_metrics)
        
        # Sort data frame ahead of plotting
        chart_data = stats_df.sort_values(by=sort_by, ascending=False)
        
        # FIX: Explicitly set x-axis to our mapped team text names and y-axis to chosen metric
        st.bar_chart(data=chart_data, x="team_name", y=sort_by)

    # ----------------------------------
    # Match History Table
    # ----------------------------------
    st.header("Match History")
    desired_cols = ["date", "round", "home_team", "away_team", "winner_actual", "rank_difference_earned"]
    existing_cols = [col for col in desired_cols if col in matches_df.columns]
    
    st.dataframe(matches_df[existing_cols], use_container_width=True)