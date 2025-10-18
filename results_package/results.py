from CFB.ncaa_api.cfbd import get_results, get_lines
from .pull_previous import pull_previous
from CFB.scraper_package import teamnames
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
import pandas as pd
import argparse

if __name__ == "__main__": 

    parser = argparse.ArgumentParser(description="Gets CFB results and lines")
    parser.add_argument("year", type=int, help="Season year (ex: 2006)")
    parser.add_argument("week", type=int, help="Week of season (ex: 7)")
    args = parser.parse_args()

    lines_data = get_lines(args.year, args.week)
    results_data = get_results(args.year, args.week)
    previous_data = pull_previous(args.week)

    lines_rows = []

    for game in lines_data:
        home = game["home_team"]
        away = game["away_team"]

        spreads = [s["spread"] for s in game["lines"] if s.get("spread") is not None]
        overs = [o["overUnder"] for o in game["lines"] if o.get("overUnder") is not None]

        spread = round(sum(spreads) / len(spreads), 2) if spreads else None
        over_under = round(sum(overs) / len(overs), 2) if overs else None

        lines_rows.append({
            "Home": home,
            "Away": away,
            "Spread": spread,
            "O/U": over_under
        })

    lines_df = pd.DataFrame(lines_rows)

    results_rows = []

    for game in results_data:
        home = game["home_team"]
        away = game["away_team"]
        home_score = game["home_points"]
        away_score = game["away_points"]
        total_score = home_score + away_score
        spread = abs(home_score - away_score)
        winner = home if home_score > away_score else away
        loser = away if home_score > away_score else home

        results_rows.append({
            "Home": home,
            "Home Score": home_score,
            "Away": away,
            "Away Score": away_score,
            "Total Score": total_score,
            "Spread": spread,
            "Winner": winner,
            "Loser": loser   
        })

    results_df = pd.DataFrame(results_rows)
    results_df = teamnames.normalize_names(results_df, ["Home", "Away", "Winner", "Loser"], teamnames.name_map)
    lines_df = teamnames.normalize_names(lines_df, ["Home", "Away"], teamnames.name_map)
    previous_data = teamnames.normalize_names(previous_data, ["Home", "Away"], teamnames.name_map)

    merged_df = (
        results_df.merge(
            lines_df[["Home", "O/U"]],
            on="Home",
            how="left")
        .merge(previous_data[["Home", "Total Expected Points"]],
            on="Home",
            how="left")
    )

    merged_df["O/U Results"] = merged_df.apply(
        lambda r: (
            "Over" if r["Total Score"] > r["O/U"]
            else "Under" if r["Total Score"] < r["O/U"]
            else "Push"
        ),
        axis=1
    )

    merged_df["Expected Points Results"] = merged_df.apply(
        lambda r: (
            "Over" if r["Total Expected Points"] > r["O/U"]
            else "Under" if r["Total Expected Points"] < r["O/U"]
            else "Push"
        ),
        axis=1
    )

    results_df = merged_df.rename(columns={"O/U": "Line O/U", "Total Expected Points": "Exp. Points", "Expected Points Results": "Exp. O/U"})

    column_order = [
        "Home", "Home Score",
        "Away", "Away Score",
        "Total Score",
        "Line O/U", "Exp. Points",
        "O/U Results", "Exp. O/U",
        "Spread",
        "Winner", "Loser"
    ]

    results_df = results_df[column_order]

    def upload_results(week: int):
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets"
        ]
        creds = Credentials.from_service_account_file("CFB/API/cfb-tracker.json", scopes=scopes)
        client = gspread.authorize(creds)

        # Open your Google Sheet by name or ID
        sheet_id = "1gKOCgH0bcGoR0KUOz2KMnYlen4Xrenhw8uHH5ULIZLk"
        spreadsheet = client.open_by_key(sheet_id)

        results_sheet_name = f"Week {week} Results"

        try:
            results_worksheet = spreadsheet.worksheet(results_sheet_name)
            results_worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            results_worksheet = spreadsheet.add_worksheet(title=results_sheet_name, rows=100, cols=10)
        set_with_dataframe(results_worksheet, results_df)

        print(f"Succesfully uploaded Week {week} Results")

    upload_results(args.week)