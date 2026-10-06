#!/usr/bin/python3
"""
Download monthly Google Trends data for alpha-gal syndrome / mammalian meat allergy
related search terms in Australia.

Two kinds of query are made on every run:

1. SINGLE-TERM queries: each term on its own. Each series is scaled 0-100 relative to
   its own busiest month, which gives the best resolution for low-volume terms but means
   levels are NOT comparable between terms.

2. CO-QUERIES: up to 5 terms in one payload. All terms in a payload share one scale
   (100 = the busiest month of the most-searched term in that payload), so their relative
   popularity CAN be compared directly (e.g. the "alpha-gal" vs "mammalian meat allergy"
   terminology question).

Settings (changed from the previous version, archived in
code/archive/google_trends_downloader_cat0_2014-02_to_2026-02.py):
  - timeframe 2014-01-01 to 2026-10-01 (was 2014-02-01 to 2026-02-01)
  - each query is run for BOTH category 0 (All categories; main analysis, more volume)
    and category 45 (Health; sensitivity analysis, less non-health noise but many more
    zero months for low-volume terms)
  - tz = -600 = AEST, UTC+10 (was 360 = UTC-6)
  - co-query payloads added
  - output written to a separate folder, plus a download log for reporting

NOTE: Google includes the WHOLE final month in monthly data. If the script runs before
that month has ended, the last month is incomplete. This is recorded in the
`last_month_partial` column of the download log, and that month should be dropped
from analyses.

Usage (from the project root, as in schedule_run.sh):
    /usr/bin/python3 code/google_trends_downloader.py
    /usr/bin/python3 code/google_trends_downloader.py --output-dir /some/test/folder
"""

# %% ####################################
# Import modules
#########################################

import argparse
import csv
import datetime
import time
from pathlib import Path

import pandas as pd
from pytrends import exceptions
from pytrends.request import TrendReq

#########################################
# Settings
#########################################

GEO = "AU"                             # Australia, national level
# Google Trends categories to download. Every query is repeated for each category.
#   0  = All categories (main analysis: highest volume, fewest zero months)
#   45 = Health         (sensitivity analysis: excludes non-health searches)
CATEGORIES = [0, 45]
TIMEFRAME = "2014-01-01 2026-10-01"    # > 5 years, so Google returns monthly data
GPROP = ""                             # "" = Web Search
HOST_LANGUAGE = "en-US"
TZ_OFFSET = -600                       # minutes offset from UTC as used by Google: -600 = AEST

# Terms queried one at a time
SINGLE_TERMS = [
    "alpha gal",
    "Alpha-gal syndrome",
    "mammalian meat allergy",
    "meat allergy",
    "tick allergy",
    "paralysis tick",
    "ticks",
    "food allergy",  # control term
]

# Terms queried together. Google allows at most 5 terms per payload.
# The dictionary key is used in the output file name.
COQUERY_PAYLOADS = {
    # Key terms plus the control, as specified for the terminology-shift analysis
    "key_terms": [
        "alpha gal",
        "mammalian meat allergy",
        "meat allergy",
        "tick allergy",
        "food allergy",
    ],
    # AGS/MMA terms only. "food allergy" is far more searched than the AGS terms, and
    # because Google reports whole numbers, sharing a scale with it can squash
    # low-volume terms to 0-1. Leaving it out keeps better resolution for comparing
    # "alpha gal" vs "mammalian meat allergy".
    "ags_terminology": [
        "alpha gal",
        "Alpha-gal syndrome",
        "mammalian meat allergy",
        "meat allergy",
        "tick allergy",
    ],
}

DELAY_BETWEEN_CALLS = 5     # seconds between API calls
MAX_RETRIES = 5             # attempts per query when rate limited
INITIAL_RETRY_DELAY = 10    # seconds; doubled after each rate-limited attempt

# Project root = one level above this script's folder (code/), so the script works
# whatever the current working directory is
PROJECT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = PROJECT_DIR / "data" / "google_trends_2014-01_2026-10"


#########################################
# Functions
#########################################

