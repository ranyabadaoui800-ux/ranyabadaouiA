import json
import os
import time
from pathlib import Path

import requests as http

from utils.logger import get_logger

logger = get_logger(__name__, "geo.log")

# Hors du dossier data/ : ingest() lit TOUS les fichiers de data/
CACHE_FILE = Path("cache") / "geo_cache.json"
TOKEN = os.getenv("IPINFO_TOKEN")  # facultatif, ne jamais l'écrire dans le code


class RateLimitError(Exception):
    """L'API a répondu 429 : limite de requêtes atteinte."""


def is_private(ip: str) -> bool:
    """IP privée ou locale : impossible à géolocaliser."""
    first, second = (int(x) for x in ip.split('.')[:2])
    return (first in (10, 127)
            or (first == 172 and 16 <= second <= 31)
            or (first == 192 and second == 168))


def load_cache() -> dict[str, str]:
    try:
        with open(CACHE_FILE, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        logger.error("Cache corrompu, on repart de zéro : %s", CACHE_FILE)
        return {}
    except OSError as e:
        logger.error("Lecture du cache impossible : %s", e)
        return {}


def save_cache(cache: dict[str, str]) -> None:
    try:
        CACHE_FILE.parent.mkdir(exist_ok=True)
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)
    except OSError as e:
        logger.error("Écriture du cache impossible : %s", e)


def geo_location(ip: str) -> str | None:
    """Code pays ('MA', 'FR'...), 'PRIVATE', ou None si la requête a échoué."""
    if is_private(ip):
        return "PRIVATE"
    params = {"token": TOKEN} if TOKEN else {}
    try:
        response = http.get(f"https://ipinfo.io/{ip}/json",
                            params=params, timeout=5)
    except http.exceptions.Timeout:
        logger.error("Timeout pour %s", ip)
        return None
    except http.exceptions.ConnectionError:
        logger.error("Pas de connexion pour %s", ip)
        return None
    except http.exceptions.RequestException as e:
        logger.error("Erreur réseau pour %s : %s", ip, e)
        return None

    if response.status_code == 429:
        raise RateLimitError(ip)
    if response.status_code != 200:
        logger.error("HTTP %s pour %s", response.status_code, ip)
        return None
    try:
        data = response.json()
    except ValueError:
        logger.error("JSON invalide pour %s", ip)
        return None
    if data.get("bogon"):
        return "PRIVATE"
    country = data.get("country")
    if not country:
        logger.warning("Pas de pays dans la réponse pour %s", ip)
        return None
    return country


def geolocate_all(ips: list[str]) -> dict[str, str]:
    """IP -> pays pour toutes les IP, en reprenant le cache déjà rempli."""
    cache = load_cache()
    todo = [ip for ip in ips if ip not in cache]
    logger.info("%d IP au total, %d déjà en cache, %d à interroger",
                len(ips), len(ips) - len(todo), len(todo))
    try:
        for i, ip in enumerate(todo, 1):
            country = geo_location(ip)
            if country:
                cache[ip] = country
            if i % 50 == 0:
                save_cache(cache)   # sauvegarde régulière
                logger.info("%d/%d IP traitées", i, len(todo))
    except RateLimitError as e:
        logger.critical("Limite atteinte (429) à l'IP %s : relance plus tard, "
                        "le cache est conservé", e)
    finally:
        save_cache(cache)
    return cache