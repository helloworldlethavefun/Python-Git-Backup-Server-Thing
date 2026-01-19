from crontab import CronTab
import os

user = os.environ['USER']
cron = CronTab(user=user)
currentDir = os.getcwd()

# Creates a cronjob scheduled to run at 6pm (18:00) every Sunday
def createCronJob(): 
    job = cron.new(command=f'{currentDir}/backupRepos.sh')
    job.setall('0 18 * * 7')
    cron.write()

def createLaunchDJob():
    pass

def createPythonJob():
    pass

def addToBackup(repo):
    with open('repos.txt', 'r+') as file:
        for line in file.readlines():
            if repo in line:
                continue
        file.write(repo + '\n')
        file.close()
