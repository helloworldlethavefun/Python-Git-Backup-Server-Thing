# Python Git Backup Server

## What is this?
Just a small python app that automates backing up your git repositories. It clones them and then automates scripts for running git pull periodically.

## Config Reference

These are some options for the config.yaml file. 


`backup-dir`: Determines where the files for the git backups go

`task-scheduler`: This sets which task scheduler to use for auto pulling git. Options: cron, launchd, python

`auto-refresh`: Turns on auto-refresh for the dashboard page. Options: True/False
`refresh-frequency`: Sets how often the page refreshes (this uses minutes). 

`app-port`, `app-debug`, `app-host`: These are all options passed into flask.run() when the application runs. Refer to the documentation for the parameters. https://flask.palletsprojects.com/en/stable/api/#flask.Flask.run


