# Python Git Backup Server

## Config Reference

These are some options for the config.yaml file. 

`micro-server`: Determines if the built in 'git micro-server' is enabled. Options: True/False.

`backup-dir` and `micro-server-dir`: Determines where the files for the git backups go and where the microserver looks for git repos.

`task-scheduler`: This sets which task scheduler to use for auto pulling git. Options: cron, launchd, python

`auto-refresh`: Turns on auto-refresh for the dashboard page. Options: True/False
`refresh-frequency`: Sets how often the page refreshes (this uses minutes). 

`app-port`, `app-debug`, `app-host`: These are all options passed into flask.run() when the application runs. Refer to the documentation for the parameters. https://flask.palletsprojects.com/en/stable/api/#flask.Flask.run


