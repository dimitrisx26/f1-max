import os

from fastapi import FastAPI
import fastf1


app = FastAPI()

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
    session.load(telemetry=False, weather=False, messages=False)
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
        session.load(telemetry=False, weather=False, messages=False)
        filtered_results = session.results[session.results["Abbreviation"] == "VER"]

        total_points += filtered_results["Points"].sum()

        filtered_results_dict = filtered_results.astype(str).to_dict(orient="records")
        if len(filtered_results_dict) > 0:
            all_races_data.append(filtered_results_dict[0])

        current_event = races_schedule[races_schedule["RoundNumber"] == i]
        event_format = current_event["EventFormat"].iloc[0]

        if event_format == "sprint" or event_format == "sprint_shootout":
            sprint_session = fastf1.get_session(year, i, "S")
            sprint_session.load(telemetry=False, weather=False, messages=False)
            sprint_results = sprint_session.results[sprint_session.results["Abbreviation"] == "VER"]

            total_points += sprint_results["Points"].sum()
            sprint_results_dict = sprint_results.astype(str).to_dict(orient="records")
            if len(sprint_results_dict) > 0:
                all_races_data.append(sprint_results_dict[0])

    return { "year": year, "total_points": total_points, "races_data": all_races_data }
    