#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test.py
# @Author:      Dr. Rui Song
# @Email:       rui.song@physics.ox.ac.uk
# @Time:        06/03/2023 15:17

import numpy as np

# Define the function to integrate
def f(x):
    return x**2

# Define the range of integration and the number of points
a = 0
b = 3
num_points = 100

# Create an array of x values
x = np.linspace(a, b, num_points)

# Evaluate the function at each x value
y = f(x)

# Use the trapz function to compute the integral
integral = np.trapz(y[::-1], x[::-1])

print("Integral of x^2 from 0 to 3:", integral)
