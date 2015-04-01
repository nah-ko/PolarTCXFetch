#!/usr/bin/env python
import requests
import json

with open("settings.json", "r") as file:
    settings = json.load(file)

loginURL = "https://flow.polar.com/login"
