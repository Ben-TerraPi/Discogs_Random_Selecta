"""utils.py – Discogs Random Selecta

Tirage aléatoire d'une release Discogs (recherche ou collection d'un utilisateur),
avec priorité aux vidéos Discogs et recherche YouTube en secours.
"""
import json
import logging
import os
import random
import re
import unicodedata
from pathlib import Path
from urllib.parse import quote_plus

import discogs_client
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
#Discogs Client & User token + Youtube

token = st.secrets["token"]["user_token"]

api_key = st.secrets["youtube"]["api_key"]

d = discogs_client.Client("ExampleApplication/0.1", user_token= token)

PER_PAGE = 100
MAX_OFFSET = 10_000                       # limite Discogs : 100 pages x 100 résultats
DEFAULT_COVER = "image/default_cover.png"
SEEN_FILE = Path("data/seen_ids.json")


# ---------------------------------------------------------------------------
# Historique des IDs déjà tirés (persistant)
# ---------------------------------------------------------------------------
def load_seen() -> set:
    try:
        return set(json.loads(SEEN_FILE.read_text()))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_seen(seen: set) -> None:
    SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(json.dumps(sorted(seen)))


# ---------------------------------------------------------------------------
# Helpers de correspondance texte (artiste / titre dans un titre de vidéo)
# ---------------------------------------------------------------------------
def _normalize(text: str) -> str:
    """minuscules, sans accents, sans ponctuation."""
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _clean_artist(name: str) -> str:
    """Retire le suffixe de désambiguïsation Discogs : 'Prince (2)' -> 'Prince'."""
    return re.sub(r"\s*\(\d+\)$", "", name or "").strip()


def artist_in_video(video_title: str, artist: str) -> bool:
    a = _normalize(_clean_artist(artist))
    return bool(a) and a in _normalize(video_title)


def artist_and_title_in_video(video_title: str, artist: str, title: str) -> bool:
    return artist_in_video(video_title, artist) and _normalize(title) in _normalize(video_title)


# ---------------------------------------------------------------------------
# Tirage aléatoire (recherche OU collection)
# ---------------------------------------------------------------------------
def _search_releases(genre, style=None, year=None):
    params = {"genre": genre, "type": "release"}
    if style:
        params["style"] = style
    if year:
        params["year"] = year
    return d.search(**params)


def _pick_unseen(paginated, seen, max_tries=10):
    """Tire un élément au hasard dans une PaginatedList en évitant les IDs déjà vus."""
    total = min(paginated.count, MAX_OFFSET)
    if total == 0:
        return None
    paginated.per_page = PER_PAGE
    item = None
    for _ in range(max_tries):
        page, pos = divmod(random.randrange(total), PER_PAGE)
        items = paginated.page(page + 1)          # pages Discogs : base 1
        if pos >= len(items):
            continue
        item = items[pos]
        if item.id not in seen:
            return item
    return item   # tout ou presque déjà vu : on renvoie le dernier tirage


def list_folders(username=None):
    """[(id, nom, nb_releases)] des dossiers de collection (username vide = moi)."""
    user = d.user(username.strip()) if username else d.identity()
    return [(f.id, f.name, f.count) for f in user.collection_folders]


# ---------------------------------------------------------------------------
# Extraction des infos d'une release
# ---------------------------------------------------------------------------
def _extract_info(album) -> dict:
    artists = getattr(album, "artists", None)
    images = getattr(album, "images", None)
    return {
        "title": album.title,
        "artist": _clean_artist(artists[0].name) if artists else "",
        "year": getattr(album, "year", None),
        "country": getattr(album, "country", None),
        "genres": getattr(album, "genres", []) or [],
        "styles": getattr(album, "styles", []) or [],
        "labels": [{"name": getattr(l, "name", ""), "url": getattr(l, "url", None)}
                   for l in (getattr(album, "labels", []) or [])],
        "tracklist": [{"position": getattr(t, "position", ""),
                       "title": getattr(t, "title", ""),
                       "duration": getattr(t, "duration", "")}
                      for t in (getattr(album, "tracklist", []) or [])],
        "notes": getattr(album, "notes", None),
        "formats": [f.get("name", "") for f in (getattr(album, "formats", []) or [])],
        "image": images[0]["uri"] if images else DEFAULT_COVER,
        "link": album.url,
    }


def _random_track_title(tracklist):
    titles = [t["title"] for t in tracklist if t["title"]]
    return random.choice(titles) if titles else None


# ---------------------------------------------------------------------------
# YouTube (secours quand Discogs n'a aucune vidéo)
# ---------------------------------------------------------------------------
def _youtube_search(artist, title, track_title=None, max_results=7):
    if not api_key:
        logger.warning("Clé API YouTube absente : recherche ignorée.")
        return []

    query = f"{artist} - {track_title or title} audio"
    try:
        youtube = build("youtube", "v3", developerKey=api_key)
        response = youtube.search().list(
            part="snippet", q=query, type="video",
            maxResults=max_results, order="relevance",
        ).execute()
    except HttpError as e:                       # quota dépassé (403), clé invalide...
        logger.error("Erreur YouTube : %s", e)
        return []

    videos = [
        {"title": item["snippet"]["title"],
         "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"}
        for item in response.get("items", [])
    ]

    # Meilleur résultat en premier : artiste + titre > artiste seul > reste
    # (tri stable : l'ordre de pertinence YouTube est conservé à score égal)
    def score(v):
        return (2 * artist_and_title_in_video(v["title"], artist, title)
                + artist_in_video(v["title"], artist))

    return sorted(videos, key=score, reverse=True)


# ---------------------------------------------------------------------------
# Construction du résultat : priorité aux vidéos Discogs, YouTube en secours
# ---------------------------------------------------------------------------
def build_result(album, nb_results=1) -> dict:
    info = _extract_info(album)
    info["id"] = album.id
    info["nb_results"] = nb_results
    info["url"] = ("https://www.youtube.com/results?search_query="
                   + quote_plus(f"{info['title']} audio"))

    videos = getattr(album, "videos", None)
    if videos:
        info["discogs_videos"] = random.choice(videos).url
        info["youtube_results"] = []
    else:
        info["discogs_videos"] = None
        info["youtube_results"] = _youtube_search(
            info["artist"], info["title"], _random_track_title(info["tracklist"])
        )
    return info


# ---------------------------------------------------------------------------
# Point d'entrée pour l'app
# ---------------------------------------------------------------------------
def draw(mode, seen, genre=None, style=None, year=None, username=None, folder_id=0):
    """mode : 'database' | 'collection' (username vide = ma propre collection)."""
    if mode == "database":
        results = _search_releases(genre, style, year)
        album = _pick_unseen(results, seen)
        nb = results.count
    else:  # 'collection'
        user = d.user(username.strip()) if username else d.identity()
        folders = user.collection_folders
        folder = next((f for f in folders if f.id == folder_id), folders[0])  # 0 = "All"
        item = _pick_unseen(folder.releases, seen)
        album = item.release if item else None
        nb = folder.count
    return build_result(album, nb) if album else None


def random_youtube(genre, style=None, year=None):
    """Compatibilité avec l'ancienne signature."""
    return draw("database", set(), genre=genre, style=style, year=year)
