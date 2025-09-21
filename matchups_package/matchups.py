from CFB.scraper_package.scraper import off_ppg_df, def_ppg_df, matchup_df, off_td_df, def_td_df, to_margin_df
import pandas as pd
import numpy as np

bet_df = pd.DataFrame(columns=["Home", "Expected Points", "TD/TO", "Away", "Expected Points", "TD/TO", "Total Expected Points", "TD/DO Differential"])


team_stats_df = (
    off_ppg_df[["Team", "2025"]].rename(columns={"2025": "Off_PPG"})
    .merge(def_ppg_df[["Team", "2025"]].rename(columns={"2025": "Def_PPG"}), on="Team")
    .merge(off_td_df[["Team", "2025"]].rename(columns={"2025": "Off_TD"}), on="Team")
    .merge(def_td_df[["Team", "2025"]].rename(columns={"2025": "Def_TD"}), on="Team")
    .merge(to_margin_df[["Team", "2025"]].rename(columns={"2025": "TO_Margin"}), on="Team")
)

team_stats_df.set_index('Team', inplace=True)

# --- Step 2: Join matchups with team stats ---
# Prepare home stats
home_stats = team_stats_df.add_prefix('Home_').reset_index().rename(columns={'Team':'Home'})
away_stats = team_stats_df.add_prefix('Away_').reset_index().rename(columns={'Team':'Away'})

matchup_with_stats = matchup_df.merge(home_stats, on='Home').merge(away_stats, on='Away')

# --- Step 3: Compute projections ---
def safe_avg(a, b):
    """Compute average ignoring NaN"""
    return np.nanmean([a, b])

def compute_td_to(off_td, def_td, to_margin):
    """TD/TO metric"""
    return off_td - def_td + to_margin

bet_rows = []

for _, row in matchup_with_stats.iterrows():
    home_exp_ppg = safe_avg(row['Home_Off_PPG'], row['Away_Def_PPG'])
    away_exp_ppg = safe_avg(row['Away_Off_PPG'], row['Home_Def_PPG'])
    favorite = row['Home'] if home_exp_ppg - away_exp_ppg > 0 else row['Away'] if home_exp_ppg - away_exp_ppg < 0 else 'Pick \'em'
    dog = row['Away'] if home_exp_ppg - away_exp_ppg > 0 else row['Home'] if home_exp_ppg - away_exp_ppg < 0 else 'Pick \'em'
    
    home_td_to = compute_td_to(row['Home_Off_TD'], row['Home_Def_TD'], row['Home_TO_Margin'])
    away_td_to = compute_td_to(row['Away_Off_TD'], row['Away_Def_TD'], row['Away_TO_Margin'])
    
    td_diff = home_td_to - away_td_to
    td_to_advantage = row['Home'] if td_diff > 0 else row['Away'] if td_diff < 0 else 'Even'
    
    bet_rows.append({
        "Home": row['Home'],
        "Expected Points (Home)": round(home_exp_ppg, 2),
        "TD/TO (Home)": round(home_td_to, 2),
        "Away": row['Away'],
        "Expected Points (Away)": round(away_exp_ppg, 2),
        "TD/TO (Away)": round(away_td_to, 2),
        "Total Expected Points": round(home_exp_ppg + away_exp_ppg, 2),
        "Expected Spread": round(abs(home_exp_ppg-away_exp_ppg), 2),
        "Favorite": favorite,
        "Underdog": dog,
        "TD/TO Differential": round(abs(td_diff), 2),
        "TD/TO Advantage": td_to_advantage
    })

# --- Step 4: Final DataFrame ---
bet_df = pd.DataFrame(bet_rows)

# for row in matchup_df.itertuples():
#     home = row[2]
#     away = row[1]

#     home_off_ppg = off_ppg_df.loc[off_ppg_df['Team'] == home, '2025']
#     home_off_ppg = np.nan if home_off_ppg.empty else home_off_ppg.iloc[0]
#     away_def_ppg = def_ppg_df.loc[def_ppg_df['Team'] == away, '2025']
#     away_def_ppg = np.nan if away_def_ppg.empty else away_def_ppg.iloc[0]
#     home_def_ppg = def_ppg_df.loc[def_ppg_df['Team'] == home, '2025']
#     home_def_ppg = np.nan if home_def_ppg.empty else home_def_ppg.iloc[0]
#     away_off_ppg = off_ppg_df.loc[off_ppg_df['Team'] == away, '2025']
#     away_off_ppg = np.nan if away_off_ppg.empty else away_off_ppg.iloc[0]
    
#     home_off_td = off_td_df.loc[off_td_df['Team'] == home, '2025']
#     home_off_td = np.nan if home_off_td.empty else home_off_td.iloc[0]
#     home_def_td = def_td_df.loc[def_td_df['Team'] == home, '2025']
#     home_def_td = np.nan if home_def_td.empty else home_def_td.iloc[0]
#     away_off_td = off_td_df.loc[off_td_df['Team'] == away, '2025']
#     away_off_td = np.nan if away_off_td.empty else away_off_td.iloc[0]
#     away_def_td = def_td_df.loc[def_td_df['Team'] == away, '2025']
#     away_def_td = np.nan if away_def_td.empty else away_def_td.iloc[0]
    
#     home_to_margin = to_margin_df.loc[to_margin_df['Team'] == home, '2025']
#     home_to_margin = np.nan if home_to_margin.empty else home_to_margin.iloc[0]
#     away_to_margin = to_margin_df.loc[to_margin_df['Team'] == away, '2025']
#     away_to_margin = np.nan if away_to_margin.empty else away_to_margin.iloc[0]

#     home_exp_ppg = (home_off_ppg + away_def_ppg) / 2
#     home_exp_ppg_text = f"{home_exp_ppg:.2f}"
#     away_exp_ppg = (home_def_ppg + away_off_ppg) / 2
#     away_exp_ppg_text = f"{away_exp_ppg:.2f}"
#     home_td_to = home_off_td - home_def_td + home_to_margin
#     away_td_to = away_off_td - away_def_td + away_to_margin

#     if (home_td_to > away_td_to):
#         to_differential = f"{(home_td_to - away_td_to):.2f} - {home}"
#     elif (away_td_to > home_td_to):
#         to_differential = f"{(away_td_to - home_td_to):.2f} - {away}"
#     else:
#         to_differential = 0
#     exp_total = home_exp_ppg + away_exp_ppg

#     length = len(bet_df)
#     bet_df.loc[length] = [home, home_exp_ppg_text, home_td_to, away, away_exp_ppg_text, away_td_to, exp_total, to_differential]
print(bet_df)

