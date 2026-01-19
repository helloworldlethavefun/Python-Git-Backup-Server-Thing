from crontab import CronTab
import os

user = os.environ['USER']
cron = CronTab(user=user)

# Creates a cron job
def addCronJob(repo):
    pass
