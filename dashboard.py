import streamlit as st
import pandas as pd
import os

# ----------------------------------
# Page Setup
# ----------------------------------
st.set_page_config(page_title="World Cup Sweepstake", page_icon="🏆", layout="wide")
st.title("🏆 World Cup 2022 Sweepstake Dashboard")

# ----------------------------------
# Path-Agnostic Data Loading
# ----------------------------------
@st.cache_data
def load_and_map_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    
    stats_names = ["team_stats_2022.csv", "world_cup_2022_team_stats.csv"]
    matches_names = ["matches_2022.csv", "world_cup_2022_matches.csv"]
    
    stats_path = None
    matches_path = None
    
    if os.path.exists(data_dir):
        for name in stats_names:
            potential_path = os.path.join(data_dir, name)
            if os.path.exists(potential_path):
                stats_path = potential_path
                break
        for name in matches_names:
            potential_path = os.path.join(data_dir, name)
            if os.path.exists(potential_path):
                matches_path = potential_path
                break

    if not stats_path or not matches_path:
        st.error("⚠️ Data files not found!")
        with st.expander("Diagnostic Tool (Click to expand)", expanded=True):
            st.markdown(f"**Dashboard Location:** `{base_dir}`")
            st.markdown(f"**Looking for data folder at:** `{data_dir}`")
            if os.path.exists(data_dir):
                st.success("✅ `data/` folder exists!")
                st.code(os.listdir(data_dir))
            else:
                st.error("❌ The `data/` folder does not exist at that path.")
        return None, None

    stats = pd.read_csv(stats_path, index_col=0)
    matches = pd.read_csv(matches_path)
    
    stats.columns = stats.columns.str.strip()
    matches.columns = matches.columns.str.strip()

    # Build Team ID -> Team Name dictionary
    id_to_name = {}
    if "home_team_id" in matches.columns and "home_team" in matches.columns:
        id_to_name.update(dict(zip(matches["home_team_id"], matches["home_team"])))
    if "away_team_id" in matches.columns and "away_team" in matches.columns:
        id_to_name.update(dict(zip(matches["away_team_id"], matches["away_team"])))

    # Map names to stats dataframe
    if "team_name" not in stats.columns and "team" not in stats.columns:
        if stats.index.name == "team_id" or stats.index.dtype in ["int64", "int32"]:
            stats["team_name"] = stats.index.map(id_to_name)
        elif "team_id" in stats.columns:
            stats["team_name"] = stats["team_id"].map(id_to_name)
        else:
            stats["team_name"] = stats.index.astype(str)
    else:
        existing_col = "team" if "team" in stats.columns else "team_name"
        stats["team_name"] = stats[existing_col].astype(str)

    stats["team_name"] = stats["team_name"].fillna(stats.index.to_series().astype(str))
    
    return stats, matches

stats_df, matches_df = load_and_map_data()

# ----------------------------------
# Render Dashboard UI
# ----------------------------------
if stats_df is not None and matches_df is not None:

    # 1. Calculations
    # Tournament Winner
    final_match = matches_df[matches_df["round"] == "Final"]
    champion = final_match.iloc[0]["winner_actual"] if len(final_match) > 0 else "TBD"

    # Most Goals Scored
    max_goals = stats_df["goals_scored"].max()
    top_scorers = ", ".join(stats_df[stats_df["goals_scored"] == max_goals]["team_name"])

    # Most Goals Conceded
    max_conceded = stats_df["goals_conceded"].max()
    worst_defences = ", ".join(stats_df[stats_df["goals_conceded"] == max_conceded]["team_name"])

    # Most Draws (With your custom Tie-Breaker)
    if "draws" in stats_df.columns:
        max_draws = stats_df["draws"].max()
        tied_draw_rows = stats_df[stats_df["draws"] == max_draws]
        
        # Tie-breaker rule: Highest scoring team settles tie
        max_goals_among_tied = tied_draw_rows["goals_scored"].max()
        final_draw_rows = tied_draw_rows[tied_draw_rows["goals_scored"] == max_goals_among_tied]
        
        draw_teams = ", ".join(final_draw_rows["team_name"])
        draws_delta = f"{max_draws} Draws"
    else:
        draw_teams = "N/A"
        draws_delta = "0 Draws"

    # Biggest Upset
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

    # 2. Display Cards (Updated to 5 Columns)
    st.header("Prize Winners 💰")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(label="Tournament Winner (£120)", value=champion)
    with col2:
        st.metric(label="Most Goals (£30)", value=top_scorers, delta=f"{max_goals} Goals")
    with col3:
        st.metric(label="Most Conceded (£30)", value=worst_defences, delta=f"{max_conceded} Goals", delta_color="inverse")
    with col4:
        st.metric(label="Most Draws (£30)", value=draw_teams, delta=draws_delta)
    with col5:
        st.metric(label="Biggest Upset (£30)", value=upset_text, delta=upset_gap)

    st.divider()

    # 3. Display Chart
    st.header("Team Statistics")
    available_metrics = [col for col in ["goals_scored", "goals_conceded", "draws"] if col in stats_df.columns]
    
    if available_metrics:
        sort_by = st.selectbox("Sort teams by:", available_metrics)
        chart_data = stats_df.sort_values(by=sort_by, ascending=False)
        st.bar_chart(data=chart_data, x="team_name", y=sort_by)

    # 4. Display Table
    st.header("Match History")
    desired_cols = ["date", "round", "home_team", "away_team", "winner_actual", "rank_difference_earned"]
    existing_cols = [col for col in desired_cols if col in matches_df.columns]
    st.dataframe(matches_df[existing_cols], use_container_width=True)