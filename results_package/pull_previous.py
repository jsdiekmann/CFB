import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import argparse

def pull_previous(week: int):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("CFB/API/cfb-tracker.json", scopes=scopes)
    client = gspread.authorize(creds)

    # Open your Google Sheet by name or ID
    sheet_id = "1gKOCgH0bcGoR0KUOz2KMnYlen4Xrenhw8uHH5ULIZLk"
    spreadsheet = client.open(sheet_id)

    # Get the previous week's worksheet
    previous_week_num = week
    previous_week_name = f"Week_{previous_week_num}"

    try:
        prev_worksheet = spreadsheet.worksheet(previous_week_name)
        prev_df = pd.DataFrame(prev_worksheet.get_all_records())
    except gspread.exceptions.WorksheetNotFound:
        print(f"❌ No sheet found for {previous_week_name}")
        prev_df = pd.DataFrame()  # fallback empty dataframe
        
    return prev_df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gets CFB results and upcoming week projections")
    parser.add_argument("week", type=int, help="Week of season (ex: 7)")
    args = parser.parse_args()

    pull_previous(args.week)