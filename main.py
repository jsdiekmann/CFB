import gspread
from gspread_dataframe import set_with_dataframe
import pandas as pd
from matchups_package import bet_df

cred = gspread.service_accaount(filename='./API/cfb-tracker.json')
spreadsheet = gc.open("CFB_2025")
worksheet = spreadsheet.worksheet("Sheet1")

set_with_dataframe(worksheet, bet_df)

print("Succesfully updated CFB_2025")