from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

import services
import models


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "https://f1-max.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],                                                      
    allow_headers=["*"]
)

# ==========================================
# SCHEDULE
# ==========================================

@app.get("/schedule/{year}")
def get_schedule(year: int):
    """
    Fetches the full event schedule for a given Formula 1 season.
    """
    return services.load_schedule(year)


# ==========================================
# RACE RESULTS
# ==========================================

@app.get("/max/results/{year}/{race}")
def get_race_results(year: int, race: int | str):
    """
    Fetches the specific race results for Max Verstappen ('VER') for a given year and round/race name.
    """
    return services.load_race_results(year, race)


# ==========================================
# TRACK SPECIFIC
# ==========================================

@app.get("/max/track/{track_name}/history", response_model=models.TrackHistory)
def get_track_history(track_name: str):
    """
    Fetches Max Verstappen's complete historical stats (wins, podiums, races entered) for a specific track.
    """
    return services.load_track_history(track_name)

@app.get("/max/track/{track_name}/fastest-lap", response_model=models.FastestLap)
def get_fastest_lap(track_name: str):
    """
    Finds Max Verstappen's absolute fastest historical lap time at a specific track.
    """
    return services.load_fastest_lap(track_name)


# ==========================================
# SEASON / YEAR STATS
# ==========================================

@app.get("/max/summary/{year}", response_model=models.YearSummary)
def get_year_summary(year: int):
    """
    Fetches a summary of Max Verstappen's performance across an entire season.
    """
    return services.load_year_summary(year)

@app.get("/max/stats/{year}", response_model=models.DriverStats)
def get_max_stats(year: int):
    """
    Endpoint to fetch Max Verstappen's total season stats for a given year.
    """
    max_stats = services.calculate_yearly_stats("VER", year)
    return max_stats

@app.get("/compare/ver/{opp}/{year}")
def compare_drivers(opp: str, year: int):
    """
    Endpoint to compare Max Verstappen's season stats against another driver for a given year.
    """
    max_stats = get_max_stats(year)
    opp_stats = services.calculate_yearly_stats(opp, year)

    return {
        "year": year,
        "max_verstappen": max_stats,
        opp.upper(): opp_stats
    }
