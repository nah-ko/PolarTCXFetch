#!/usr/bin/env python
import requests,  json,  zipfile,  StringIO,  os,  shutil
from datetime import datetime,  timedelta
from lxml import objectify

with open("settings.json", "r") as f:
    settings = json.load(f)

# Start from last time synchronization was done (with lastsync.dat file),
# if file doesn't exists, start from 'sync_days' before today
today = datetime.now()
try:
    fd = open("lastsync.dat",  "r")
    D = fd.read()
    fd.close()
    firstDate = datetime.strptime(D,  "%d.%m.%Y")
except:
    print("Problem reading lastsync.dat (file missing or unreadable)")
    firstDate = today - timedelta(days = settings['sync_days'])
startDate = firstDate.strftime("%d.%m.%Y")
endDate  = today.strftime("%d.%m.%Y")
# Write last time we synchronize into lastsync.dat
fd = open("lastsync.dat",  "w")
fd.write(endDate)
fd.close()
# Give website a User-Agent who won't be rejected...
myHeaders = {'user-agent':  'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}

print("Connecting to Polar Flow webapp...")

login = requests.post("https://flow.polar.com/login", 
                      data={"email":settings['polarflow_email'],"password":settings['polarflow_pass']}, 
                      headers=myHeaders)
login.raise_for_status()
#if login.raise_for_status():
#    print("Ooopss!! Something went wrong...\nError is: {}".format(login.raise_for_status()))
#    exit(1)

print("Connected!\nRequesting last unsync activities since {}...".format(startDate))

activities = requests.get("https://flow.polar.com/training/getCalendarEvents?start=%s&end=%s" % (startDate,  endDate), 
                          cookies=login.cookies  )

#Get information only from 'EXERCISE' type activities found by:   activities.json[x]['type']
# 4 Jul 2015: activities.json no longer work (no reason)
print("Fetch {} activities.".format(activities.content.count('EXERCISE')))
for activity in json.loads(activities.content):
    if activity['type'] == 'EXERCISE':
        print("Fetch activity from: %s (ID: %s);\n\tTCX Url: https://flow.polar.com%s/export/tcx/true" % (activity['datetime'],  activity['listItemId'],  activity['url']))
        tcxFile = requests.get("https://flow.polar.com%s/export/tcx/true" % activity['url'], 
                               cookies=login.cookies
        )
        # Make sure there is a directory where to download files, if not we'll create it
        archivesDir = settings['archives_dir']
        if not os.path.exists(archivesDir):
            os.mkdir(archivesDir)
        # Polar Flow exports activities in zipfiles, so we need to get it and then extract all files.
        try:
            zipDoc = zipfile.ZipFile(StringIO.StringIO(tcxFile.content))
        except:
            print("Error extracting file: not a zip file")
            continue
        zipDoc.extractall(archivesDir)
        tcxFileName = zipDoc.filelist[0].filename
        # Extract activity type from TCX file, value is stored into <Activity> tag, by "Sport" attribute.
        tcxTree = objectify.parse(archivesDir+tcxFileName)
        Root = tcxTree.getroot()
        Activity = Root.Activities.Activity
        ActivityType = Activity.attrib['Sport']
        # If ActivityType is "Other", then we know that Polar give real sport name information in filename
        if ActivityType == 'Other':
            tcxFileName_Right = tcxFileName.split('_')[1]
            ActivityType = str(tcxFileName_Right.split('.')[0])
        # Move file to the associated sport type directory
        sourceFile = archivesDir + tcxFileName
        destDir = archivesDir + ActivityType + '/'
        try:
            if not os.path.exists(destDir):
                os.mkdir(destDir)
            shutil.move(sourceFile, destDir)
            print("Activity (type: {}) saved to: {}/{}".format(ActivityType,  destDir,  tcxFileName))
        except (shutil.Error,  IOError, os.error), why:
            print("Unable to move {} to {} because of error: {}".format(sourceFile, destDir, str(why)))
            if why.find('already exists') != -1:
                print("Removing existing file {}".format(tcxFileName))
                shutil.remove(sourceFile)

print("Every training file is yours !")
