"""Command-line interface for mlb-odds-scraper"""

import argparse
import asyncio
import json
import time
from datetime import datetime

from .scraper import scrape_range_async


def main():
    parser = argparse.ArgumentParser(
        description="MLB Historical Odds Scraper - Scrapes betting odds from SportsBookReview"
    )
    parser.add_argument("start_date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("end_date", help="End date (YYYY-MM-DD)")
    parser.add_argument("-f", "--fast", action="store_true", help="Fast mode (reduced delays)")
    parser.add_argument("-c", "--concurrent", type=int, default=5, help="Max concurrent requests (default: 5)")
    parser.add_argument("-o", "--output", default="mlb_odds.json", help="Output filename")
    parser.add_argument("-t", "--types", nargs="+", default=["moneyline"], 
                       choices=["moneyline", "pointspread", "totals"],
                       help="Types of odds to retrieve (can specify multiple)")

    args = parser.parse_args()

    try:
        datetime.strptime(args.start_date, "%Y-%m-%d")
        datetime.strptime(args.end_date, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        return 1

    if args.concurrent < 1 or args.concurrent > 20:
        print("Concurrent requests should be between 1 and 20")
        return 1

    # Remove duplicates and validate odds types
    odds_types = list(set(args.types))
    valid_types = ["moneyline", "pointspread", "totals"]
    for odds_type in odds_types:
        if odds_type not in valid_types:
            print(f"Invalid odds type: {odds_type}. Must be one of: {', '.join(valid_types)}")
            return 1

    print(f"Starting async scraper (max {args.concurrent} concurrent requests)")
    print(f"Odds types: {', '.join(odds_types)}")
    start_time = time.time()
    
    all_data = asyncio.run(scrape_range_async(
        args.start_date, 
        args.end_date, 
        args.fast, 
        args.concurrent,
        odds_types
    ))

    with open(args.output, "w") as f:
        json.dump(all_data, f, indent=2)

    end_time = time.time()
    total_games = sum(len(games) for games in all_data.values())
    
    print(f"Scraped {total_games} games from {len(all_data)} dates")
    print(f"Runtime: {end_time - start_time:.2f} seconds")
    print(f"Saved to {args.output}")
    
    return 0


if __name__ == "__main__":
    exit(main())

