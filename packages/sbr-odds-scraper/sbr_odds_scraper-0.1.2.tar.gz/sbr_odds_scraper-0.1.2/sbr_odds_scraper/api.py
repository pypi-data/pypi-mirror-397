"""Simple API for scraping MLB odds into pandas DataFrames"""

import asyncio
from typing import List, Optional
from .scraper import scrape_range_async


def _run_async(coro):
    """Run async code, handling Jupyter's existing event loop."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop, use asyncio.run()
        return asyncio.run(coro)
    
    # Running in Jupyter/IPython with existing loop
    import nest_asyncio
    nest_asyncio.apply()
    return loop.run_until_complete(coro)


def scrape(
    start_date: str,
    end_date: Optional[str] = None,
    odds_types: Optional[List[str]] = None,
    sportsbooks: Optional[List[str]] = None,
    fast: bool = False,
    max_concurrent: int = 5,
) -> "pd.DataFrame":
    """
    Scrape MLB odds from SportsBookReview and return as a pandas DataFrame.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format (defaults to start_date for single day)
        odds_types: List of odds types: "moneyline", "pointspread", "totals"
                   Defaults to all three.
        sportsbooks: List of sportsbooks to include, e.g. ["fanduel", "draftkings"]
                    Defaults to all available.
        fast: If True, reduces delays between requests (may trigger rate limiting)
        max_concurrent: Maximum concurrent requests (1-20)
    
    Returns:
        pandas DataFrame with columns:
        - date, start_time, away_team, home_team, away_score, home_score
        - venue, game_type, status
        - sportsbook, odds_type
        - For moneyline: home_odds, away_odds (opening and current)
        - For pointspread: home_odds, away_odds, home_spread, away_spread
        - For totals: over_odds, under_odds, total
    
    Example:
        >>> import sbr_odds_scraper as sbr
        >>> df = sbr.scrape("2024-10-01", "2024-10-02")
        >>> df = sbr.scrape("2024-10-01", odds_types=["moneyline"], sportsbooks=["fanduel"])
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas is required for DataFrame output. Install with: pip install pandas")
    
    if end_date is None:
        end_date = start_date
    
    if odds_types is None:
        odds_types = ["moneyline", "pointspread", "totals"]
    
    if sportsbooks is not None:
        sportsbooks = [s.lower() for s in sportsbooks]
    
    # Run the async scraper
    data = _run_async(scrape_range_async(
        start_date, end_date, fast, max_concurrent, odds_types
    ))
    
    # Flatten to DataFrame rows
    rows = []
    for date, games in data.items():
        for game in games:
            gv = game.get("gameView", {})
            base_row = {
                "date": date,
                "start_time": gv.get("startDate"),
                "away_team": gv.get("awayTeam", {}).get("fullName"),
                "away_team_short": gv.get("awayTeam", {}).get("shortName"),
                "home_team": gv.get("homeTeam", {}).get("fullName"),
                "home_team_short": gv.get("homeTeam", {}).get("shortName"),
                "away_score": gv.get("awayTeamScore"),
                "home_score": gv.get("homeTeamScore"),
                "venue": gv.get("venueName"),
                "game_type": gv.get("gameType"),
                "mlb_game_pk": gv.get("mlbGamePk"),
                "status": gv.get("gameStatusText"),
            }
            
            odds = game.get("odds", {})
            for odds_type, books in odds.items():
                for book in books:
                    book_name = book.get("sportsbook", "").lower()
                    if sportsbooks is not None and book_name not in sportsbooks:
                        continue
                    row = base_row.copy()
                    row["sportsbook"] = book.get("sportsbook")
                    row["odds_type"] = odds_type
                    
                    opening = book.get("openingLine", {})
                    current = book.get("currentLine", {})
                    
                    if odds_type == "moneyline":
                        row["opening_home_odds"] = opening.get("homeOdds")
                        row["opening_away_odds"] = opening.get("awayOdds")
                        row["current_home_odds"] = current.get("homeOdds")
                        row["current_away_odds"] = current.get("awayOdds")
                    elif odds_type == "pointspread":
                        row["opening_home_odds"] = opening.get("homeOdds")
                        row["opening_away_odds"] = opening.get("awayOdds")
                        row["opening_home_spread"] = opening.get("homeSpread")
                        row["opening_away_spread"] = opening.get("awaySpread")
                        row["current_home_odds"] = current.get("homeOdds")
                        row["current_away_odds"] = current.get("awayOdds")
                        row["current_home_spread"] = current.get("homeSpread")
                        row["current_away_spread"] = current.get("awaySpread")
                    elif odds_type == "totals":
                        row["opening_over_odds"] = opening.get("overOdds")
                        row["opening_under_odds"] = opening.get("underOdds")
                        row["opening_total"] = opening.get("total")
                        row["current_over_odds"] = current.get("overOdds")
                        row["current_under_odds"] = current.get("underOdds")
                        row["current_total"] = current.get("total")
                    
                    rows.append(row)
    
    return pd.DataFrame(rows)


def scrape_raw(
    start_date: str,
    end_date: Optional[str] = None,
    odds_types: Optional[List[str]] = None,
    fast: bool = False,
    max_concurrent: int = 5,
) -> dict:
    """
    Same as scrape() but returns raw dict instead of DataFrame.
    """
    if end_date is None:
        end_date = start_date
    
    if odds_types is None:
        odds_types = ["moneyline", "pointspread", "totals"]
    
    return _run_async(scrape_range_async(
        start_date, end_date, fast, max_concurrent, odds_types
    ))

