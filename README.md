# Python Git Backup Server

## What is this?
Just a small python app that automates backing up your git repositories. It clones them and then automates scripts for running git pull periodically.

## How to setup
> ![IMPORTANT] 
> This program relies on having git credentials already cached in the command line for running git pull. It's also worth noting that at this time, this program only supports backing up from github, although gitlab support is planned as well. And a final note is that cron is the only task scheduler setup in this program 

- Clone the repository
- Optional but reommended: Create a virtual environment `python -m venv .env`
- Install required packages `pip3 install -r requirements.txt`
- Then using your favourite text editor, have a look and configure `config.yaml`. Although feel free to use the defaults if you wish ¯\_(ツ)_/¯
- Create a github token. I haven't tested it with fine-graned tokens, but using a classic token with repository access works. 
- Export that token as an environment variable. For MacOS/Linux it's `export GITHUB_TOKEN=<token-here>`
- Run the app! `python3 main.py`

## Config Reference

These are some options for the config.yaml file. 


`backup-dir`: Determines where the files for the git backups go

`task-scheduler`: This sets which task scheduler to use for auto pulling git. Options: cron, launchd, python

`auto-refresh`: Turns on auto-refresh for the dashboard page. Options: True/False
`refresh-frequency`: Sets how often the page refreshes (this uses minutes). 

`app-port`, `app-debug`, `app-host`: These are all options passed into flask.run() when the application runs. Refer to the documentation for the parameters. https://flask.palletsprojects.com/en/stable/api/#flask.Flask.run


