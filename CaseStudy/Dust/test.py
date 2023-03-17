#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/03/2023 15:17

import numpy as np
from scipy.spatial import cKDTree

lat_grid = np.random.uniform(-90, 90, size=(5000, 5000))
lon_grid = np.random.uniform(-180, 180, size=(5000, 5000))

lat_search = np.random.uniform(-90, 90, size=(1000, 1))
lon_search = np.random.uniform(-180, 180, size=(1000, 1))

coords = np.stack((lat_grid.ravel(), lon_grid.ravel()), axis=-1)
tree = cKDTree(coords)

search_points = np.hstack((lat_search, lon_search))
distances, indices = tree.query(search_points)

print(distances, indices)