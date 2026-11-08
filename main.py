from collections import Counter
from ingestion import read
from processing import extract_transform
from ingestion import read

if __name__ == "__main__":
    rows = read.ingest('./data')
    events = extract_transform.transform(rows)
    print(len(rows), len(events))
    print(Counter(e['type'] for e in events))
if __name__ == "__main__":
    rows = read.ingest('./data')
    print(len(rows))    