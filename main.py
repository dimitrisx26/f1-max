from fastapi.middleware.cors import CORSMiddleware
import os

from fastapi import FastAPI
import fastf1
from datetime import datetime


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],                                                      
    allow_headers=["*"]
)

os.makedirs("cache", exist_ok=True)

fastf1.Cache.enable_cache("cache")

@app.get("/schedule/{year}")
def get_schedule(year: int):
    schedule = fastf1.get_event_schedule(year)
    schedule_dict = schedule.to_dict(orient="records")
    return schedule_dict

@app.get("/max/results/{year}/{race}")
def get_race_results(year: int, race: int | str):
    session = fastf1.get_session(year, race, "R")
    session.load(laps=False, telemetry=False, weather=False, messages=False)
    filtered_results = session.results[session.results["Abbreviation"] == "VER"]
    filtered_results_dict = filtered_results.astype(str).to_dict(orient="records")
    return filtered_results_dict

@app.get("/max/summary/{year}")
def get_year_summary(year: int):
    total_points = 0
    all_races_data = []

    schedule = fastf1.get_event_schedule(year)
    races_schedule = schedule[schedule["EventFormat"] != "testing"]
    races_num = races_schedule["RoundNumber"].max()

    for i in range(1, races_num + 1):
        session = fastf1.get_session(year, i, "R")

        session.load(laps=False, telemetry=False, weather=False, messages=False)
        filtered_results = session.results[session.results["Abbreviation"] == "VER"]

        total_points += filtered_results["Points"].sum()

        filtered_results_dict = filtered_results.astype(str).to_dict(orient="records")
        if len(filtered_results_dict) > 0:
            all_races_data.append(filtered_results_dict[0])

        current_event = races_schedule[races_schedule["RoundNumber"] == i]
        event_format = current_event["EventFormat"].iloc[0]

        if event_format in ["sprint", "sprint_shootout", "sprint_qualifying"]:
            sprint_session = fastf1.get_session(year, i, "S")
            sprint_session.load(laps=False, telemetry=False, weather=False, messages=False)
            sprint_results = sprint_session.results[sprint_session.results["Abbreviation"] == "VER"]

            total_points += sprint_results["Points"].sum()
            sprint_results_dict = sprint_results.astype(str).to_dict(orient="records")
            if len(sprint_results_dict) > 0:
                all_races_data.append(sprint_results_dict[0])

    return { "year": year, "points": total_points, "races_data": all_races_data }

def calculate_yearly_stats(driver_abbr: str, year: int):
    total_points = 0
    total_wins = 0
    total_podiums = 0

    schedule = fastf1.get_event_schedule(year)
    races_schedule = schedule[schedule["EventFormat"] != "testing"]
    races_num = races_schedule["RoundNumber"].max()

    for i in range(1, races_num + 1):
        session = fastf1.get_session(year, i, "R")

        session.load(laps=False, telemetry=False, weather=False, messages=False)
        filtered_results = session.results[session.results["Abbreviation"] == driver_abbr.upper()]

        total_points += filtered_results["Points"].sum()

        filtered_results_dict = filtered_results.astype(str).to_dict(orient="records")

        if len(filtered_results_dict) > 0:
            position = filtered_results["Position"].sum()

            if position == 1.0:
                total_wins += 1

            if position <= 3.0:
                total_podiums += 1

        current_event = races_schedule[races_schedule["RoundNumber"] == i]
        event_format = current_event["EventFormat"].iloc[0]

        if event_format in ["sprint", "sprint_shootout", "sprint_qualifying"]:
            sprint_session = fastf1.get_session(year, i, "S")
            sprint_session.load(laps=False, telemetry=False, weather=False, messages=False)
            sprint_results = sprint_session.results[sprint_session.results["Abbreviation"] == driver_abbr.upper()]

            total_points += sprint_results["Points"].sum()

    return { "year": year, "points": total_points, "wins": total_wins, "podiums": total_podiums }

@app.get("/max/stats/{year}")
def get_max_stats(year: int):
    max_stats = calculate_yearly_stats("VER", year)
    return max_stats

@app.get("/compare/ver/{opp}/{year}")
def compare_drivers(opp: str, year: int):
    max_stats = get_max_stats(year)
    opp_stats = calculate_yearly_stats(opp, year)

    return {
        "year": year,
        "max_verstappen": max_stats,
        opp.upper(): opp_stats
    }

@app.get("/max/track/{track_name}/history")
def get_track_history(track_name: str):
    races_entered = 0
    total_wins = 0
    total_podiums = 0
    current_year = datetime.now().year

    for i in range(2015, current_year):
        schedule = fastf1.get_event_schedule(i)
        contains_track = schedule[schedule["Location"].str.contains(track_name, case=False)]

        if len(contains_track) == 0:
            continue

        round_number = contains_track["RoundNumber"].iloc[0]
        session = fastf1.get_session(i, round_number, "R")

        session.load(laps=False, telemetry=False, weather=False, messages=False)
        filtered_results = session.results[session.results["Abbreviation"] == "VER"]

        races_entered += 1

        position = filtered_results["Position"].sum()
        if position == 1.0:
            total_wins += 1

        if position <= 3.0:
            total_podiums += 1

    return { "track": track_name, "races_entered": races_entered, "wins": total_wins, "podiums": total_podiums }

@app.get("/max/track/{track_name}/fastest-lap")
def get_fastest_lap(track_name: str):
    absolute_fastest_time = 999999.0
    fastest_year = 0
    fastest_compound = ""
    current_year = datetime.now().year

    for i in range(2018, current_year):
        schedule = fastf1.get_event_schedule(i)
        races_schedule = schedule[schedule["EventFormat"] != "testing"] 
        contains_track = races_schedule[schedule["Location"].str.contains(track_name, case=False)]

        if len(contains_track) == 0:
            continue

        round_number = contains_track["RoundNumber"].iloc[0]
        session = fastf1.get_session(i, round_number, "R")

        session.load(telemetry=False, weather=False, messages=False)

        try:
            ver_laps = session.laps.pick_driver("VER")

            if ver_laps.empty:
                continue
        except fastf1.exceptions.DataNotLoadedError: # pyright: ignore[reportAttributeAccessIssue]
            continue

        fastest_lap = ver_laps.pick_fastest()
        if fastest_lap is None:
            continue

        lap_time_sec = fastest_lap["LapTime"].total_seconds()
        if absolute_fastest_time > lap_time_sec:
            absolute_fastest_time = lap_time_sec
            fastest_year = i
            fastest_compound = fastest_lap["Compound"]

    minutes = int(absolute_fastest_time // 60)
    seconds = absolute_fastest_time % 60
    formatted_fastest_time = f"{minutes}:{seconds:06.3f}"

    return {
        "year": fastest_year,
        "fastest_lap_time": formatted_fastest_time, 
        "compound": fastest_compound
    }
