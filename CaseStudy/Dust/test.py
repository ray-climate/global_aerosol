#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/03/2023 15:17

def test_lat_sublists():
    # create test data
    latitude_all = [10, 20, 30, 35, 40, 50, 55, 60, 70, 60, 50, 40]
    lat_jump_threshold = 10

    # expected output
    expected = [[0, 1, 2], [3], [4, 5], [6], [7, 8]]

    # run the function
    lat_sublists = [[0]]
    j = 1
    while j < len(latitude_all):
        if abs(latitude_all[j] - latitude_all[lat_sublists[-1][-1]]) >= lat_jump_threshold:
            lat_sublists.append([j])
        else:
            lat_sublists[-1].append(j)
        j += 1

    # compare the actual output to the expected output
    print(lat_sublists)

test_lat_sublists()
