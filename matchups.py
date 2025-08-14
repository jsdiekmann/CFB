from scraper_package import off_ppg_df, def_ppg_df, matchup_df, off_td_df, def_td_df, to_margin_df
import pandas as pd
import numpy as np

bet_df = pd.DataFrame(columns=["Home Expected Points", "Away Expected Points", "Total Expected Points", "Home TD/TO", "Away TD/TO", "TD/DO Differential"])

for row in matchup_df.itertuples():
    
    home_off_ppg = off_ppg_df.loc[off_ppg_df['Team'] == row[2], '2024']
    home_off_ppg = np.nan if home_off_ppg.empty else home_off_ppg.iloc[0]
    away_def_ppg = def_ppg_df.loc[def_ppg_df['Team'] == row[1], '2024']
    away_def_ppg = np.nan if away_def_ppg.empty else away_def_ppg.iloc[0]
    home_def_ppg = def_ppg_df.loc[def_ppg_df['Team'] == row[2], '2024']
    home_def_ppg = np.nan if home_def_ppg.empty else home_def_ppg.iloc[0]
    away_off_ppg = off_ppg_df.loc[off_ppg_df['Team'] == row[1], '2024']
    away_off_ppg = np.nan if away_off_ppg.empty else away_off_ppg.iloc[0]
    
    home_off_td = off_td_df.loc[off_td_df['Team'] == row[2], '2024']
    home_off_td = np.nan if home_off_td.empty else home_off_td.iloc[0]
    home_def_td = def_td_df.loc[def_td_df['Team'] == row[2], '2024']
    home_def_td = np.nan if home_def_td.empty else home_def_td.iloc[0]
    away_off_td = off_td_df.loc[off_td_df['Team'] == row[1], '2024']
    away_off_td = np.nan if away_off_td.empty else away_off_td.iloc[0]
    away_def_td = def_td_df.loc[def_td_df['Team'] == row[1], '2024']
    away_def_td = np.nan if away_def_td.empty else away_def_td.iloc[0]
    
    home_to_margin = to_margin_df.loc[to_margin_df['Team'] == row[2], '2024']
    home_to_margin = np.nan if home_to_margin.empty else home_to_margin.iloc[0]
    away_to_margin = to_margin_df.loc[to_margin_df['Team'] == row[1], '2024']
    away_to_margin = np.nan if away_to_margin.empty else away_to_margin.iloc[0]

    home_exp_ppg = (home_off_ppg + away_def_ppg) / 2
    home_exp_ppg_text = f"{row[2]}: {home_exp_ppg}"
    away_exp_ppg = (home_def_ppg + away_off_ppg) / 2
    away_exp_ppg_text = f"{row[1]}: {away_exp_ppg}"
    home_td_to = home_off_td - home_def_td + home_to_margin
    away_td_to = away_off_td - away_def_td + away_to_margin

    if (home_td_to > away_td_to):
        to_differential = f"{row[2]}: {(home_td_to - away_td_to):.2f}"
    elif (away_td_to > home_td_to):
        to_differential = f"{row[1]}: {(away_td_to - home_td_to):.2f}"
    else:
        to_differential = 0
    exp_total = home_exp_ppg + away_exp_ppg

    length = len(bet_df)
    bet_df.loc[length] = [home_exp_ppg_text, away_exp_ppg_text, exp_total, home_td_to, away_td_to, to_differential]
print(bet_df)
