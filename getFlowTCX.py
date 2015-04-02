#!/usr/bin/env python
import datetime
import requests
import json

with open("settings.json", "r") as file:
    settings = json.load(file)

startDate = "01.03.2015"
endDate  = "01.04.2015"
loginURL = "https://flow.polar.com/login"
myHeaders = {'user-agent':  'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}

login = requests.post(loginURL, 
                      data={"email":settings['polarflow_email'],"password":settings['polarflow_pass']}, 
                      headers=myHeaders)

activities = requests.get("https://flow.polar.com/training/getCalendarEvents?start=%s&end=%s" % (startDate,  endDate), 
                          cookies=login.cookies  )

#Get information only from 'EXERCISE' type activities found by:   activities.json[x]['type']
for activity in activities.json:
    if activity['type'] == 'EXERCISE':
        print("Fetch activity from: %s (ID: %s), TCX Url: https://flow.polar.com/%s/export/tcx" % (activity['datetime'],  activity['listItemId'],  activity['url']))
        tcxFile = requests.get("https://flow.polar.com/%s/export/tcx" % activity['url'], 
                               cookies=login.cookies
        )
        filename = "%s_%s.tcx" % (activity['listItemId'],  activity['datetime'])
        # Save the file locally, just in case.
        with file("archives/" + filename, "w") as f:
            f.write(resp.text.encode("UTF-8"))
