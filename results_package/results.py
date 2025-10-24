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
        spread_opens = [s["spreadOpen"] for s in game["lines"] if s.get("spreadOpen") is not None]
        over_opens = [o["overUnderOpen"] for o in game["lines"] if o.get("overUnderOpen") is not None]

        spread = round(sum(spreads) / len(spreads), 2) if spreads else None
        over_under = round(sum(overs) / len(overs), 2) if overs else None
        spread_opens = round(sum(spread_opens) / len(spread_opens), 2) if spread_opens else None
        over_opens = round(sum(over_opens) / len(over_opens), 2) if over_opens else None

        favorite = home if spread < 0 else away

        lines_rows.append({
            "Home": home,
            "Away": away,
            "Favorite": favorite,
            "Spread": abs(spread),
            "Opening Spread": abs(spread_opens),
            "O/U": over_under,
            "Opening O/U": over_opens
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
            "Point Diff.": spread,
            "Winner": winner,
            "Loser": loser   
        })

    results_df = pd.DataFrame(results_rows)
    results_df = teamnames.normalize_names(results_df, ["Home", "Away", "Winner", "Loser"], teamnames.name_map)
    lines_df = teamnames.normalize_names(lines_df, ["Favorite", "Home", "Away"], teamnames.name_map)
    previous_data = teamnames.normalize_names(previous_data, ["Home", "Away"], teamnames.name_map)

    merged_df = (
        results_df.merge(
            lines_df[["Home", "O/U", "Spread", "Favorite"]],
            on="Home",
            how="left")
        .merge(previous_data[["Home", "Total Expected Points", "Exp. Favorite", "Exp. Underdog", "Expected Spread", "TD/TO Differential", "TD/TO Advantage"]],
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

    merged_df["Spread Results"] = merged_df.apply(
        lambda r: (
            "Favorite" if (r["Winner"] == r["Favorite"] and r["Spread"] < r["Point Diff."])
            else "Push" if (r["Point Diff."] == r["Spread"])
            else "Underdog"
        ),
        axis=1
    )


    # Check this logic to make sure that we are calculating the correct favorite and/or expected fav
    merged_df["Expected Point Diff. Results"] = merged_df.apply(
        lambda r: (
            "Push" if (r["Point Diff."] == r["Expected Spread"])
            else "Right" if (
                (r["Exp. Favorite"] == r["Winner"] and r["Exp. Favorite"] != r["Favorite"])
                or (r["Exp. Favorite"] == r["Winner"] and r["Expected Spread"] >= r["Spread"] and r["Expected Spread"] <= r["Point Diff."])
                or (r["Exp. Favorite"] == r["Winner"] and r["Expected Spread"] >= r["Spread"] and r["Point Diff."] > r["Spread"])
                or (r["Exp. Favorite"] == r["Winner"] and r["Exp. Favorite"] == r["Favorite"] and r["Expected Spread"] < r["Spread"] and r["Spread"] > r["Point Diff."])
                or (r["Exp. Favorite"] != r["Winner"] and r["Exp. Favorite"] != r["Favorite"] and r["Point Diff."] < r["Spread"])
                or (r["Exp. Favorite"] != r["Winner"] and r["Exp. Favorite"] == r["Favorite"] and r["Expected Spread"] < r["Spread"])
            )
            else "Wrong" # if (r["Winner"] != r["Exp. Favorite"] and ((r["Exp. Favorite"] != r["Favorite"]) or
            #                                                            (r["Exp. Favorite"] == r["Favorite"]) and r["Expected Spread"] < r["Point Diff."]))
        ),
        axis=1
    )    

    results_df = merged_df.rename(columns={
        "O/U": "Line O/U",
        "Total Expected Points": "Exp. Points",
        "Expected Points Results": "Exp. O/U",
        "Expected Spread": "Exp. Diff.",
        "Expected Point Diff. Results": "Exp. Spread Winner",
        "TD/TO Differential": "TD/TO Diff.",
        "TD/TO Advantage": "TD/TO Adv."
    })

    column_order = [
        "Home", "Home Score",
        "Away", "Away Score",
        "Total Score",
        "Line O/U", "Exp. Points",
        "O/U Results", "Exp. O/U",
        "Favorite", "Spread", 
        "Exp. Favorite", "Exp. Diff.", 
        "Point Diff.", "Winner",
        "Spread Results", "Exp. Spread Winner",
        "TD/TO Diff.", "TD/TO Adv."
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