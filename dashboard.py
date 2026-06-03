import streamlit as st
import pandas as pd

# ----------------------------------
# Page Setup
# ----------------------------------
st.set_page_config(page_title="World Cup Sweepstake", page_icon="🏆", layout="wide")
st.title("🏆 World Cup 2022 Sweepstake Dashboard")

# ----------------------------------
# Load Data
# ----------------------------------
# We use st.cache_data so the app doesn't reload the CSV every time a friend clicks something
@st.cache_data
def load_data():
    stats = pd.read_csv("data/world_cup_2022_team_stats.csv", index_col=0)
    matches = pd.read_csv("data/world_cup_2022_matches.csv")
    return stats, matches

stats_df, matches_df = load_data()

# ----------------------------------
# Top Level Metrics (The Prize Money)
# ----------------------------------
st.header("Prize Winners 💰")
col1, col2, col3, col4 = st.columns(4)

# You can eventually import your SweepstakeEngine here to populate these dynamically!
with col1:
    st.metric(label="Tournament Winner (£120)", value="Argentina")
with col2:
    st.metric(label="Most Goals (£30)", value="France", delta="16 Goals")
with col3:
    st.metric(label="Most Conceded (£30)", value="Costa Rica", delta="-11 Goals", delta_color="inverse")
with col4:
    st.metric(label="Biggest Upset (£30)", value="Saudi Arabia", delta="Gap: 48")

st.divider()

# ----------------------------------
# Interactive Data Views
# ----------------------------------
st.header("Team Statistics")

# Let your friends filter the data!
sort_by = st.selectbox("Sort teams by:", ["goals_scored", "goals_conceded", "draws"])
st.bar_chart(stats_df[sort_by].sort_values(ascending=False))

st.header("Match History")
st.dataframe(matches_df[["date", "round", "home_team", "away_team", "winner_actual", "rank_difference_earned"]])