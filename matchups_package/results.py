from CFB.ncaa_api.cfbd import get_results, get_lines
import pandas as pd
import argparse

if __name__ == "__main__": 

    parser = argparse.ArgumentParser(description="Gets CFB results and lines")
    parser.add_argument("year", type=int, help="Season year (ex: 2006)")
    parser.add_argument("week", type=int, help="Week of season (ex: 7)")
    args = parser.parse_args()

    def get_results(week: int=args.week):
        results_titles = ["Home", "Home Score", "Away", "Away Score", "Total Score", "Spread", "Winner", "Loser", "O/U"]
        results_df = pd.DataFrame(columns=results_titles)
        results_data = get_results(args.year, args.week)

        lines_titles = ["Home", "Away", "Spread", "O/U" ]
        lines_df = pd.DataFrame(columns=lines_titles)
        lines_data = get_lines(args.year, args.week)

        for line in lines_data:
            home = line.get("home_team")
            away = line.get("away_team")
            game_lines = line.get("lines")
            spread = 0
            over_under = 0
            for book in game_lines:
                spread += book.get("spread")
                over_under += book.get("overUnder")
            spread = round(spread / 3, 2)
            over_under = round(over_under / 3, 2)
        
            line_result = [home, away, spread, over_under]
            length = len(lines_df)

            lines_df.loc[length] = line_result

        for row in results_data:
            home_team = row[0]
            away_team = row[1]
            home_score = row[2]
            away_score = row[3]
            total_score = home_score + away_score
            spread = abs(home_score - away_score)
            if max(home_score, away_score) == home_score:
                winner = home_team
                loser = away_team
            else:
                winner = away_team
                loser = home_team
            o_u = "Over" if total_score > over_under else "Under"
            result = [home_team, home_score,  away_team, away_score, total_score, spread, winner, loser, o_u]
            length = len(results_df)

            results_df.loc[length] = result
    
        return results_df