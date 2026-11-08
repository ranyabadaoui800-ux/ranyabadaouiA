from ingestion import read
from processing import extract_transform, geolocation

if __name__ == "__main__":
    rows = read.ingest('./data')
    events = extract_transform.transform(rows)
    ips = sorted({e['ip'] for e in events})
    print(len(rows), "lignes,", len(events), "événements,", len(ips), "IP uniques")
    countries = geolocation.geolocate_all(ips)
    print(len(countries), "IP géolocalisées")