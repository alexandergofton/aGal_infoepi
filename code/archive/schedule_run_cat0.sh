#!/bin/bash

# --- Configuration ---
PYTHON_BIN="/usr/bin/python3"  # has pytrends; miniforge python3 does not
PYTHON_SCRIPT="code/google_trends_downloader.py"
LOG_FILE="code/logs/google_trends_scheduler.log"
TOTAL_RUNS=20
SLEEP_INTERVAL=86400  # 24 hours in seconds

# --- Main loop ---
echo "Starting scheduler. Will run $TOTAL_RUNS times over $TOTAL_RUNS days." | tee -a "$LOG_FILE"

for ((i=1; i<=TOTAL_RUNS; i++)); do
    echo "" | tee -a "$LOG_FILE"
    echo "=== Run $i of $TOTAL_RUNS | $(date) ===" | tee -a "$LOG_FILE"

    "$PYTHON_BIN" "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1

    if [ $? -eq 0 ]; then
        echo "Run $i completed successfully." | tee -a "$LOG_FILE"
    else
        echo "WARNING: Run $i exited with an error. Check log for details." | tee -a "$LOG_FILE"
    fi

    if [ $i -lt $TOTAL_RUNS ]; then
        echo "Next run in 24 hours ($(date -d '+24 hours'))." | tee -a "$LOG_FILE"
        sleep $SLEEP_INTERVAL
    fi
done

echo "" | tee -a "$LOG_FILE"
echo "All $TOTAL_RUNS runs complete. | $(date)" | tee -a "$LOG_FILE"
