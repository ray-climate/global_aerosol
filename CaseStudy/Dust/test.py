#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/03/2023 15:17

import matplotlib.pyplot as plt

circle_cross = plt.Circle((0,0), radius=1, fill=False, linestyle='--')
fig, ax = plt.subplots()
ax.set_aspect('equal')
ax.add_artist(circle_cross)
ax.axhline(y=0, color='k', linestyle='--')
ax.axvline(x=0, color='k', linestyle='--')
plt.show()