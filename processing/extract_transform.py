import re
from utils.logger import get_logger

logger = get_logger(__name__, "extract.log")

# En-tête commun : "May 24 00:28:00 ns sshd[1351222]: "
HEADER = (r'(?P<month>\w{3})\s+(?P<day>\d{1,2})\s(?P<time>\d{2}:\d{2}:\d{2})'
          r'\s\S+\ssshd\[\d+\]:\s')
# Les lignes "message repeated N times: [ ... ]" cachent N tentatives de plus
REPEAT = r'(?:message repeated (?P<repeat>\d+) times: \[ )?'
IP = r'(?P<ip>\d{1,3}(?:\.\d{1,3}){3})'

PATTERNS = {
    "failed": re.compile(
        HEADER + REPEAT + r'Failed password for (?P<invalid>invalid user )?'
        r'(?P<user>\S*)\s+from ' + IP),
    "accepted": re.compile(
        HEADER + r'Accepted (?P<method>\w+) for (?P<user>\S+) from ' + IP),
}


def extract(row: str) -> dict | None:
    """Une ligne de log -> un événement (dict), ou None si non pertinente."""
    for event_type, pattern in PATTERNS.items():
        match = pattern.search(row)
        if match:
            data = match.groupdict()
            data["type"] = event_type
            data["invalid_user"] = bool(data.pop("invalid", None))
            data["count"] = int(data.pop("repeat", None) or 1)
            return data
    return None


def transform(rows: list[str]) -> list[dict]:
    events = []
    for row in rows:
        try:
            event = extract(row)
        except Exception as e:
            logger.error("Erreur sur la ligne %r : %s", row.strip(), e)
            continue
        if event:
            events.append(event)
        elif "Failed password" in row or ": Accepted " in row:
            # ligne qui devrait matcher mais ne matche pas : à investiguer
            logger.warning("Ligne non reconnue : %s", row.strip())
    return events