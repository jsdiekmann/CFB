from CFB.ncaa_api.cfbd import get_results, get_lines
from .pull_previous import pull_previous
from CFB.scraper_package import teamnames
import pandas as pd
import argparse

if __name__ == "__main__": 

    parser = argparse.ArgumentParser(description="Gets CFB results and lines")
    parser.add_argument("year", type=int, help="Season year (ex: 2006)")
    parser.add_argument("week", type=int, help="Week of season (ex: 7)")
    args = parser.parse_args()

    lines_data = get_lines(args.year, args.week)
    results_data = get_results(args.year, args.week)
    # previous_data = pull_previous(args.week)

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

    merged_df = results_df.merge(
        lines_df[["Home", "O/U"]],
        on="Home",
        how="left"
    )

    merged_df["O/U Results"] = merged_df.apply(
        lambda r: (
            "Over" if r["Total Score"] > r["O/U"]
            else "Under" if r["Total Score"] < r["O/U"]
            else "Push"
        ),
        axis=1
    )

    results_df["Home"] = results_df["Home"].replace(teamnames.name_map)
    results_df["Away"] = results_df["Away"].replace(teamnames.name_map)
    results_df["Winner"] = results_df["Winner"].replace(teamnames.name_map)
    results_df["Loser"] = results_df["Loser"].replace(teamnames.name_map)
    results_df = merged_df.rename(columns={"O/U": "Line O/U"})

    print(results_df)