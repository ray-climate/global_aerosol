
###
# !/usr/bin/python

# Example URL
username = "ruisong123"
password = "Lztxdy.862210"
url = "https://asdc.larc.nasa.gov/data/CALIPSO/LID_L2_05kmAPro-Standard-V4-20/2020/05/CAL_LID_L2_05kmAPro-Standard-V4-20.2020-05-20T06-30-56ZN.hdf"

import requests

with requests.Session() as session:
    session.auth = (username, password)

    r1 = session.request('get', url)

    r = session.get(r1.url, auth=(username, password))

    if r.ok:
        print(r.content)  # Say