def fetch_interest_over_time(pytrends, keywords, category):
    """
    Request interest-over-time for a list of 1-5 keywords that share one scale,
    within one Google Trends category.

    Returns a DataFrame indexed by month with one column per keyword plus
    'isPartial', or an empty DataFrame if no data could be retrieved.
    """
    if not 1 <= len(keywords) <= 5:
        raise ValueError(f"Google Trends accepts 1-5 keywords per payload, got {len(keywords)}")

    retry_delay = INITIAL_RETRY_DELAY
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            pytrends.build_payload(
                kw_list=keywords,
                cat=category,
                geo=GEO,
                timeframe=TIMEFRAME,
                gprop=GPROP,
            )
            return pytrends.interest_over_time()
        except exceptions.TooManyRequestsError:
            print(f"  Attempt {attempt}/{MAX_RETRIES}: rate limited, retrying in {retry_delay} s")
        except exceptions.ResponseError as e:
            # Other HTTP errors (often 429 reported differently); also worth retrying
            print(f"  Attempt {attempt}/{MAX_RETRIES}: response error ({e}), retrying in {retry_delay} s")
        except Exception as e:
            print(f"  Unexpected error: {e!r}")
            break
        time.sleep(retry_delay)
        retry_delay *= 2

    return pd.DataFrame()


def safe_name(text):
    """Make a string safe for use in a file name (spaces -> underscores)."""
    return text.replace(" ", "_")


def append_to_log(log_path, row):
    """Append one row describing a download to the CSV download log (created if needed)."""
    write_header = not log_path.exists()
    with open(log_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def run_query(pytrends, category, query_type, query_name, keywords, output_dir, today_str, log_path):
    """Fetch one payload in one category, save it as CSV, and record the download in the log."""
    print(f"\n{'-' * 60}\ncategory {category} | {query_type}: {query_name} -> {keywords}\n{'-' * 60}")

    df = fetch_interest_over_time(pytrends, keywords, category)
    # The category is part of the file name, e.g. gt_monthly_au_cat0_single_alpha_gal_2026-11-01.csv
    out_file = output_dir / f"gt_monthly_{GEO.lower()}_cat{category}_{query_type}_{query_name}_{today_str}.csv"

    log_row = {
        "download_timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "query_type": query_type,
        "query_name": query_name,
        "keywords": "; ".join(keywords),
        "geo": GEO,
        "category": category,
        "timeframe": TIMEFRAME,
        "gprop": GPROP if GPROP else "web",
        "tz": TZ_OFFSET,
        "status": "",
        "n_months": 0,
        "first_month": "",
        "last_month": "",
        "last_month_partial": "",
        "file": "",
    }

    if df.empty:
        # pytrends returns an empty frame when every value is 0 (common for low-volume
        # terms within the Health category) or when the request failed after retries
        print("  No data returned (all-zero series or failed request). Logged, no file written.")
        log_row["status"] = "empty"
        append_to_log(log_path, log_row)
        return

    # Record whether Google flags the final month as incomplete, then drop the flag column
    last_partial = bool(df["isPartial"].iloc[-1]) if "isPartial" in df.columns else False
    df = df.drop(columns=["isPartial"], errors="ignore")
    df.index.name = "date"
    df.to_csv(out_file)

    log_row.update({
        "status": "ok",
        "n_months": len(df),
        "first_month": df.index.min().strftime("%Y-%m-%d"),
        "last_month": df.index.max().strftime("%Y-%m-%d"),
        "last_month_partial": last_partial,
        "file": out_file.name,
    })
    append_to_log(log_path, log_row)

    print(f"  Saved {len(df)} months ({log_row['first_month']} to {log_row['last_month']}) -> {out_file}")
    if last_partial:
        print("  NOTE: Google flags the last month as partial; drop it from analyses.")


#########################################
# Main
#########################################

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR,
                        help=f"Folder for CSV output (default: {DEFAULT_OUTPUT_DIR})")
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "download_log.csv"
    today_str = datetime.date.today().strftime("%Y-%m-%d")

    print(f"Google Trends download {today_str}")
    print(f"geo={GEO} | categories={CATEGORIES} | timeframe={TIMEFRAME} | gprop={GPROP or 'web'}")
    print(f"Output: {output_dir}")

    pytrends = TrendReq(hl=HOST_LANGUAGE, tz=TZ_OFFSET)

    # Each query is a (category, type, name, keywords) tuple: for each category,
    # single terms first, then co-queries
    queries = []
    for category in CATEGORIES:
        queries += [(category, "single", safe_name(term), [term]) for term in SINGLE_TERMS]
        queries += [(category, "coquery", name, kws) for name, kws in COQUERY_PAYLOADS.items()]

    for i, (category, query_type, query_name, keywords) in enumerate(queries, start=1):
        print(f"\n[{i}/{len(queries)}]", end="")
        run_query(pytrends, category, query_type, query_name, keywords, output_dir, today_str, log_path)
        if i < len(queries):
            time.sleep(DELAY_BETWEEN_CALLS)

    print("\n=== All queries processed ===")


if __name__ == "__main__":
    main()
