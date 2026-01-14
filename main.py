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


# Define the application
app = Flask(__name__)
app.secret_key = os.urandom(24)

def get_user():
    headers = {'Authorization': f'Bearer {ghToken}', 'X-Github-Api-Version': '2022-11-28'}
    r = requests.get('https://api.github.com/user', headers=headers)
    return r.json().get('login')

# Config variables
ghToken = os.environ["GITHUB_TOKEN"]
user = get_user()
micro-server-dir = config['config']['micro-server-dir']
backup-dir = config['config']['backup-dir']

def backupGhRepo(repo):
    try:
        os.system(f'git clone https://oauth2:{ghToken}@github.com/{user}/{repo}.git {backup-dir}/{repo}')
    except Exception as e:
        print(e)

#
#Just send a request to the github API and if it returns 200 then confirm that the API can be reached
def verifyGithubConnection():
    try:
        headers = {'Authorization': f'Bearer {ghToken}', 'X-Github-Api-Version': '2022-11-28'}
        r = requests.get('https://api.github.com/octocat', headers=headers)
        if r.status_code == 200:
            return 'API is working!'
        else:
            app.logger.warning(f'API HTTP return code: {r.status_code}')
            return 'Hmmm something is wrong. Please check the console for the status code'
    except Exception as e:
        app.logger.error(e)
        return 'Hmmm something is wrong. Please check the console.'

def getListOfGithubRepos():
    headers = {'Accept': 'application/vnd.github+json', 'Authorization': f'Bearer {ghToken}', 'X-GitHub-Api-Version': '2022-11-28'}
    r = requests.get('https://api.github.com/user/repos') # Change back to the directory this script is in


#def cdToScriptDir():
#    abspath = os.path.abspath(__file__)
#    print(abspath)
#    dname = os.path.dirname(abspath)
#    print(dname)
#    os.chdir(dname)

# Define main app route
@app.route('/')
def home():
    apiStatus = verifyGithubConnection()
    files = os.listdir('repos')
    return render_template('index.html', files=files, apistatus=apiStatus)

# Creates a new git repository using the git class
@app.route('/new-repo/<repo>')
def new_repo(repo):
    new_repo = Git(repo)
    del new_repo
    cdToScriptDir()
    flash(f'{repo} has been created successfully!', 'success')
    return redirect(url_for('home'))

# This route backs up the chosen repository from github
@app.route('/backupRepo', methods=['GET', 'POST'])
def backupRepo():
    if request.method == 'POST':
        chosen_repo = request.form.get('chosen_repo')
        backupGhRepo(chosen_repo)
        return redirect(url_for('home'))
   
    headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {ghToken}", "X-GitHub-Api-Version": "2022-11-28"}
    r = requests.get("https://api.github.com/user/repos", headers=headers)

    data = r.json()

    for i in data:
        name = i.get("name")
        repos.append(name)
   
    return render_template('repos.html', repos=repos)


# The Following code is part of the micro git server
@app.route('/<path:repo_path>/info/refs', methods=['GET'])
def info_refs(repo_path):
    service = request.args.get('service')

    if ".git" not in repo_path:
        repo_path = repo_path + '.git'
    
    real_path = Path(f'{micro-server-dir}/{repo_path}') 

    print(repo_path)

    if real_path.exists():
        repo = Git(str(real_path))
    else:
        repo = Git.init(str(real_path))

    data_io = repo.inforefs(service)
    
    # 5. Return a Flask Response (not StreamingResponse)
    media = f'application/x-{service}-advertisement'
    return Response(
        data_io.getvalue(), 
        mimetype=media
    )

@app.route('/<path:repo_path>/<service_name>', methods=['POST'])
def service_rpc(repo_path, service_name):
    real_path = Path(f'{micro-server-dir}/{repo_path}')
    repo = Git(str(real_path))

    # 1. Read input data from the request body
    # Your Git.service class uses .communicate(), so we need the whole body.
    input_data = request.data 
    
    # 2. Send to Git
    output_io = repo.service(service_name, input_data)

    # 3. Return Flask Response
    media = f'application/x-{service_name}-result'
    return Response(
        output_io.getvalue(), 
        mimetype=media
    )

if __name__ == "__main__":
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        file.close()
    app.run(port=8080, debug=True)
