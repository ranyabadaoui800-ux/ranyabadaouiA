from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # génère une image, sans ouvrir de fenêtre
import matplotlib.pyplot as plt

from utils.logger import get_logger

logger = get_logger(__name__, "dashboard.log")

OUTPUT_FILE = Path("output") / "dashboard.png"


def failed_by_country(events: list[dict], countries: dict[str, str]) -> Counter:
    """Dashboard 1 : tentatives échouées par pays."""
    result: Counter = Counter()
    for e in events:
        if e["type"] != "failed":
            continue
        country = countries.get(e["ip"], "Inconnu")
        if country == "PRIVATE":
            country = "Privé"
        result[country] += e["count"]
    return result


def success_by_user(events: list[dict]) -> Counter:
    """Dashboard 2 : tentatives réussies par user."""
    result: Counter = Counter()
    for e in events:
        if e["type"] == "accepted":
            result[e["user"]] += e["count"]
    return result


def failed_invalid_user(events: list[dict]) -> Counter:
    """Dashboard 3 : tentatives échouées avec un invalid user (par nom testé)."""
    result: Counter = Counter()
    for e in events:
        if e["type"] == "failed" and e["invalid_user"]:
            result[e["user"] or "(vide)"] += e["count"]
    return result


def _bar(ax, counter: Counter, title: str, top: int = 10, horizontal: bool = True):
    if not counter:
        logger.warning("Aucune donnée pour : %s", title)
        ax.text(0.5, 0.5, "Aucune donnée", ha="center", va="center")
        ax.set_title(title)
        ax.axis("off")
        return
    items = counter.most_common(top)
    labels = [k for k, _ in items]
    values = [v for _, v in items]
    if horizontal:
        ax.barh(labels[::-1], values[::-1])
    else:
        ax.bar(labels, values)
    ax.set_title(title)


def build_dashboard(events: list[dict], countries: dict[str, str]) -> None:
    by_country = failed_by_country(events, countries)
    by_user = success_by_user(events)
    invalid = failed_invalid_user(events)

    # Affichage texte (utile aussi sans graphique)
    print("Échecs par pays (top 10) :", by_country.most_common(10))
    print("Réussites par user :", dict(by_user))
    print("Échecs invalid user :", sum(invalid.values()),
          "| top noms :", invalid.most_common(5))

    try:
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        _bar(axes[0], by_country, "Tentatives échouées par pays (top 10)")
        _bar(axes[1], by_user, "Tentatives réussies par user", horizontal=False)
        _bar(axes[2], invalid,
             f"Échecs invalid user : {sum(invalid.values())} (top 10 noms)")
        fig.tight_layout()
        OUTPUT_FILE.parent.mkdir(exist_ok=True)
        fig.savefig(OUTPUT_FILE)
        plt.close(fig)
        logger.info("Dashboard enregistré : %s", OUTPUT_FILE)
    except OSError as e:
        logger.error("Impossible d'enregistrer le dashboard : %s", e)
    except Exception as e:
        logger.error("Erreur pendant la création du dashboard : %s", e)