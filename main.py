import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
import pandas as pd
from .matchups_package.matchups import bet_df
from .results_package.results import get_results
import re
import argparse

def main(week: int):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets"
    ]

    creds = Credentials.from_service_account_file("CFB/API/cfb-tracker.json", scopes=scopes)

    client = gspread.authorize(creds)
    sheet_id = "1gKOCgH0bcGoR0KUOz2KMnYlen4Xrenhw8uHH5ULIZLk"
    spreadsheet = client.open_by_key(sheet_id)

    # existing_titles = [ws.title for ws in spreadsheet.worksheets()]
    # pattern = re.compile(r"Week (\d+)")
    # numbers = [int(m.group(1)) for t in existing_titles if (m := pattern.match(t))]
    # next_number = max(numbers, default=0) + 1
    # new_title = f"Week {next_number}"

    sheet_name = f"Week {week}"
    results_sheet_name = f"Week {week - 1} Results"

    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        worksheet.clear()
        results_worksheet = spreadsheet.worksheet(results_sheet_name)
        results_worksheet.clear()
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=10)
        results_worksheet = spreadsheet.add_worksheet(title=results_sheet_name, rows=100, cols=10)
    set_with_dataframe(worksheet, bet_df)
    set_with_dataframe(results_worksheet, get_results(week - 1))

    print("Succesfully updated CFB_2025")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gets CFB results and upcoming week projections")
    parser.add_argument("week", type=int, help="Week of season (ex: 7)")
    args = parser.parse_args()

    main(args.week)