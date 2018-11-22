# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 13:57:19 2017

# 将收益和两个参数，以三维图的方式展示出来

@author: Tracy Zhu
"""
# coding:utf-8

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.axes3d import Axes3D

instrument_id_1 = "RB1710"
instrument_id_2 = 'RB1801'
frequency = '15min'
limit_change = 0

result_file = '.\\option_strategy\\result\\3d_profit.txt'
x = []
y = []
z = []
f = open(result_file, 'r')
lines = f.readlines()
for line in lines:
    sample_period, prediction_period, correction_prob = line.split(',')
    x.append(sample_period)
    y.append(prediction_period)
    z.append(correction_prob)


f.close()

# string型转int型
x = [float(x) for x in x if x]
y = [float(y) for y in y if y]
z = [float(z) for z in z if z]

fig = plt.figure()
ax = Axes3D(fig)
# ax.scatter3D(x, y, z)
ax.plot_trisurf(x,y,z)
ax.set_xlabel('limit_num')
ax.set_ylabel('holding_period')
ax.set_zlabel('mean_pct')
plt.show()