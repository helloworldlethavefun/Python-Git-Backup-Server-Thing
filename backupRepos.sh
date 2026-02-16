#!/bin/bash

# Get the directory where the script itself is stored
PARENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

Readfile="$PARENT_DIR/repos.txt"
Logfile="$PARENT_DIR/pullLog.log"
BackupDir="$PARENT_DIR/backups"

# Check if the file exists before blindly trying to cat it
if [[ ! -f "$Readfile" ]]; then
    echo "Error: $Readfile not found." >> "$Logfile"
    exit 1
fi

while IFS= read -r line; do
    echo "$line:" >> "$Logfile"
    git -C "$BackupDir/$line" pull >> "$Logfile" 2>&1
done < "$Readfile"
