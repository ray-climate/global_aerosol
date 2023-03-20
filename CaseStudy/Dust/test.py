#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/03/2023 15:17

import matplotlib.pyplot as plt

# Sample data
temperatures = [15, 14, 12, 10, 8, 6, 5, 3, 15, 20, 25, 27, 30, 33, 35, 38, 40, 42, 45, 48, 50, 52, 55, 58, 60]
heights = [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600, 2800, 3000, 3200, 3400, 3600, 3800, 4000, 4200, 4400, 4600, 4800, 5000]

# Calculate height intervals
height_intervals = [heights[i+1] - heights[i] for i in range(len(heights)-1)]

# Create a bar chart
fig, ax = plt.subplots()
ax.barh(heights[:-1], temperatures, height_intervals, align='edge', edgecolor='black', linewidth=1, facecolor='none')

# Label the axes
ax.set_xlabel('Temperature')
ax.set_ylabel('Height')

# Show the plot
plt.show()
