#!/usr/bin/env python
from datetime import datetime,  timedelta
import requests
import json
import zipfile
import StringIO

with open("settings.json", "r") as f:
    settings = json.load(f)

# Start from 'sync_days' before today
today = datetime.now()
firstDate = today - timedelta(days = settings['sync_days'])
startDate = firstDate.strftime("%d.%m.%Y")
endDate  = today.strftime("%d.%m.%Y")
# Give website a User-Agent who won't be rejected...
myHeaders = {'user-agent':  'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}

login = requests.post("https://flow.polar.com/login", 
                      data={"email":settings['polarflow_email'],"password":settings['polarflow_pass']}, 
                      headers=myHeaders)

activities = requests.get("https://flow.polar.com/training/getCalendarEvents?start=%s&end=%s" % (startDate,  endDate), 
                          cookies=login.cookies  )

#Get information only from 'EXERCISE' type activities found by:   activities.json[x]['type']
for activity in activities.json:
    if activity['type'] == 'EXERCISE':
        print("Fetch activity from: %s (ID: %s), TCX Url: https://flow.polar.com%s/export/tcx" % (activity['datetime'],  activity['listItemId'],  activity['url']))
        tcxFile = requests.get("https://flow.polar.com%s/export/tcx" % activity['url'], 
                               cookies=login.cookies
        )
        # Polar Flow exports activities in zipfiles, so we need to get it and then extract all files.
        try:
            zipDoc = zipfile.ZipFile(StringIO.StringIO(tcxFile.content))
        except:
            print("Error extracting file: not a zip file")
            continue
        zipDoc.extractall("archives/")
