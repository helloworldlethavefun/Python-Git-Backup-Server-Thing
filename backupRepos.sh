#! /bin/bash

Readfile="repos.txt"
Logfile="pullLog.log"

for line in $(cat "$Readfile"); do
	echo "$line:" >> $Logfile | git -C backups/$line pull >> $Logfile 
done
