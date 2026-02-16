#! /usr/bin/python3

# Import subrprocess
import subprocess
import os
import yaml


currentdir = os.path.dirname(os.path.realpath(__file__))

with open(f'{currentdir}/config.yaml', 'r') as f:
    config = yaml.safe_load(f)
    f.close()

# Create some vars for the repos.txt and log file
readfile = f'{currentdir}/repos.txt'
logfile = f'{currentdir}/pullLog.log'
backupdir = config['backup-dir']

# Get the repos to backup
with open(readfile, 'r') as f:
    contents = f.readlines()
    f.close()

# Run git pull on each repository
for string in contents:
    string = string.strip()
    args = ['git', '-C', f'{backupdir}/{string}', 'pull']
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()

    # Write the output of stdout and stderr to the log file for logging
    with open(logfile, 'a') as f:
        f.write(stdout)
        f.write(stderr)
        f.close()
