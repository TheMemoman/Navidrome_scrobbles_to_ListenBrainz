# Navidrome_Scrobbles_to_ListenBrainz
A Python script to synchronize your play history (scrobbles) from your Navidrome database to your ListenBrainz profile.  
This script allows you to bulk submit tracks from your Navidrome history to ListenBrainz for plays that occurred before you enabled scrobbling.

**Important:** It does **not** track play counts, only individual listens with timestamps.  
The script is intended to be run **once** to import historical plays; after that, regular scrobbling from Navidrome to ListenBrainz can continue using other clients if desired.

## Description

The script connects to your Navidrome SQLite database and retrieves all tracks you’ve played within a configurable date range (`START_YEAR` to `END_YEAR`).  
It exports a CSV of the listens and then submits them to ListenBrainz via the official API, preserving the original play timestamps.  

It supports **batch processing** and includes logging of successes and failures for safe handling of large libraries.

## How It Works

1. **Query Navidrome Database**  
   The script connects to your SQLite Navidrome database (`DB_PATH`) and queries all tracks with `play_count > 0` in the `annotation` table. Tracks are filtered by `START_YEAR` and `END_YEAR`.

2. **Export CSV**  
   A CSV file (`CSV_PATH`) is generated containing `artist`, `track`, `album`, and `timestamp` for all selected plays.

3. **Prepare Submission**  
   The script converts each track’s play date into the format required by ListenBrainz and creates a submission payload.

4. **Batch Submission**  
   Listens are submitted to ListenBrainz in batches (`BATCH_SIZE`, default 100) via the ListenBrainz API. Progress and any errors are printed to the console. A short delay is included between batches to avoid rate limits.

## Configure the following variables

| Name                 | Description                                                                                     | Suggested Value                     |
|----------------------|-------------------------------------------------------------------------------------------------|------------------------------------|
| `DB_PATH`            | Path to your Navidrome SQLite database                                                          | `/path/to/navidrome.db`            |
| `CSV_PATH`           | Path to save the CSV file                                                                       | `listenbrainz_scrobbles.csv`       |
| `START_YEAR`         | Starting year to include listens                                                                | `2020`                             |
| `END_YEAR`           | Ending year to include listens                                                                  | `2026`                             |
| `LISTENBRAINZ_TOKEN` | Your ListenBrainz API token                                                                     | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |

## Execute the script

1. Create a virtual environment and install dependencies:

```bash
python3 -m venv ~/navidrome_listenbrainz_venv
source ~/navidrome_listenbrainz_venv/bin/activate
pip install --upgrade pip
pip install requests
```

2. Run the script from the virtual environment:

```bash
python scrobbles_listenbrainz.py
```
