import streamlit as st
import pandas as pd
from metrics import calculate_sweepstake_metrics

st.set_page_config(page_title="World Cup 2026 Sweepstake", page_icon="🏆", layout="wide")

st.title("🏆 World Cup 2026 Sweepstake Hub")

try:
    players_df = pd.read_csv('data/sweepstakeplayers.csv')
    team_to_player = dict(zip(players_df['Team'], players_df['Name']))
    team_to_rank = dict(zip(players_df['Team'], players_df['FIFA_Rank_(Jun26)']))
except FileNotFoundError:
    st.error("Missing sweepstakeplayers.csv in data/ directory.")
    st.stop()

results = calculate_sweepstake_metrics()

# --- 1. LIVE FINANCIAL PRIZE BOARD ---
st.header("💰 Live Prize Standings")
if results:
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        st.metric("Tournament Winner (£120)", "🏆 TBD")
        st.caption("Paid out post-final match")
        
    with c2:
        mg = results['most_goals']
        st.metric(f"Most Goals (£30): {mg['Name']}", f"{int(mg['goals_scored'])} Goals")
        st.caption(f"Team: **{mg['Team']}** (Conceded: {int(mg['goals_conceded'])})")
        
    with c3:
        mc = results['most_conceded']
        st.metric(f"Most Conceded (£30): {mc['Name']}", f"{int(mc['goals_conceded'])} Goals")
        st.caption(f"Team: **{mc['Team']}** (Scored: {int(mc['goals_scored'])})")
        
    with c4:
        md = results['most_draws']
        st.metric(f"Most Draws (£30): {md['Name']}", f"{int(md['draws'])} Draws")
        st.caption(f"Team: **{md['Team']}** (Goals in draws: {int(md['draw_goals_scored'])})")
        
    with c5:
        u = results['biggest_upset']
        if u:
            st.metric(f"Biggest Upset (£30): {u['winner_player']}", f"+{u['diff']} Diff")
            st.caption(f"**{u['winner_team']}** beat **{u['loser_team']}** ({u['score']})")
        else:
            st.metric("Biggest Upset (£30)", "None Recorded")
            st.caption("Awaiting completed matches...")

st.markdown("---")

# --- 2. INTERACTIVE ANALYTICS CHARTS ---
st.header("📊 Sweepstake Analytics")
if results:
    chart_data = results['master_data'].copy()
    chart_data['Display Label'] = chart_data['Team'] + " (" + chart_data['Name'] + ")"
    
    category_view = st.selectbox(
        "Select Category Leaderboard to Visualize:",
        ["⚽ Most Goals Scored", "🧤 Most Goals Conceded", "🤝 Most 90-Min Draws", "💥 Biggest Upsets Board"]
    )
    
    if category_view == "⚽ Most Goals Scored":
        st.subheader("Top Goalscoring Teams (Tiebreaker: Lowest Conceded)")
        goals_df = chart_data.sort_values(by=['goals_scored', 'goals_conceded'], ascending=[False, True]).head(15)
        st.bar_chart(data=goals_df, x='Display Label', y='goals_scored', color="#2ebd59")
        
    elif category_view == "🧤 Most Goals Conceded":
        st.subheader("Most Goals Conceded (Tiebreaker: Highest Scored)")
        conceded_df = chart_data.sort_values(by=['goals_conceded', 'goals_scored'], ascending=[False, False]).head(15)
        st.bar_chart(data=conceded_df, x='Display Label', y='goals_conceded', color="#ff4b4b")
        
    elif category_view == "🤝 Most 90-Min Draws":
        st.subheader("Most 90-Min Draws (Tiebreaker: Highest Scored in Draws)")
        draws_df = chart_data.sort_values(by=['draws', 'draw_goals_scored'], ascending=[False, False]).head(15)
        st.bar_chart(data=draws_df, x='Display Label', y='draws', color="#ffaa00")
        
    elif category_view == "💥 Biggest Upsets Board":
        st.subheader("Highest Ranking Differentials (Winner Rank - Loser Rank)")
        try:
            matches_df = pd.read_csv('data/matches_2026.csv')
            finished_matches = matches_df[matches_df['status'] == 'FINISHED'].copy()
            upset_list = []
            
            for _, match in finished_matches.iterrows():
                home, away, winner = match['home_team'], match['away_team'], match['winner']
                if home in team_to_rank and away in team_to_rank:
                    if winner == 'HOME_TEAM':
                        diff = team_to_rank[home] - team_to_rank[away]
                        label = f"{home} ({team_to_player[home]}) def. {away}"
                        upset_list.append({'Matchup': label, 'Rank Difference': diff})
                    elif winner == 'AWAY_TEAM':
                        diff = team_to_rank[away] - team_to_rank[home]
                        label = f"{away} ({team_to_player[away]}) def. {home}"
                        upset_list.append({'Matchup': label, 'Rank Difference': diff})
                        
            if upset_list:
                upset_df = pd.DataFrame(upset_list).sort_values(by='Rank Difference', ascending=False).head(10)
                st.bar_chart(data=upset_df, x='Matchup', y='Rank Difference', color="#7e57c2")
            else:
                st.info("No completed matches recorded yet.")
        except Exception:
            st.info("Fixture data loading...")

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
            st.dataframe(upcoming[['Kickoff (UTC)', 'Home Team', 'Away Team', 'status']], use_container_width=True, hide_index=True)
        else:
            st.success("No upcoming fixtures remaining!")

    with tab2:
        if not completed.empty:
            # 💥 FIX 3: Added .fillna(0) so missing API scores don't crash the integer conversion!
            completed['Score'] = completed['home_score'].fillna(0).astype(int).astype(str) + " - " + completed['away_score'].fillna(0).astype(int).astype(str)
            st.dataframe(completed[['Home Team', 'Score', 'Away Team', 'winner']], 
                         use_container_width=True, hide_index=True)
        else:
            st.info("Tournament matches haven't started yet. Results will populate here.")
except FileNotFoundError:
    st.warning("Run ingestion steps to populate data.")

st.markdown("---")

# --- 4. MASTER SWEEPSTAKE STANDINGS ---
st.header("👥 Participant Leaderboard")
if results:
    master_standings = results['master_data'].copy()
    master_standings = master_standings[['Name', 'Team', 'FIFA_Rank_(Jun26)', 'goals_scored', 'goals_conceded', 'draws', 'draw_goals_scored', 'Paid']]
    master_standings.columns = ['Player Name', 'Assigned Country', 'FIFA Rank', 'Goals For', 'Goals Against', '90-Min Draws', 'Goals in Draws', 'Paid Status']
    st.dataframe(master_standings.sort_values(by='Goals For', ascending=False), use_container_width=True, hide_index=True)