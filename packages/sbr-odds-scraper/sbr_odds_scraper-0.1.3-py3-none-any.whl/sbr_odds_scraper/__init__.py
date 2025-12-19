"""
SBR Odds Scraper

A web scraper that collects historical MLB betting odds from SportsBookReview.

Original author: Arnav Saraogi (https://github.com/ArnavSaraogi)
Original repo: https://github.com/ArnavSaraogi/mlb-odds-scraper
"""

__version__ = "0.1.3"
__author__ = "Arnav Saraogi"
__author_email__ = ""
__original_repo__ = "https://github.com/ArnavSaraogi/mlb-odds-scraper"

from .api import scrape, scrape_raw
from .scraper import (
    scrape_range_async,
    get_mlb_schedule,
    normalize_name,
)

__all__ = [
    "scrape",
    "scrape_raw",
    "scrape_range_async",
    "get_mlb_schedule", 
    "normalize_name",
]

