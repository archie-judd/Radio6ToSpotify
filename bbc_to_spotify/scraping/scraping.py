import logging

import requests
from bs4 import BeautifulSoup as bs

from bbc_to_spotify.scraping.models import ScrapedTrack
from bbc_to_spotify.utils import PlaylistUrl

logger = logging.getLogger(__name__)


def scrape_primary_artist(artist: str) -> str:
    artist_primary = artist.replace("&", "ft.").split("ft.")[0]
    return artist_primary


def scrape_tracks_from_playlist_page(playlist_url: PlaylistUrl) -> list[ScrapedTrack]:

    scraped_tracks: list[ScrapedTrack] = []

    logger.info(f"Scraping tracks from:{playlist_url}")

    page = requests.get(url=playlist_url, timeout=30)
    soup = bs(markup=page.content, features="html.parser")

    sections = soup.find_all(class_=("component__body br-box-page"))
    for section in sections:
        songs = [
            p.get_text(strip=True).lstrip("↑").strip()
            for p in section.find_all("p")
            if not p.find("h2") and " - " in p.get_text()
        ]
        for song in songs:
            artist = song.split(" - ")[0]
            primary_artist = scrape_primary_artist(artist)
            track_name = song.split(" - ")[-1]
            scraped_tracks.append(ScrapedTrack(artist=primary_artist, name=track_name))

    logger.debug(f"Scraped {len(scraped_tracks)} tracks.\n{scraped_tracks}")

    return scraped_tracks
