# Python Git backup server
# Morgan Piper 11/01/26

# Imports
from flask import Flask, render_template, redirect, url_for, flash, send_from_directory, request, Response, make_response, abort, send_file
import os
import requests
import yaml
from pathlib import Path
import subprocess
from taskScheduler import *

class RepositoryNotFound(Exception):
    def __init__(self, repo):
        self.repo = repo

    def __str__(self):
        return f'Sorry {self.repo} was not found'

# Init the flask application and generate an app secret key.
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Grab the config settings from config.yaml
with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        file.close()

# Literally just get of the username of the authenticated github user with the token
def get_gh_user():
    headers = {'Authorization': f'Bearer {ghToken}', 'X-Github-Api-Version': '2022-11-28'}
    r = requests.get('https://api.github.com/user', headers=headers)
    return r.json().get('login')

# Set the config options based on what options are set in config.yaml. View readme for configuration options
apiServer = config['api-server']
backupDir = config['backup-dir']
taskScheduler = config['task-scheduler']
autoRefresh = config['auto-refresh']
refreshFrequency = config['refresh-frequency']
port = config['app-port']
debug = config['app-debug']
host = config['app-host']


# Gets token and the username of the authorized user
if 'github' in apiServer:
    ghToken = os.environ["GITHUB_TOKEN"]
    user = get_gh_user()


# Pulls the git repository from github
def backupGhRepo(repo):
        args = ['git', 'clone', f'https://oauth2:{ghToken}@github.com/{user}/{repo}.git', f'{backupDir}/{repo}']
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        if 'not found' in stdout or 'not found' in stderr:
            raise RepositoryNotFound(repo)

#Just send a request to the github API and if it returns 200 then confirm that the API can be reached
def verifyGithubConnection():
    try:
        headers = {'Authorization': f'Bearer {ghToken}', 'X-Github-Api-Version': '2022-11-28'}
        r = requests.get('https://api.github.com/octocat', headers=headers)
        if r.status_code == 200:
            return 'Working!'
        else:
            app.logger.warning(f'API HTTP return code: {r.status_code}')
            return 'Hmmm something is wrong. Please check the console for the status code'
    except Exception as e:
        app.logger.error(e)
        return 'Hmmm something is wrong. Please check the console.'


# Request a list of user's git repositories from github
def getListOfGithubRepos():
    headers = {'Accept': 'application/vnd.github+json', 'Authorization': f'Bearer {ghToken}', 'X-GitHub-Api-Version': '2022-11-28'}
    r = requests.get('https://api.github.com/user/repos') 


# Get the latest commit date of a repository
def getLastCommitDate(repo):
    args = [f'git --git-dir {backupDir}/{repo}/.git log -n 1 | grep Date | tee']
    commitDate = subprocess.run(args, shell=True, check=True, capture_output=True, text=True)
    return commitDate.stdout.strip()

# Creates the directories as per configured
def createDirectories():
    if os.path.exists(backupDir) == False:
        os.mkdir(backupDir)

# Index route. This is the 'dashboard' for everything, showing the backed up repos, 
# latest pulled commits, and the status of the chosen API
@app.route('/')
def home():
    # Dict to store the repo and latest commit date of repo
    commits = {}
   

    # Runs the function to verify the API is working and also lists the files
    # in the chosen backup directory
    apiStatus = verifyGithubConnection()
    files = os.listdir(backupDir)


    # For each repo in the repo folder, run the function
    # to pull the latest commit date and add that to the dict commits
    for file in files:
        date = getLastCommitDate(file)
        commits[file] = date

    # Render all of this in the index template
    return render_template('index.html', 
                           refreshFrequency=refreshFrequency, 
                           repos=commits,
                           apiserver=apiServer,
                           apistatus=apiStatus,
                           user=user
                           )

# When this endpoint is requested, just return the output of pullLog.log
@app.route('/getpulllogs')
def getPullLogs():
    try:
        return send_file('pullLog.log')
    except Exception as e:
        print(e)
        return 'Sorry, there was an error. Please check the console'

# This route backs up the chosen repository from github
@app.route('/backupRepo', methods=['GET', 'POST'])
def backupRepo():
    # List to store the pulled repos
    repos = []
    
    
    # If the request was a POST, pull the list of chosen repos from the form
    # Backup the repo and add a flash message confirming each backed up repo
    if request.method == 'POST':
        chosen_repos = request.form.getlist('chosen_repo')
        for chosen_repo in chosen_repos:
            try:
                backupGhRepo(chosen_repo)
                addToBackup(chosen_repo)
                flash(f'{chosen_repo} has been successfully backed up!')
            except Exception as e:
                print(e)
                flash(f'There was an error backing up {chosen_repo}, please check the console', 'error')
        return redirect(url_for('home'))
  

    # Create an API request for a list of the user's repositories stored in GitHub
    headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {ghToken}", "X-GitHub-Api-Version": "2022-11-28"}
    r = requests.get("https://api.github.com/user/repos", headers=headers)


    # Get the json copy of the data
    data = r.json()
    print(data)


    # Pull the names of the repositories from the json data
    for i in data:
        name = i.get("name")
        repos.append(name)
   
    # Render the repos.html template and pass the list of users repositories
    return render_template('repos.html', repos=repos)

# If ran as a script, create the required directories and run the flask application
if __name__ == "__main__":
    createDirectories()
    if taskScheduler == 'cron':
        createCronJob()
    app.run(port=port, debug=debug, host=host)
