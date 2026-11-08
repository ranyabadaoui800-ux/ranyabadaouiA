import gzip
import os
import os.path as pt
from utils.logger import get_logger

logger = get_logger(__name__, "ingestion.log")


def ingest(path: str) -> list[str]:
    rows: list[str] = []
    try:
        # reverse=True : auth.log.4.gz (le plus ancien) en premier
        files = sorted(os.listdir(path), reverse=True)
    except FileNotFoundError:
        logger.error("Dossier introuvable : %s", path)
        return rows
    except PermissionError:
        logger.error("Accès refusé au dossier : %s", path)
        return rows

    if not files:
        logger.warning("Dossier vide : %s", path)

    for file in files:
        file_path = pt.join(path, file)
        try:
            if file.endswith('.gz'):
                opener = gzip.open(file_path, mode='rt', encoding='utf-8')
            else:
                opener = open(file_path, encoding='utf-8')
            with opener as f:
                lines = f.readlines()
            rows.extend(lines)
            logger.info("%s : %d lignes lues", file, len(lines))
        except FileNotFoundError:
            logger.error("Fichier introuvable : %s", file_path)
        except PermissionError:
            logger.error("Accès refusé : %s", file_path)
        except gzip.BadGzipFile:
            logger.error("Fichier gzip corrompu : %s", file_path)
        except UnicodeDecodeError:
            logger.error("Erreur d'encodage : %s", file_path)
        except OSError as e:
            logger.error("Erreur système sur %s : %s", file_path, e)
    return rows