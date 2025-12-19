# SBR Odds Scraper

A web scraper that collects historical MLB betting odds from [SportsBookReview](https://www.sportsbookreview.com).

Based on [Arnav Saraogi's mlb-odds-scraper](https://github.com/ArnavSaraogi/mlb-odds-scraper).

## Installation

```bash
pip install sbr-odds-scraper
```

## Python API

```python
import sbr_odds_scraper as sbr

# Single day - returns pandas DataFrame
df = sbr.scrape("2024-10-01")

# Date range
df = sbr.scrape("2024-10-01", "2024-10-05")

# Specific odds types (moneyline, pointspread, totals)
df = sbr.scrape("2024-10-01", odds_types=["moneyline"])

# Specific sportsbooks
df = sbr.scrape("2024-10-01", sportsbooks=["fanduel", "draftkings"])

# Combine filters
df = sbr.scrape("2024-10-01", odds_types=["moneyline"], sportsbooks=["fanduel"])

# Faster scraping (may trigger rate limits)
df = sbr.scrape("2024-10-01", fast=True)

# Raw dict instead of DataFrame
data = sbr.scrape_raw("2024-10-01")
```

### DataFrame Columns

| Column | Description |
|--------|-------------|
| `date` | Game date |
| `start_time` | Game start time (ISO format) |
| `away_team`, `home_team` | Team full names |
| `away_score`, `home_score` | Final scores |
| `venue` | Stadium name |
| `game_type` | R=Regular, F=Wild Card, D=Division, L=League, W=World Series |
| `sportsbook` | Sportsbook name (fanduel, draftkings, betmgm, etc.) |
| `odds_type` | moneyline, pointspread, or totals |
| `opening_*`, `current_*` | Opening and current line values |

## CLI Usage

```bash
sbr-odds-scraper 2024-10-01 2024-10-05 -t moneyline pointspread -o odds.json
```

| Flag | Description |
|------|-------------|
| `-t`, `--types` | Odds types: `moneyline`, `pointspread`, `totals` (default: moneyline) |
| `-c`, `--concurrent` | Concurrent requests (default: 5) |
| `-f`, `--fast` | Faster scraping (reduced delays) |
| `-o`, `--output` | Output filename (default: mlb_odds.json) |

## JSON Structure

The raw data is organized by date. Each date contains a list of games with sportsbook odds:

```json
{
  "2021-04-01": [
    {
      "gameView": {
        "startDate": "2021-04-01T17:05:00+00:00",
        "awayTeam": {
          "fullName": "Toronto Blue Jays",
          "shortName": "TOR"
        },
        "awayTeamScore": 3,
        "homeTeam": {
          "fullName": "New York Yankees",
          "shortName": "NYY"
        },
        "homeTeamScore": 2,
        "gameStatusText": "Final (10)",
        "venueName": "Yankee Stadium",
        "gameType": "R"
      },
      "odds": {
        "moneyline": [
          {
            "sportsbook": "fanduel",
            "openingLine": { "homeOdds": -188, "awayOdds": 155 },
            "currentLine": { "homeOdds": -200, "awayOdds": 168 }
          },
          {
            "sportsbook": "draftkings",
            "openingLine": { "homeOdds": -175, "awayOdds": 148 },
            "currentLine": { "homeOdds": -195, "awayOdds": 165 }
          }
        ],
        "pointspread": [
          {
            "sportsbook": "fanduel",
            "openingLine": { "homeOdds": 122, "awayOdds": -144, "homeSpread": -1.5, "awaySpread": 1.5 },
            "currentLine": { "homeOdds": 100, "awayOdds": -120, "homeSpread": -1.5, "awaySpread": 1.5 }
          }
        ],
        "totals": [
          {
            "sportsbook": "fanduel",
            "openingLine": { "overOdds": -106, "underOdds": -114, "total": 8 },
            "currentLine": { "overOdds": -122, "underOdds": 100, "total": 7.5 }
          }
        ]
      }
    }
  ]
}
```

## Notes

- Historical data available from ~2019-05-03 onwards
- Use `fast=True` / `-f` sparingly to avoid rate limiting
- Game types: R=Regular, S=Spring, E=Exhibition, A=All-Star, D=Division, F=Wild Card, L=League Championship, W=World Series

## Credits

Original scraper by [Arnav Saraogi](https://github.com/ArnavSaraogi/mlb-odds-scraper).

## Disclaimer

For educational purposes only. Review SportsBookReview's Terms of Service before use.
