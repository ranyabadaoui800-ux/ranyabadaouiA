
import sqlite3
from pathlib import Path

from utils.logger import get_logger

logger = get_logger(__name__, "database.log")

# Chemin de la base de données
DB_PATH = Path(__file__).resolve().parent / "logs.db"


def init_db():
    """Créer la base de données et la table des événements."""

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT,
                    ip TEXT,
                    username TEXT,
                    count INTEGER,
                    invalid_user INTEGER,
                    country TEXT
                )
            """)

        logger.info("Base de données initialisée.")

    except sqlite3.Error as e:
        logger.error("Erreur lors de la création de la base : %s", e)
        raise


def save_events(events: list[dict], countries: dict[str, str]):
    """Enregistrer les événements dans la base de données."""

    try:
        with sqlite3.connect(DB_PATH) as conn:

            data = []

            for event in events:
                country = countries.get(event["ip"], "Inconnu")

                data.append((
                    event["type"],
                    event["ip"],
                    event["user"],
                    event["count"],
                    int(event["invalid_user"]),
                    country
                ))

            conn.executemany("""
                INSERT INTO events
                (event_type, ip, username, count, invalid_user, country)
                VALUES (?, ?, ?, ?, ?, ?)
            """, data)

        logger.info("%s événements enregistrés.", len(data))

    except (sqlite3.Error, KeyError, TypeError) as e:
        logger.error("Erreur lors de l'enregistrement : %s", e)
        raise
