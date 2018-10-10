# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 10:27:52 2016

# 脚本用于画出两个合约日线之间的价差

@author: Tracy Zhu
"""

import os, sys
import logging
import statsmodels.formula.api as smf

# 导入用户库：：
sys.path.append("..")
from python_base.plot_method import *
