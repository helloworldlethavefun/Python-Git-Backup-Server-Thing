from crontab import CronTab
import os

user = os.environ['USER']
cron = CronTab(user=user)


