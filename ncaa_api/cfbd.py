from fastapi import FastAPI, HTTPException, Query
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

CFBD_BASE_URL = "https://api.collegefootballdata.com"
CFBD_API_KEY = os.getenv("CFBD_API_KEY")  # Store your key as an environment variable

def get_results(year: int, week: int, season_type: str = "regular", classification: str = "fbs"):
    if not CFBD_API_KEY:
        raise HTTPException(status_code=500, detail="CFBD_API_KEY not found in environment variables.")
    
    headers = {"Authorization": f"Bearer {CFBD_API_KEY}"}
    params = {"year": year, "week": week, "seasonType": season_type, "classification": classification}
    
    try:
        response = requests.get(url=f"{CFBD_BASE_URL}/games", headers=headers, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

    data = response.json()

    # Simplify the response for clarity
    results = []
    for game in data:
        if game.get("awayClassification") != "fcs":
            results.append({
                "home_team": game.get("homeTeam"),
                "away_team": game.get("awayTeam"),
                "home_points": game.get("homePoints"),
                "away_points": game.get("awayPoints")}
            )
    
    return results


def get_lines(year: int, week: int, season_type: str = "regular"):
    if not CFBD_API_KEY:
        raise HTTPException(status_code=500, detail="CFBD_API_KEY not found in environment variables.")
    
    headers = {"Authorization": f"Bearer {CFBD_API_KEY}"}
    params = {"year": year, "week": week, "seasonType": season_type}
    
    try:
        response = requests.get(url=f"{CFBD_BASE_URL}/lines", headers=headers, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

    data = response.json()

    # Simplify the response for clarity
    results = []
    for game in data:
        if game.get("awayClassification") != "fcs":
            results.append({
                "home_team": game.get("homeTeam"),
                "away_team": game.get("awayTeam"),
                "lines": game.get("lines")
            })
            
    return results

@app.get("/cfb/scoreboard")
def scoreboard(year: int = 2025, week: int = Query(1), season_type: str = "regular", classification: str = "fbs"):
    """
    Example:
    GET /cfb/scoreboard?year=2025&week=1
    """
    return {"games": get_results(year, week, season_type, classification)}

@app.get("/cfb/lines")
def lines(year: int = 2025, week: int = 1, season_type: str = "regular", provider: str = "fanDuel"):
    return {"lines": get_lines(year, week, season_type)}