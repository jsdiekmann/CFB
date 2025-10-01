from bs4 import BeautifulSoup
import requests
import pandas as pd
import re

# Need to create data frame of stat tables and then use those to make comparisons so we are not scraping every time

# Average of Team A points/game and Team B points allowed/game and vice versa

matchup_url = "https://www.teamrankings.com/ncf/schedules/season/?week=1272"
off_ppg_url = "https://www.teamrankings.com/college-football/stat/points-per-game"
off_td_url = "https://www.teamrankings.com/college-football/stat/offensive-touchdowns-per-game"
def_ppg_url = "https://www.teamrankings.com/college-football/stat/opponent-points-per-game"
def_td_url = "https://www.teamrankings.com/college-football/stat/opponent-offensive-touchdowns-per-game"
to_margin_url = "https://www.teamrankings.com/college-football/stat/turnover-margin-per-game"

try:
    matchup_page = requests.get(matchup_url)
    off_ppg_page = requests.get(off_ppg_url)
    off_td_page = requests.get(off_td_url)
    def_ppg_page = requests.get(def_ppg_url)
    def_td_page = requests.get(def_td_url)
    to_margin_page = requests.get(to_margin_url)
    
except requests.RequestException as e:
    print(f"Error retrieving {e}")

matchup_soup = BeautifulSoup(matchup_page.text, "html.parser")
off_ppg_soup = BeautifulSoup(off_ppg_page.text, "html.parser")
off_td_soup = BeautifulSoup(off_td_page.text, "html.parser")
def_ppg_soup = BeautifulSoup(def_ppg_page.text, "html.parser")
def_td_soup = BeautifulSoup(def_td_page.text, "html.parser")
to_margin_soup = BeautifulSoup(to_margin_page.text, "html.parser")

# Fetches and assigns home team and away team for search of 
matchup_titles = ["Away", "Home"]
matchup_df = pd.DataFrame(columns=matchup_titles)
matchup_data = matchup_soup.find_all('tr')
for row in matchup_data:
    cols = row.find_all('td')
    if not cols:
        continue
    matchup = cols[0].get_text(strip=True)
    matchup_array = re.split(r'(?:@|vs\.)', matchup)
    home_team = matchup_array[1].strip()
    away_team = matchup_array[0].strip()
    teams = [away_team, home_team]
    length = len(matchup_df)
    matchup_df.loc[length] = teams

    
# Creates a dataframe from the Offense PPG table
off_ppg_titles_obj = off_ppg_soup.find_all('th')
off_ppg_titles = [title.text for title in off_ppg_titles_obj]
off_ppg_df = pd.DataFrame(columns = off_ppg_titles)
off_ppg_column_data = off_ppg_soup.find_all('tr')

for row in off_ppg_column_data[1:]:
    row_data = row.find_all('td')
    row_data_info = [info.text.strip() for info in row_data]
    
    length = len(off_ppg_df)
    if row_data_info[2] != '--':
        off_ppg_df.loc[length] = row_data_info
    
off_ppg_df['2025'] = pd.to_numeric(off_ppg_df['2025'])

# Creates a dataframe from the Defense PPG table
def_ppg_titles_obj = def_ppg_soup.find_all('th')
def_ppg_titles = [title.text for title in def_ppg_titles_obj]
def_ppg_df = pd.DataFrame(columns = def_ppg_titles)
def_ppg_column_data = def_ppg_soup.find_all('tr')

for row in def_ppg_column_data[1:]:
    row_data = row.find_all('td')
    row_data_info = [info.text.strip() for info in row_data]
    
    length = len(def_ppg_df)
    if row_data_info[2] != '--':
        def_ppg_df.loc[length] = row_data_info
    
def_ppg_df['2025'] = pd.to_numeric(def_ppg_df['2025'])


# Creates a dataframe from the Offensive TD table
off_td_titles_obj = off_td_soup.find_all('th')
off_td_titles = [title.text for title in off_td_titles_obj]
off_td_df = pd.DataFrame(columns = off_td_titles)
off_td_column_data = off_td_soup.find_all('tr')

for row in off_td_column_data[1:]:
    row_data = row.find_all('td')
    row_data_info = [info.text.strip() for info in row_data]

    length = len(off_td_df)
    if row_data_info[2] != '--':
        off_td_df.loc[length] = row_data_info

off_td_df['2025'] = pd.to_numeric(off_td_df['2025'])

# Creates a dataframe from the Defensive TD table
def_td_titles_obj = def_td_soup.find_all('th')
def_td_titles = [title.text for title in def_td_titles_obj]
def_td_df = pd.DataFrame(columns = def_td_titles)
def_td_column_data = def_td_soup.find_all('tr')

for row in def_td_column_data[1:]:
    row_data = row.find_all('td')
    row_data_info = [info.text.strip() for info in row_data]

    length = len(def_td_df)
    if row_data_info[2] != '--':
        def_td_df.loc[length] = row_data_info

def_td_df['2025'] = pd.to_numeric(def_td_df['2025'])

# Creates a dataframe from the TO Ratio table
to_margin_titles_obj = to_margin_soup.find_all('th')
to_margin_titles = [title.text for title in to_margin_titles_obj]
to_margin_df = pd.DataFrame(columns = to_margin_titles)
to_margin_column_data = to_margin_soup.find_all('tr')

for row in to_margin_column_data[1:]:
    row_data = row.find_all('td')
    row_data_info = [info.text.strip() for info in row_data]

    length = len(to_margin_df)
    if row_data_info[2] != '--':
        to_margin_df.loc[length] = row_data_info

to_margin_df['2025'] = pd.to_numeric(to_margin_df['2025'])
