import streamlit as st
import pandas as pd
from metrics import calculate_sweepstake_metrics

st.set_page_config(page_title="World Cup 2026 Sweepstake", page_icon="🏆", layout="wide")

st.title("🏆 World Cup 2026 Sweepstake Hub")

# Establish player identity context 
try:
    players_df = pd.read_csv('data/sweepstakeplayers.csv')
    team_to_player = dict(zip(players_df['Team'], players_df['Name']))
    team_to_rank = dict(zip(players_df['Team'], players_df['FIFA_Rank_(Jun26)']))
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

# --- 2. INTERACTIVE ANALYTICS CHARTS ---
st.header("📊 Sweepstake Analytics")

try:
    team_stats_df = pd.read_csv('data/team_stats_2026.csv')
    matches_df = pd.read_csv('data/matches_2026.csv')
    
    # Create combined display label: "Country (Player)"
    chart_data = pd.merge(players_df, team_stats_df, on='Team', how='left').fillna(0)
    chart_data['Display Label'] = chart_data['Team'] + " (" + chart_data['Name'] + ")"
    
    # Dropdown menu to toggle between the 4 categories
    category_view = st.selectbox(
        "Select Category Leaderboard to Visualize:",
        ["⚽ Most Goals Scored", "🧤 Most Goals Conceded", "🤝 Most 90-Min Draws", "💥 Biggest Upsets Board"]
    )
    
    if category_view == "⚽ Most Goals Scored":
        st.subheader("Top Goalscoring Teams")
        goals_df = chart_data.sort_values(by='goals_scored', ascending=False).head(15)
        # Set index to Display Label so Streamlit automatically uses it for the chart axis
        st.bar_chart(data=goals_df, x='Display Label', y='goals_scored', color="#2ebd59")
        
    elif category_view == "🧤 Most Goals Conceded":
        st.subheader("Leakiest Defenses (Most Conceded)")
        conceded_df = chart_data.sort_values(by='goals_conceded', ascending=False).head(15)
        st.bar_chart(data=conceded_df, x='Display Label', y='goals_conceded', color="#ff4b4b")
        
    elif category_view == "🤝 Most 90-Min Draws":
        st.subheader("Tightly Contested Teams (Most Draws)")
        draws_df = chart_data.sort_values(by='draws', ascending=False).head(15)
        st.bar_chart(data=draws_df, x='Display Label', y='draws', color="#ffaa00")
        
    elif category_view == "💥 Biggest Upsets Board":
        st.subheader("Highest Ranking Differentials in Finished Matches")
        
        finished_matches = matches_df[matches_df['status'] == 'FINISHED'].copy()
        upset_list = []
        
        for _, match in finished_matches.iterrows():
            home, away, winner = match['home_team'], match['away_team'], match['winner']
            
            if home in team_to_rank and away in team_to_rank:
                home_rank = team_to_rank[home]
                away_rank = team_to_rank[away]
                
                # Check for home upset
                if winner == 'HOME_TEAM' and home_rank > away_rank:
                    diff = home_rank - away_rank
                    label = f"{home} ({team_to_player[home]}) def. {away}"
                    upset_list.append({'Matchup': label, 'Rank Difference': diff})
                # Check for away upset
                elif winner == 'AWAY_TEAM' and away_rank > home_rank:
                    diff = away_rank - home_rank
                    label = f"{away} ({team_to_player[away]}) def. {home}"
                    upset_list.append({'Matchup': label, 'Rank Difference': diff})
                    
        if upset_list:
            upset_df = pd.DataFrame(upset_list).sort_values(by='Rank Difference', ascending=False).head(10)
            st.bar_chart(data=upset_df, x='Matchup', y='Rank Difference', color="#7e57c2")
        else:
            st.info("No upsets have occurred yet! This chart will populate when a lower-ranked team wins.")

except FileNotFoundError:
    st.info("Run Ingestion and Transformation files first to build data visuals.")

st.markdown("---")

# --- 3. THE FIXTURE CENTRE ---
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

# --- 4. MASTER SWEEPSTAKE STANDINGS ---
st.header("👥 Participant Leaderboard")
try:
    master_standings = pd.merge(players_df, team_stats_df, on='Team', how='left').fillna(0)
    
    master_standings = master_standings[['Name', 'Team', 'FIFA_Rank_(Jun26)', 'goals_scored', 'goals_conceded', 'draws', 'Paid']]
    master_standings.columns = ['Player Name', 'Assigned Country', 'FIFA Rank', 'Goals For', 'Goals Against', '90-Min Draws', 'Paid Status']
    
    st.dataframe(master_standings.sort_values(by='Goals For', ascending=False), 
                 use_container_width=True, hide_index=True)
except Exception:
    st.dataframe(players_df, use_container_width=True, hide_index=True)