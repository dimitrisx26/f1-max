export interface F1Record {
  title: string;
  value: string | number;
  description: string;
  year_achieved: number;
}

export const MAX_RECORDS: F1Record[] = [
  {
    title: "Most Wins in a Season",
    value: 19,
    description: "Secured 19 victories out of 22 races.",
    year_achieved: 2023
  },
  {
    title: "Highest Win Percentage",
    value: "86.36%",
    description: "Highest percentage of race wins in a single F1 season.",
    year_achieved: 2023
  },
  {
    title: "Most Consecutive Wins",
    value: 10,
    description: "Broke the all-time F1 record for consecutive race victories (Miami to Monza).",
    year_achieved: 2023
  },
  {
    title: "Youngest Race Winner",
    value: "18y 228d",
    description: "Won the Spanish Grand Prix on his Red Bull Racing debut.",
    year_achieved: 2016
  },
  {
    title: "Youngest Podium Finisher",
    value: "18y 228d",
    description: "Achieved his first podium at the same time he took his first win.",
    year_achieved: 2016
  },
  {
    title: "Youngest Driver to Start",
    value: "17y 166d",
    description: "Made his F1 debut at the Australian Grand Prix for Toro Rosso before he could legally drive a road car.",
    year_achieved: 2015
  },
  {
    title: "Youngest Point Scorer",
    value: "17y 180d",
    description: "Finished P7 at the Malaysian Grand Prix to score his first world championship points.",
    year_achieved: 2015
  },
  {
    title: "Youngest to Set Fastest Lap",
    value: "19y 44d",
    description: "Set the fastest lap during the wet and chaotic Brazilian Grand Prix.",
    year_achieved: 2016
  },
  {
    title: "Youngest Grand Slam",
    value: "23y 277d",
    description: "Secured Pole, Win, Fastest Lap, and Led Every Lap at the Austrian Grand Prix.",
    year_achieved: 2021
  },
  {
    title: "Most Podiums in a Season",
    value: 21,
    description: "Finished on the podium in 21 out of 22 races, proving ultimate consistency.",
    year_achieved: 2023
  },
  {
    title: "Most Points in a Season",
    value: 575,
    description: "Scored the highest number of championship points in a single F1 season.",
    year_achieved: 2023
  },
  {
    title: "Largest Championship Margin",
    value: "290 pts",
    description: "The largest points gap between 1st and 2nd place (Sergio Perez) in F1 history.",
    year_achieved: 2023
  },
  {
    title: "Most Laps Led in a Season",
    value: 1003,
    description: "Became the first driver in history to lead over 1,000 laps in a single year.",
    year_achieved: 2023
  },
  {
    title: "Most Hat-Tricks in a Season",
    value: 6,
    description: "Achieved Pole Position, Race Win, and Fastest Lap in the same weekend 6 times.",
    year_achieved: 2023
  },
  {
    title: "Most Pitstops by a Winner",
    value: 6,
    description: "Won the chaotic, rain-soaked Dutch Grand Prix despite making 6 pit stops.",
    year_achieved: 2023
  }
];
