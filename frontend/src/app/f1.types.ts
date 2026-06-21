export interface DriverResult {
  Abbreviation: string;
  BroadcastName: string;
  FullName: string;
  Position: string;
  GridPosition: string;
  Points: string;
  Status: string;
  Time: string;
  TeamName: string;
  TrackName?: string;
}

export interface SeasonSummary {
  year: number;
  points: number;
  races_data: DriverResult[];
}

export interface SeasonStats {
  year: number;
  points: number;
  wins: number;
  podiums: number;
}

export interface DriverStats {
  year: number;
  points: number;
  wins: number;
  podiums: number;
}

export interface ComparisonData {
  year: number;
  max_verstappen: DriverStats;
  [opponentAbbr: string]: any; 
}

export interface TrackHistory {
  track: string;
  races_entered: number;
  wins: number;
  podiums: number;
}

export interface FastestLapData {
  year: number;
  fastest_lap_time: string;
  compound: string;
}

export const DRIVER_MAP: Record<string, string> = {
  "VER": "Max Verstappen",
  "PER": "Sergio Perez",
  "HAM": "Lewis Hamilton",
  "RUS": "George Russell",
  "LEC": "Charles Leclerc",
  "SAI": "Carlos Sainz",
  "NOR": "Lando Norris",
  "PIA": "Oscar Piastri",
  "ALO": "Fernando Alonso",
  "STR": "Lance Stroll",
  "GAS": "Pierre Gasly",
  "OCO": "Esteban Ocon",
  "ALB": "Alexander Albon",
  "SAR": "Logan Sargeant",
  "TSU": "Yuki Tsunoda",
  "RIC": "Daniel Ricciardo",
  "BOT": "Valtteri Bottas",
  "ZHO": "Zhou Guanyu",
  "MAG": "Kevin Magnussen",
  "HUL": "Nico Hulkenberg",
  "VET": "Sebastian Vettel",
  "RAI": "Kimi Raikkonen",
  "MSC": "Mick Schumacher",
  "LAT": "Nicholas Latifi",
  "GIO": "Antonio Giovinazzi",
  "MAZ": "Nikita Mazepin",
  "KUB": "Robert Kubica"
};
