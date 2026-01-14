# Python Git backup server
# Morgan Piper 11/01/26

# Imports
from flask import Flask, render_template, redirect, url_for, flash, send_from_directory, request, Response, make_response
from git import Git
import os
import requests
import yaml
from pathlib import Path
from starlette.responses import StreamingResponse
import subprocess

# Init the flask application and generate an app secret key.
app = Flask(__name__)
app.secret_key = os.urandom(24)


with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        file.close()


def get_user():
    headers = {'Authorization': f'Bearer {ghToken}', 'X-Github-Api-Version': '2022-11-28'}
    r = requests.get('https://api.github.com/user', headers=headers)
    return r.json().get('login')


# Gets token and the username of the authorized user
ghToken = os.environ["GITHUB_TOKEN"]
user = get_user()


# Pulls config options from config.yaml. View config.yaml for configuration options
microServerDir = config['micro-server-dir']
backupDir = config['backup-dir']
taskScheduler = config['task-scheduler']
autoRefresh = config['auto-refresh']
refreshFrequency = config['refresh-frequency']
port = config['app-port']


# Pulls the git repository from github
def backupGhRepo(repo):
    try:
        os.system(f'git clone https://oauth2:{ghToken}@github.com/{user}/{repo}.git {backupDir}/{repo}')
    except Exception as e:
        print(e)


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
    r = requests.get('https://api.github.com/user/repos') # Change back to the directory this script is in


# Get the latest commit date of a repository
def getLastCommitDate(repo):
    args = [f'git --git-dir {backupDir}/{repo}/.git log -n 1 | grep Date | tee']
    commitDate = subprocess.run(args, shell=True, check=True, capture_output=True, text=True)
    return commitDate.stdout.strip()


# Creates the directories as per configured
def createDirectories():
    if os.path.exists(backupDir) == False and os.path.exists(microServerDir) == False:
        os.mkdir(backupDir)
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
    return render_template('index.html', refreshFrequency=refreshFrequency, repos=commits, apistatus=apiStatus)


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
            backupGhRepo(chosen_repo)
            flash(f'{chosen_repo} has been successfully backed up!')
        return redirect(url_for('home'))
  

    # Create an API request for a list of the user's repositories stored in GitHub
    headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {ghToken}", "X-GitHub-Api-Version": "2022-11-28"}
    r = requests.get("https://api.github.com/user/repos", headers=headers)


    # Get the json copy of the data
    data = r.json()


    # Pull the names of the repositories from the json data
    for i in data:
        name = i.get("name")
        repos.append(name)
   
    
    # Render the repos.html template and pass the list of users repositories
    return render_template('repos.html', repos=repos)



# The Following code is for the "micro git server." Credit for the original code to meyer1994 on Github
# This was modified to work with flask, rather than uvicorn and fast_api
# Original Code: https://github.com/meyer1994/gitserver/tree/master


@app.route('/<path:repo_path>/info/refs', methods=['GET'])
def info_refs(repo_path):
    service = request.args.get('service')

    if ".git" not in repo_path:
        repo_path = repo_path + '.git'
    
    real_path = Path(f'{microServerDir}/{repo_path}') 

    if real_path.exists():
        repo = Git(str(real_path))
    else:
        repo = Git.init(str(real_path))

    data_io = repo.inforefs(service)
    
    media = f'application/x-{service}-advertisement'
    return Response(
        data_io.getvalue(), 
        mimetype=media
    )


@app.route('/<path:repo_path>/<service_name>', methods=['POST'])
def service_rpc(repo_path, service_name):
    real_path = Path(f'{micro-server-dir}/{repo_path}')
    repo = Git(str(real_path))

    input_data = request.data 
    
    output_io = repo.service(service_name, input_data)

    media = f'application/x-{service_name}-result'
    return Response(
        output_io.getvalue(), 
        mimetype=media
    )


# If ran as a script, create the required directories and run the flask application
if __name__ == "__main__":
    createDirectories()
    app.run(port=port, debug=True)
