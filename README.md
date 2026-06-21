# Max Verstappen Command Center 🏁

A high-performance, real-time telemetry and historical data dashboard built to track the career and real-time statistics of Formula 1 World Champion Max Verstappen. 

This project demonstrates a fully decoupled, modern web architecture using a **Python/FastAPI** backend to crunch millions of rows of raw F1 telemetry data, and an **Angular 21** frontend utilizing reactive Signals to deliver a sleek, minimalist, Apple-inspired user interface.

## ✨ Core Features

* **Season Overview & Race Log:** Instantly query any F1 season to retrieve total points, wins, and podiums, alongside a detailed race-by-race grid vs. finish log.
* **Race Deep-Dive:** Fetch precise telemetry data for specific rounds (e.g. `2023`, Round `1`), displaying final grid position, status, and championship points won.
* **Championship Rivalries:** A dynamic comparison engine that pits Max Verstappen against any other driver on the grid in a given season to visualize the points differential.
* **Track Records & History:** Search by specific tracks to pull all-time fastest lap data, compound information, and historical win rates.
* **The Trophy Cabinet:** A curated, scrollable historical log of Max's greatest achievements and broken records.

## 🛠 Tech Stack & Architecture

### Frontend (Client)
* **Framework:** Angular 18+ (Standalone Components)
* **State Management:** Angular Signals (Reactive, zoneless-ready state)
* **Styling:** Custom SCSS (No UI libraries used). Designed with a strict "Apple-style minimal" aesthetic featuring deep navy surfaces, `SF Pro Display` typography, and soft elevations.
* **Network:** Angular `HttpClient` for async data fetching.

### Backend (API)
* **Framework:** Python + FastAPI
* **Data Engine:** `FastF1` and `Pandas`
* **Architecture:** RESTful architecture. The backend acts as a data-crunching middleware, downloading raw telemetry from the official Ergast/F1 APIs, processing dataframes with Pandas, and serving clean JSON to the client.

## 🚀 Getting Started (Local Development)

This project requires both the Python backend and Angular frontend to be running simultaneously.

### 1. Start the Backend API
The backend requires Python 3.9+. 

```bash
# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server (runs on http://127.0.0.1:8000)
uvicorn main:app --reload
```
*Note: The first time you request data for a specific race, the FastF1 library will cache the telemetry locally. Subsequent requests will be near-instant.*

### 2. Start the Frontend
The frontend requires Node.js and the Angular CLI.

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the Angular development server
npm run start
```
Navigate to `http://localhost:4200/` in your browser to view the Command Center.

## 🎨 Design Philosophy
The UI was built from scratch without relying on heavy component libraries (like Material or Bootstrap). The goal was to avoid the "generic dashboard" look and instead build a bespoke, premium interface. 

It utilizes a responsive 12-column Bento Box layout, deep `#040914` matte backgrounds, and strict Red Bull Racing brand colors (`#FF5B00` Dutch Orange, `#FFC72C` Yellow).

## 📝 License
This project is for educational and portfolio purposes. Data is sourced via the open-source FastF1 library.
