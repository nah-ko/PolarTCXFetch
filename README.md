# PolarTCXFetch
Polar Flow TCX file download
This script intend to download training file from Polar Flow (http://flow.polar.com) web interface.

## Instructions
1. Copy settings-sample.json to settings.json and enter your Polar Flow credentials;
2. Enter the synchronisation days back in the past;
3. Give location of the archives directory where TCX files will be stored;
4. Run the script.

## Description
This script log into Flow web application, request for your activities (depending on last day you synchronise your files) and download them as training files (aka TCX files).
If the directory needed doesn't exists, it'll be created for you.

