import os

import fastf1
from datetime import datetime
from fastapi import HTTPException
from diskcache import Cache
from concurrent.futures import ThreadPoolExecutor, as_completed

cache = Cache("cache")

os.makedirs("cache", exist_ok=True)

fastf1.Cache.enable_cache("cache")

def get_round_summary(year: int, round_number: int, event_name: str, event_format: str):
    """
    Helper function to fetch Max Verstappen's summary data for a single round.
    Handles both the main race and sprint race (if applicable).
    Returns total points and a list of race data dictionaries.
    """
    round_points = 0
    round_data = []

    try:
        session = fastf1.get_session(year, round_number, "R")

        session.load(laps=False, telemetry=False, weather=False, messages=False)
        filtered_results = session.results[session.results["Abbreviation"] == "VER"]

        round_points += filtered_results["Points"].sum()

        filtered_results_dict = filtered_results.astype(str).to_dict(orient="records")
        if len(filtered_results_dict) > 0:
            res = filtered_results_dict[0]
            res["TrackName"] = event_name
            res["RoundNumber"] = round_number
            round_data.append(res)

        if event_format in ["sprint", "sprint_shootout", "sprint_qualifying"]:
            try:
                sprint_session = fastf1.get_session(year, round_number, "S")
                sprint_session.load(laps=False, telemetry=False, weather=False, messages=False)
                sprint_results = sprint_session.results[sprint_session.results["Abbreviation"] == "VER"]

                round_points += sprint_results["Points"].sum()
                sprint_results_dict = sprint_results.astype(str).to_dict(orient="records")
                if len(sprint_results_dict) > 0:
                    sprint_res = sprint_results_dict[0]
                    sprint_res["TrackName"] =  "(Sprint) " + event_name
                    sprint_res["RoundNumber"] = round_number
                    round_data.append(sprint_res)
            except Exception as e:
                print(f"Skipping sprint round {round_number}: {e}")
    except Exception as e:
        print(f"Skipping round {round_number}: {e}")

    return { "points": round_points, "round_data": round_data }

def get_round_stats(driver_abbr: str, year: int, round_number: int, event_format: str):
    """
    Helper function to calculate stats (points, wins, podiums) for a specific driver in a single round.
    Handles both main races and sprint races.
    """
    total_points = 0
    total_wins = 0
    total_podiums = 0

    try:
        session = fastf1.get_session(year, round_number, "R")

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

        if event_format in ["sprint", "sprint_shootout", "sprint_qualifying"]:
            try:
                sprint_session = fastf1.get_session(year, round_number, "S")
                sprint_session.load(laps=False, telemetry=False, weather=False, messages=False)
                sprint_results = sprint_session.results[sprint_session.results["Abbreviation"] == driver_abbr.upper()]

                total_points += sprint_results["Points"].sum()
            except Exception as e:
                    print(f"Skipping sprint round {round_number}: {e}")
    except Exception as e:
        print(f"Skipping round {round_number}: {e}")

    return { "points": total_points, "wins": total_wins, "podiums": total_podiums }

def calculate_yearly_stats(driver_abbr: str, year: int):
    """
    Calculates the total season stats (points, wins, podiums) for a specific driver.
    Uses a thread pool to fetch each round concurrently.
    Results are cached to disk.
    """
    cache_key = f"stats_{driver_abbr}_{year}"
    if cache_key in cache:
        return cache[cache_key]

    total_points = 0
    total_wins = 0
    total_podiums = 0

    try:
        schedule = fastf1.get_event_schedule(year)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Schedule for year {year} not found. Error: {e}")

    races_schedule = schedule[schedule["EventFormat"] != "testing"]
    races_num = races_schedule["RoundNumber"].max()

    with ThreadPoolExecutor(max_workers=8) as executor:
        tasks = []

        for i in range(1, races_num + 1):
            current_event = races_schedule[races_schedule["RoundNumber"] == i]
            event_format = current_event["EventFormat"].iloc[0]

            tasks.append(executor.submit(get_round_stats, driver_abbr, year, i, event_format))

        for future in as_completed(tasks):
            round_result = future.result()

            total_points += round_result["points"]
            total_wins += round_result["wins"]
            total_podiums += round_result["podiums"]

    stats = {"year": year, "points": total_points, "wins": total_wins, "podiums": total_podiums }
    cache[cache_key] = stats

    return stats

def get_track_year_stats(year: int, track_name: str):
    """
    Helper function to fetch Max Verstappen's stats (wins, podiums, races entered) 
    for a specific track in a specific year.
    """
    races_entered = 0
    total_wins = 0
    total_podiums = 0

    schedule = fastf1.get_event_schedule(year)
    contains_track = schedule[schedule["Location"].str.contains(track_name, case=False)]

    if len(contains_track) == 0:
        return { "races": 0, "wins": 0, "podiums": 0 }

    round_number = contains_track["RoundNumber"].iloc[0]
    session = fastf1.get_session(year, round_number, "R")

    session.load(laps=False, telemetry=False, weather=False, messages=False)
    filtered_results = session.results[session.results["Abbreviation"] == "VER"]

    races_entered += 1

    position = filtered_results["Position"].sum()
    if position == 1.0:
        total_wins += 1

    if position <= 3.0:
        total_podiums += 1

    return { "races": races_entered, "wins": total_wins, "podiums": total_podiums }

