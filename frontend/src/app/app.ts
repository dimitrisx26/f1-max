import { DecimalPipe, UpperCasePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, inject, signal, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { MAX_RECORDS } from './f1.records';
import Chart from 'chart.js/auto';
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
   * Reference to the season chart canvas element and the Chart.js instance.
   */
  @ViewChild('seasonChart') seasonChartRef?: ElementRef<HTMLCanvasElement>;
  seasonChartInstance: Chart | null = null;

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
   * After the view initializes, render the season chart.
   */
  ngAfterViewInit() {
    this.renderChart();
  }

  /**
   * Loads season data for a given year, including Max's stats and a summary of the season.
   * @param year the year to load season data for
   */
  loadSeasonData(year: string): void {
    this.isSeasonLoading.set(true)
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

    this.isSeasonLoading.set(true)
    this.http.get<SeasonSummary>(`${this.DOMAIN}/max/summary/${year}`)
      .subscribe({
        next: (response) => {
          this.summaryData.set(response);
          this.isSeasonLoading.set(false);
          this.renderChart();
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
    this.isTrackLoading.set(true)
    this.http.get<FastestLapData>(`${this.DOMAIN}/max/track/${track}/fastest-lap/`)
      .subscribe({
        next: (response) => {
          this.fastestLapData.set(response);
          this.isTrackLoading.set(false);
        },
        error: (err) => {
          console.error(err);
          this.isTrackLoading.set(false);
        }
      });

    this.isTrackLoading.set(true)
    this.http.get<TrackHistory>(`${this.DOMAIN}/max/track/${track}/history/`)
      .subscribe({
        next: (response) => {
          this.historyData.set(response);
          this.isTrackLoading.set(false);
        },
        error: (err) => {
          console.error(err);
          this.isTrackLoading.set(false);
        }
      });
  }

  /**
   * Renders the season chart using Chart.js based on the current summary data.
   */
  renderChart() {
    const summary = this.summaryData();
    if (!summary || !summary.races_data || summary.races_data.length === 0 || !this.seasonChartRef) {
      return;
    }

    const ctx = this.seasonChartRef.nativeElement.getContext('2d');
    if (!ctx) return;

    if (this.seasonChartInstance) {
      this.seasonChartInstance.destroy();
    }

    const labels = summary.races_data.map(r => r.TrackName || 'Race');
    const positions = summary.races_data.map(r => parseInt(r.Position) || 0);

    this.seasonChartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Finishing Position',
          data: positions,
          borderColor: '#ff5b00',
          backgroundColor: 'rgba(255, 91, 0, 0.2)',
          borderWidth: 2,
          pointBackgroundColor: '#fff',
          pointBorderColor: '#ff5b00',
          pointRadius: 4,
          fill: true,
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            reverse: true, // Lower number is better in F1
            min: 1,
            max: 20,
            ticks: {
              stepSize: 1,
              color: '#8f9bb3'
            },
            grid: {
              color: 'rgba(255, 255, 255, 0.05)'
            }
          },
          x: {
            ticks: {
              color: '#8f9bb3',
              maxRotation: 45,
              minRotation: 45
            },
            grid: {
              display: false
            }
          }
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: '#111d36',
            titleColor: '#fff',
            bodyColor: '#f2f4f7',
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
            callbacks: {
              label: (context) => `P${context.parsed.y}`
            }
          }
        }
      }
    });
  }

}
