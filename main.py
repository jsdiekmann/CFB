import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
import pandas as pd
from .matchups_package.matchups import bet_df
import re

scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

creds = Credentials.from_service_account_file("CFB/API/cfb-tracker.json", scopes=scopes)

client = gspread.authorize(creds)
sheet_id = "1gKOCgH0bcGoR0KUOz2KMnYlen4Xrenhw8uHH5ULIZLk"
spreadsheet = client.open_by_key(sheet_id)

existing_titles = [ws.title for ws in spreadsheet.worksheets()]
pattern = re.compile(r"Week (\d+)")
numbers = [int(m.group(1)) for t in existing_titles if (m := pattern.match(t))]
next_number = max(numbers, default=0) + 1
new_title = f"Week {next_number}"
try:
    worksheet = spreadsheet.worksheet(new_title)
    worksheet.clear()
except gspread.exceptions.WorksheetNotFound:
    worksheet = spreadsheet.add_worksheet(title=new_title, rows=100, cols=10)
    
set_with_dataframe(worksheet, bet_df)

print("Succesfully updated CFB_2025")