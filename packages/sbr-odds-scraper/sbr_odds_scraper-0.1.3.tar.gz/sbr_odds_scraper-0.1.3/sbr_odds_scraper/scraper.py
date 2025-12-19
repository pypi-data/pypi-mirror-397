import aiohttp
import asyncio
import json
import re
import random
import functools
import requests
from datetime import datetime, timedelta
from tqdm import tqdm
from .pools import USER_AGENTS, ACCEPT_LANGUAGES

NEXT_DATA_PATTERN = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.DOTALL)

@functools.lru_cache(maxsize=64)
def normalize_name(name):
    """Cached team name normalization"""
    return (name
            .lower()
            .replace(".", "")
            .replace("'", "")
            .replace("-", " ")
            .replace("&", "and")
            .strip())

async def get_html_async(session, url, semaphore, retries=3, base_delay=2):
    """Async version of get_html with semaphore for rate limiting"""
    for attempt in range(retries):
        async with semaphore:
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept-Language": random.choice(ACCEPT_LANGUAGES),
            }
            try:
                async with session.get(url, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        return await resp.text()
                    else:
                        print(f"Request failed with status {resp.status} for {url}")
            except Exception as e:
                print(f"Error fetching {url}: {e}")
        
        if attempt < retries - 1:
            delay = base_delay + random.uniform(0, 2)
            await asyncio.sleep(delay)
    
    return None

def get_mlb_schedule(start_date, end_date):
    """Fetch MLB schedule with game_pk and game times for merge_asof matching."""
    
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    schedule_map = {}
    current_start = start
    
    while current_start <= end:
        current_end = min(current_start.replace(year=current_start.year + 1) - timedelta(days=1), end)
        url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate={current_start.strftime('%Y-%m-%d')}&endDate={current_end.strftime('%Y-%m-%d')}"
        resp = requests.get(url)
        data = resp.json()
        
        for date_info in data.get("dates", []):
            date = date_info["date"]
            if date not in schedule_map:
                schedule_map[date] = []
            for g in date_info.get("games", []):
                away = g["teams"]["away"]["team"]["name"]
                home = g["teams"]["home"]["team"]["name"]
                schedule_map[date].append({
                    "away": normalize_name(away),
                    "home": normalize_name(home),
                    "game_pk": g["gamePk"],
                    "game_date": g.get("gameDate"),  # ISO timestamp
                    "game_type": g["gameType"]
                })

        current_start = current_end + timedelta(days=1)

    return schedule_map

def get_odds_url(date, odds_type):
    """Get the appropriate URL for the given odds type"""
    base_url = "https://www.sportsbookreview.com/betting-odds/mlb-baseball"
    
    if odds_type == "moneyline":
        return f"{base_url}/?date={date}"
    elif odds_type == "pointspread":
        return f"{base_url}/pointspread/full-game/?date={date}"
    elif odds_type == "totals":
        return f"{base_url}/totals/full-game/?date={date}"
    else:
        raise ValueError(f"Unknown odds type: {odds_type}")

def extract_odds_data(odds, odds_type):
    """Extract the appropriate odds data based on the odds type"""
    opening_line = odds.get("openingLine", {})
    current_line = odds.get("currentLine", {})
    
    if odds_type == "moneyline":
        opening_keys = ["homeOdds", "awayOdds"]
        current_keys = ["homeOdds", "awayOdds"]
    elif odds_type == "pointspread":
        opening_keys = ["homeOdds", "awayOdds", "homeSpread", "awaySpread"]
        current_keys = ["homeOdds", "awayOdds", "homeSpread", "awaySpread"]
    else:  # totals
        opening_keys = ["overOdds", "underOdds", "total"]
        current_keys = ["overOdds", "underOdds", "total"]
    
    opening_line_cleaned = {k: opening_line.get(k) for k in opening_keys}
    current_line_cleaned = {k: current_line.get(k) for k in current_keys}
    
    return opening_line_cleaned, current_line_cleaned

def _lookup_game_info(schedule_list, away, home, start_time=None):
    """Look up game info from schedule list, handling doubleheaders by time."""
    matches = [g for g in schedule_list if g["away"] == away and g["home"] == home]
    if not matches:
        return {"game_type": "Unknown", "game_pk": None}
    if len(matches) == 1:
        return {"game_type": matches[0]["game_type"], "game_pk": matches[0]["game_pk"]}
    # Multiple matches (doubleheader) - try to match by time
    if start_time:
        from datetime import datetime
        try:
            sbr_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            best_match = min(matches, key=lambda g: abs(
                (datetime.fromisoformat(g["game_date"].replace('Z', '+00:00')) - sbr_time).total_seconds()
            ) if g["game_date"] else float('inf'))
            return {"game_type": best_match["game_type"], "game_pk": best_match["game_pk"]}
        except:
            pass
    # Fallback to first match
    return {"game_type": matches[0]["game_type"], "game_pk": matches[0]["game_pk"]}


async def scrape_mlb_odds_async(session, date, odds_type, schedule_map, semaphore, base_delay=2):
    """Async version of scrape_mlb_odds"""
    
    url = get_odds_url(date, odds_type)
    html = await get_html_async(session, url, semaphore, base_delay=base_delay)
    
    if not html:
        print(f"Failed to fetch {odds_type} odds for {date}")
        return date, odds_type, []

    match = NEXT_DATA_PATTERN.search(html)
    if not match:
        print(f"No __NEXT_DATA__ found for {odds_type} odds on {date}")
        return date, odds_type, []

    try:
        data = json.loads(match.group(1))
        odds_tables = data.get("props", {}).get("pageProps", {}).get("oddsTables", [])
        
        if not odds_tables:
            return date, odds_type, []

        game_rows = odds_tables[0].get("oddsTableModel", {}).get("gameRows", [])
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Error parsing {odds_type} data for {date}: {e}")
        return date, odds_type, []

    games_for_date = []
    schedule_list = schedule_map.get(date, [])

    for game in game_rows:
        try:
            game_view = game.get("gameView", {})
            away = normalize_name(game_view.get("awayTeam", {}).get("fullName", "Unknown"))
            home = normalize_name(game_view.get("homeTeam", {}).get("fullName", "Unknown"))
            start_time = game_view.get("startDate")

            # Create a game identifier for matching across odds types
            game_key = f"{away}_vs_{home}_{start_time}" if start_time else f"{away}_vs_{home}"
            
            # Look up game info from MLB schedule
            game_info = _lookup_game_info(schedule_list, away, home, start_time)
            
            cleaned_game = {
                "gameKey": game_key,
                "gameView": {}
            }
            
            # Copy game view data
            for key in ["startDate", "awayTeam", "awayTeamScore", "homeTeam", "homeTeamScore", "gameStatusText", "venueName"]:
                cleaned_game["gameView"][key] = game_view.get(key)
            
            cleaned_game["gameView"]["gameType"] = game_info["game_type"]
            cleaned_game["gameView"]["mlbGamePk"] = game_info["game_pk"]

            cleaned_odds_views = []
            for odds in game.get("oddsViews", []):
                if odds is None:
                    continue
                
                try:
                    sportsbook = odds.get("sportsbook", "Unknown")
                    opening_line_cleaned, current_line_cleaned = extract_odds_data(odds, odds_type)
                    
                    cleaned_book = {
                        "sportsbook": sportsbook, 
                        "openingLine": opening_line_cleaned, 
                        "currentLine": current_line_cleaned
                    }
                    cleaned_odds_views.append(cleaned_book)
                except Exception as e:
                    print(f"Error processing {odds_type} odds for {date}: {e}")
                    continue
            
            cleaned_game["oddsViews"] = cleaned_odds_views
            games_for_date.append(cleaned_game)
            
        except Exception as e:
            print(f"Error processing game for {odds_type} on {date}: {e}")
            continue

    return date, odds_type, games_for_date

def merge_odds_data(all_results, odds_types):
    """Merge odds data from different types into a single structure"""
    merged_data = {}
    
    # Group results by date
    date_results = {}
    for date, odds_type, games in all_results:
        if date not in date_results:
            date_results[date] = {}
        date_results[date][odds_type] = games
    
    # Merge games by game key
    for date, odds_by_type in date_results.items():
        merged_games = {}
        
        # First pass: collect all unique games
        for odds_type, games in odds_by_type.items():
            for game in games:
                game_key = game.get("gameKey")
                if not game_key:
                    continue
                
                # For matching across odds types, use teams+time as key
                if game_key not in merged_games:
                    # Create a copy of gameView to avoid reference issues
                    game_view_copy = game["gameView"].copy()
                    merged_games[game_key] = {
                        "gameView": game_view_copy,
                        "odds": {}
                    }
                
                # Add odds for this type
                merged_games[game_key]["odds"][odds_type] = game["oddsViews"]
        
        # Convert to list
        merged_data[date] = list(merged_games.values())
    
    return merged_data

async def scrape_range_async(start_date, end_date, fast=False, max_concurrent=5, odds_types=None):
    """Main async scraping function for multiple odds types
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        fast: If True, reduces delays between requests
        max_concurrent: Maximum number of concurrent requests
        odds_types: List of odds types to scrape (moneyline, pointspread, totals)
    
    Returns:
        Dictionary of scraped odds data organized by date
    """
    if odds_types is None:
        odds_types = ["moneyline"]
        
    print("Fetching MLB schedule...")
    game_type_map = get_mlb_schedule(start_date, end_date)
    
    if not game_type_map:
        print("No games found in date range")
        return {}
    
    dates = sorted(game_type_map.keys())
    print(f"Found {len(dates)} dates to scrape for odds types: {', '.join(odds_types)}")
    
    semaphore = asyncio.Semaphore(max_concurrent)
    base_delay = 0.1 if fast else 1.0
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        # Create tasks for each date and odds type combination
        for date in dates:
            for odds_type in odds_types:
                task = scrape_mlb_odds_async(session, date, odds_type, game_type_map, semaphore, base_delay)
                tasks.append(task)
        
        print(f"Scraping {len(tasks)} date/odds-type combinations with {max_concurrent} concurrent requests...")
        
        results = []
        chunk_size = max_concurrent * 2
        
        pbar = None
        try:
            pbar = tqdm(total=len(tasks), desc="Scraping", unit="requests")
            
            for i in range(0, len(tasks), chunk_size):
                chunk_tasks = tasks[i:i + chunk_size]
                chunk_results = await asyncio.gather(*chunk_tasks, return_exceptions=True)
                
                successful_in_chunk = 0
                for result in chunk_results:
                    if isinstance(result, tuple) and len(result) == 3:
                        date, odds_type, games = result
                        results.append((date, odds_type, games))
                        if games:
                            successful_in_chunk += 1
                    else:
                        print(f"\nTask failed: {result}")
                
                pbar.update(len(chunk_tasks))
                total_with_games = sum(1 for _, _, games in results if games)
                pbar.set_postfix({"with_games": total_with_games, "chunk_success": successful_in_chunk})
                
                if not fast and i + chunk_size < len(tasks):
                    delay = base_delay + random.uniform(0, base_delay)
                    await asyncio.sleep(delay)
                    
        finally:
            if pbar:
                pbar.close()
    
    # Merge all odds types into a single data structure
    merged_data = merge_odds_data(results, odds_types)
    
    return merged_data

