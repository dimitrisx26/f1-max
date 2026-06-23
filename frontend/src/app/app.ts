import { DecimalPipe, UpperCasePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, inject, signal } from '@angular/core';
import { MAX_RECORDS } from './f1.records';
import { ComparisonData, DRIVER_MAP, DriverResult, FastestLapData, SeasonStats, SeasonSummary, TrackHistory, F1_TRACKS } from './f1.types';

@Component({
  selector: 'app-root',
  imports: [
    DecimalPipe,
    UpperCasePipe
  ],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {

  /**
   * API Domain
   */
  private readonly DOMAIN = "https://f1-max-backend.duckdns.org"

  /**
   * Provides the HttpClient service for making HTTP requests.
   */
  private http = inject(HttpClient);

  /**
   * Drives mapped from abbreviation to full name
   */
  driverMap: Record<string, string> = DRIVER_MAP;

  /**
   * Data coming from the API
   */
  statsData = signal<SeasonStats | null>(null);
  summaryData = signal<SeasonSummary | null>(null);
  resultsData = signal<DriverResult[] | null>(null);
  compareData = signal<ComparisonData | null>(null);
  fastestLapData = signal<FastestLapData | null>(null);
  historyData = signal<TrackHistory | null>(null);

  /**
   * Static records to display in the "Historical Records" section of the dashboard.
   */
  historicalRecords = MAX_RECORDS;

  /**
   * Used to determine if a UI element is loading
   */
  isSeasonLoading = signal<boolean>(false);
  isRaceLoading = signal<boolean>(false);
  isCompareLoading = signal<boolean>(false);
  isTrackLoading = signal<boolean>(false);

  /**
   * Years to display in the dropdown for selecting a season.
   */
  years = Array.from({length: 12}, (_, i) => 2026 - i);

  /**
   * Opponents to display in the dropdown for selecting a driver to compare against Max.
   */
  opponents = Object.entries(this.driverMap).map(([abbr, name]) => ({ abbr, name })).filter(o => o.abbr !== 'VER');

  /**
   * Tracks to display in the dropdown for selecting a track to view Max's history and fastest lap.
   */
  tracks = F1_TRACKS.sort();

  /**
   * Initializes the component.
   */
  ngOnInit(): void {
    // Preload sections with 2023 default values
    this.loadSeasonData('2023');
    this.loadRaceData('2023', '1');
    this.loadComparison('2023', 'PER');
    this.loadTrackData('Bahrain');
  }



  /**
   * Loads season data for a given year, including Max's stats and a summary of the season.
   * @param year the year to load season data for
   */
  loadSeasonData(year: string): void {
    this.isSeasonLoading.set(true);
    this.statsData.set(null);
    this.summaryData.set(null);
    
    this.http.get<SeasonStats>(`${this.DOMAIN}/max/stats/${year}`)
      .subscribe({
        next: (response) => {
          this.statsData.set(response);
          this.isSeasonLoading.set(false);
        },
        error: (err) => {
          console.error(err);
          this.isSeasonLoading.set(false);
        }
      });

    this.isSeasonLoading.set(true);
    this.http.get<SeasonSummary>(`${this.DOMAIN}/max/summary/${year}`)
      .subscribe({
        next: (response) => {
          this.summaryData.set(response);
          this.isSeasonLoading.set(false);
        },
        error: (err) => {
          console.error(err);
          this.isSeasonLoading.set(false);
        }
      });
  }

  /**
   * Loads race data for a given year and round, including Max's result
   * and the full race results.
   * @param year the year to load season data
   * @param round the round/race to load data
   */
  loadRaceData(year: string, round: string): void {
    this.isRaceLoading.set(true)
    this.http.get<DriverResult[]>(`${this.DOMAIN}/max/results/${year}/${round}`)
      .subscribe({
        next: (response) => {
          this.resultsData.set(response);
          this.isRaceLoading.set(false);
        },
        error: (err) => {
          console.error(err);
          this.isRaceLoading.set(false);
        }
      });
  }

  /**
   * Loads comparison data for Max Verstappen against a specified opponent in a given year.
   * @param year the year to load season data
   * @param opp the opponent to load data
   */
  loadComparison(year: string, opp: string): void {
    this.isCompareLoading.set(true)
    this.http.get<ComparisonData>(`${this.DOMAIN}/compare/ver/${opp}/${year}/`)
      .subscribe({
        next: (response) => {
          this.compareData.set(response);
          this.isCompareLoading.set(false);
        },
        error: (err) => {
          console.error(err);
          this.isCompareLoading.set(false);
        }
      });
  }

  /**
   * Loads track data for a given track, including the fastest lap
   * and Max's history at that track.
   * @param track the track to load data
   */
  loadTrackData(track: string): void {
    this.isTrackLoading.set(true);
    this.fastestLapData.set(null);
    this.historyData.set(null);
    
    this.http.get<FastestLapData>(`${this.DOMAIN}/max/track/${track}/fastest-lap/`)
      .subscribe({
        next: (response) => {
          this.fastestLapData.set(response);
          this.isTrackLoading.set(false);
        },
        error: (err) => {
          console.error('Fastest lap not found or error:', err);
          this.fastestLapData.set(null);
          this.isTrackLoading.set(false);
        }
      });

    this.http.get<TrackHistory>(`${this.DOMAIN}/max/track/${track}/history/`)
      .subscribe({
        next: (response) => {
          this.historyData.set(response);
        },
        error: (err) => {
          console.error('Track history not found or error:', err);
          this.historyData.set(null);
        }
      });
  }



}
