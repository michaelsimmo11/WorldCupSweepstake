import streamlit as st
import pandas as pd
from metrics import calculate_sweepstake_metrics

st.set_page_config(page_title="World Cup 2026 Sweepstake", page_icon="🏆", layout="wide")

st.title("🏆 World Cup 2026 Sweepstake Hub")

# Updated path to the data folder
try:
    players_df = pd.read_csv('data/sweepstakeplayers.csv')
    team_to_player = dict(zip(players_df['Team'], players_df['Name']))
except FileNotFoundError:
    st.error("Missing sweepstakeplayers.csv in data/ directory.")
    st.stop()

metrics = calculate_sweepstake_metrics()

# --- 1. LIVE FINANCIAL PRIZE BOARD ---
st.header("💰 Live Prize Standings")
if metrics:
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        st.metric("Tournament Winner (£120)", "🏆 TBD")
        st.caption("Paid out post-final match")
    with c2:
        st.metric(f"Most Goals (£30): {metrics['most_goals']['Name']}", f"{metrics['most_goals']['goals_scored']} Gls")
        st.caption(f"Team: **{metrics['most_goals']['Team']}**")
    with c3:
        st.metric(f"Most Conceded (£30): {metrics['most_conceded']['Name']}", f"{metrics['most_conceded']['goals_conceded']} Gls")
        st.caption(f"Team: **{metrics['most_conceded']['Team']}**")
    with c4:
        st.metric(f"Most Draws (£30): {metrics['most_draws']['Name']}", f"{metrics['most_draws']['draws']} Draws")
        st.caption(f"Team: **{metrics['most_draws']['Team']}**")
    with c5:
        u = metrics['biggest_upset']
        if u:
            st.metric(f"Biggest Upset (£30): {u['winner_player']}", f"+{u['diff']} Rank Diff")
            st.caption(f"**{u['winner_team']}** beat **{u['loser_team']}** ({u['score']})")
        else:
            st.metric("Biggest Upset (£30)", "None Recorded")
            st.caption("Awaiting unexpected results...")

st.markdown("---")

# --- 2. THE FIXTURE CENTRE ---
st.header("📅 Matchday Hub")
try:
    matches_df = pd.read_csv('data/matches_2026.csv')
    
    matches_df['home_p'] = matches_df['home_team'].map(team_to_player).fillna("Unknown")
    matches_df['away_p'] = matches_df['away_team'].map(team_to_player).fillna("Unknown")
    
    matches_df['Home Team'] = matches_df['home_team'] + " (" + matches_df['home_p'] + ")"
    matches_df['Away Team'] = matches_df['away_team'] + " (" + matches_df['away_p'] + ")"
    
    upcoming = matches_df[matches_df['status'] != 'FINISHED'].copy()
    completed = matches_df[matches_df['status'] == 'FINISHED'].copy()
    
    tab1, tab2 = st.tabs(["🔮 Upcoming Fixtures", "✅ Recent Results"])
    
    with tab1:
        if not upcoming.empty:
            upcoming['Kickoff (UTC)'] = pd.to_datetime(upcoming['utcDate']).dt.strftime('%m-%d %H:%M')
            st.dataframe(upcoming[['Kickoff (UTC)', 'Home Team', 'Away Team', 'status']], 
                         use_container_width=True, hide_index=True)
        else:
            st.success("No upcoming fixtures left scheduled!")
            
    with tab2:
        if not completed.empty:
            completed['Score'] = completed['home_score'].astype(int).astype(str) + " - " + completed['away_score'].astype(int).astype(str)
            st.dataframe(completed[['Home Team', 'Score', 'Away Team', 'winner']], 
                         use_container_width=True, hide_index=True)
        else:
            st.info("Tournament matches haven't started yet. Results will populate here.")
except FileNotFoundError:
    st.warning("Run Ingestion and Transformation steps to populate live schedules.")

st.markdown("---")

# --- 3. MASTER SWEEPSTAKE STANDINGS ---
st.header("👥 Participant Leaderboard")
try:
    team_stats_df = pd.read_csv('data/team_stats_2026.csv')
    master_standings = pd.merge(players_df, team_stats_df, on='Team', how='left').fillna(0)
    
    master_standings = master_standings[['Name', 'Team', 'FIFA_Rank_(Jun26)', 'goals_scored', 'goals_conceded', 'draws', 'Paid']]
    master_standings.columns = ['Player Name', 'Assigned Country', 'FIFA Rank', 'Goals For', 'Goals Against', '90-Min Draws', 'Paid Status']
    
    st.dataframe(master_standings.sort_values(by='Goals For', ascending=False), 
                 use_container_width=True, hide_index=True)
except Exception:
    st.dataframe(players_df, use_container_width=True, hide_index=True)