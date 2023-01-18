#!/usr/bin/env python

import os

save_dir = '/gws/pw/j07/nceo_aerosolfire/rsong/project/global_aerosol/Caliop/Download/2020_05_17'
os.system("wget --load-cookies ~/.urs_cookies --save-cookies ~/.urs_cookies --auth-no-challenge=on --keep-session-cookies --content-disposition -P %s -A '*2020-05-17*' -r -nd -np -nc -nH --cut-dirs=4 -e robots=off https://asdc.larc.nasa.gov/data/CALIPSO/LID_L2_05kmAPro-Standard-V4-20/2020/05/"%save_dir)