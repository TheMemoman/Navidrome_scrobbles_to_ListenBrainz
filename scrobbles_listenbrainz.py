import sqlite3
import csv
from pathlib import Path
from datetime import datetime
import time
import requests

# ----- CONFIG -----
DB_PATH = "navidrome.db"
CSV_PATH = "listenbrainz_scrobbles.csv"
START_YEAR = 2020
END_YEAR = 2026
LISTENBRAINZ_TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # <- put your token here, no <>

API_URL = "https://api.listenbrainz.org/1/submit-listens"
BATCH_SIZE = 100

# ----- QUERY NAVIDROME DB -----
def query_navidrome(db_path, start_year, end_year):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = f"""
    SELECT
        mf.artist,
        mf.title,
        mf.album,
        a.play_date
    FROM annotation a
    JOIN media_file mf ON mf.id = a.item_id
    WHERE a.play_count > 0
      AND a.play_date >= '{start_year}-01-01 00:00:00'
      AND a.play_date <=  '{end_year}-12-31 00:00:00'
    ORDER BY a.play_date ASC;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

# ----- EXPORT CSV -----
def export_csv(rows, csv_path):
    csv_file = Path(csv_path)
    with csv_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["artist", "track", "album", "timestamp"])
        for artist, track, album, play_date in rows:
            if play_date is None:
                continue
            dt = datetime.fromisoformat(play_date.replace(" ", "T"))
            iso_ts = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            writer.writerow([artist, track, album, iso_ts])
    print(f"CSV saved to {csv_path}")

# ----- PREPARE FOR SUBMISSION -----
def prepare_listens_for_submission(rows):
    listens = []
    for artist, track, album, play_date in rows:
        if play_date is None:
            continue
        dt = datetime.fromisoformat(play_date.replace(" ", "T"))
        timestamp = int(dt.timestamp())
        listens.append({
            "listened_at": timestamp,
            "track_metadata": {
                "artist_name": artist,
                "track_name": track,
                "release_name": album or "",
                "additional_info": {
                    "submission_client": "navidrome-submit-script",
                    "music_service": "navidrome"
                }
            }
        })
    return listens

# ----- SUBMIT LISTENS -----
def submit_listens(listens, token):
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    total = len(listens)
    num_batches = (total - 1) // BATCH_SIZE + 1
    print(f"Submitting {total} listens in {num_batches} batches...")

    for batch_idx in range(0, total, BATCH_SIZE):
        batch_listens = listens[batch_idx:batch_idx+BATCH_SIZE]
        payload = {"listen_type": "import", "payload": batch_listens}
        
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=15)
            resp_json = response.json()
            
            if response.status_code in [200, 202] and resp_json.get("status") == "ok":
                print(f"Batch {batch_idx//BATCH_SIZE + 1}/{num_batches} submitted successfully ({len(batch_listens)} listens)")
            else:
                print(f"Batch {batch_idx//BATCH_SIZE + 1}/{num_batches} failed! Status: {response.status_code}, Response: {resp_json}")
        except Exception as e:
            print(f"Exception submitting batch {batch_idx//BATCH_SIZE + 1}: {e}")
        time.sleep(1)

# ----- MAIN -----
def main():
    rows = query_navidrome(DB_PATH, START_YEAR, END_YEAR)
    print(f"Found {len(rows)} listens in {START_YEAR}.")
    
    export_csv(rows, CSV_PATH)
    
    listens = prepare_listens_for_submission(rows)
    submit_listens(listens, LISTENBRAINZ_TOKEN)

if __name__ == "__main__":
    main()