def get_year_fastest_lap(year: int, track_name: str):
    """
    Helper function to find Max Verstappen's fastest lap time at a specific track for a single year.
    Returns the time in seconds and the tire compound used.
    """
    schedule = fastf1.get_event_schedule(year)
    races_schedule = schedule[schedule["EventFormat"] != "testing"] 
    contains_track = races_schedule[schedule["Location"].str.contains(track_name, case=False)]

    if len(contains_track) == 0:
        return None

    round_number = contains_track["RoundNumber"].iloc[0]
    session = fastf1.get_session(year, round_number, "R")

    session.load(telemetry=False, weather=False, messages=False)

    try:
        ver_laps = session.laps.pick_driver("VER")

        if ver_laps.empty:
            return None
    except fastf1.exceptions.DataNotLoadedError: # pyright: ignore[reportAttributeAccessIssue]
        return None

    fastest_lap = ver_laps.pick_fastest()
    if fastest_lap is None:
        return None

    lap_time_sec = fastest_lap["LapTime"].total_seconds()
    fastest_compound = fastest_lap["Compound"]

    return { "year": year, "time": lap_time_sec, "compound": fastest_compound }

def load_schedule(year: int):
    """
    Fetches the full event schedule for a given Formula 1 season.
    Returns a list of dictionaries containing event details (date, location, format, etc.).
    """
    try:
        schedule = fastf1.get_event_schedule(year)
        schedule_dict = schedule.to_dict(orient="records")
        return schedule_dict
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Schedule for year {year} not found. Error: {e}")

def load_race_results(year: int, race: int | str):
    """
    Fetches the specific race results for Max Verstappen ('VER') for a given year and round/race name.
    """
    try:
        session = fastf1.get_session(year, race, "R")
        session.load(laps=False, telemetry=False, weather=False, messages=False)
        filtered_results = session.results[session.results["Abbreviation"] == "VER"]
        filtered_results_dict = filtered_results.astype(str).to_dict(orient="records")
        return filtered_results_dict
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Race '{race}' in year {year} not found. Error: {e}")

def load_year_summary(year: int):
    """
    Fetches a summary of Max Verstappen's performance across an entire season.
    Uses a thread pool to fetch each round concurrently.
    Results are cached to disk.
    """
    cache_key = f"year_summary_{year}"
    if cache_key in cache:
        return cache[cache_key]

    total_points = 0
    all_races_data = []

    try:
        schedule = fastf1.get_event_schedule(year)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Schedule for year {year} not found. Error: {e}")

    races_schedule = schedule[schedule["EventFormat"] != "testing"]
    races_num = races_schedule["RoundNumber"].max()

    with ThreadPoolExecutor(max_workers=8) as executor:
        tasks = []

        for i in range(1, races_num + 1):
            current_event = races_schedule[races_schedule["RoundNumber"] == i]
            event_name = current_event["EventName"].iloc[0]
            event_format = current_event["EventFormat"].iloc[0]

            tasks.append(executor.submit(get_round_summary, year, i, event_name, event_format))

        for future in as_completed(tasks):
            round_result = future.result()

            total_points += round_result["points"]
            all_races_data.extend(round_result["round_data"])

    all_races_data.sort(key=lambda x: x.get("RoundNumber", 0))
    summary = { "year": year, "points": total_points, "races_data": all_races_data }
    cache[cache_key] = summary

    return summary

def load_track_history(track_name: str):
    """
    Fetches Max Verstappen's complete historical stats (wins, podiums, races entered) for a specific track.
    Iterates through all years since 2015 concurrently.
    Results are cached to disk.
    """
    cache_key = f"history_{track_name}"
    if cache_key in cache:
        return cache[cache_key]

    races_entered = 0
    total_wins = 0
    total_podiums = 0
    current_year = datetime.now().year

    with ThreadPoolExecutor(max_workers=8) as executor:
        tasks = []

        for i in range(2015, current_year):
            tasks.append(executor.submit(get_track_year_stats, i, track_name))

        for future in as_completed(tasks):
            track_result = future.result()

            races_entered += track_result["races"]
            total_wins += track_result["wins"]
            total_podiums += track_result["podiums"]

    if races_entered == 0:
        raise HTTPException(status_code=404, detail=f"Track '{track_name}' not found or no races entered by Max Verstappen.")

    track_history = { "track": track_name, "races_entered": races_entered, "wins": total_wins, "podiums": total_podiums }
    cache[cache_key] = track_history

    return track_history

def load_fastest_lap(track_name: str):
    """
    Finds Max Verstappen's absolute fastest historical lap time at a specific track.
    Searches concurrently through all years since 2018.
    Results are cached to disk.
    """
    cache_key = f"fastest_lap_{track_name}"
    if cache_key in cache:
        return cache[cache_key]

    absolute_fastest_time = 999999.0
    fastest_year = 0
    fastest_compound = ""
    current_year = datetime.now().year

    with ThreadPoolExecutor(max_workers=8) as executor:
        tasks = []

        for i in range(2018, current_year):
            tasks.append(executor.submit(get_year_fastest_lap, i, track_name))

        for future in as_completed(tasks):
            year_result = future.result()

            if year_result is not None:
                if absolute_fastest_time > year_result["time"]:
                    absolute_fastest_time = year_result["time"]
                    fastest_year = year_result["year"]
                    fastest_compound = year_result["compound"]

    if fastest_year == 0:
        raise HTTPException(status_code=404, detail=f"No fastest lap found for Max Verstappen at track '{track_name}'.")

    minutes = int(absolute_fastest_time // 60)
    seconds = absolute_fastest_time % 60
    formatted_fastest_time = f"{minutes}:{seconds:06.3f}"

    fastest_lap = {
        "year": fastest_year,
        "fastest_lap_time": formatted_fastest_time, 
        "compound": fastest_compound
    }
    cache[cache_key] = fastest_lap

    return fastest_lap
