#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/03/2023 15:17

lat_data = [1.1, 1.2, 1.3, 1.4, 5.1, 5.2, 5.4, 9.1, 9.2, 9.3, 3.3, 3.2, 3.1]

threshold = 2.0
sublists = [[0]]  # initialize with the index of the first value

i = 1
while i < len(lat_data):
    if abs(lat_data[i] - lat_data[sublists[-1][-1]]) >= threshold:
        sublists.append([i])
    else:
        sublists[-1].append(i)
    i += 1

print(sublists)
