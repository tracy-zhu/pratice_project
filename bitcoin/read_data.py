# -*- coding: utf-8 -*-

import sys
import pandas as pd

sys.path.append("..")

file_name = '.\\bitcoin\\executions_20w.csv'

df = pd.read_csv(file_name, parse_dates=['timestamp'])
df_sort = df.sort_values(by='timestamp')

df_sort[['timestamp', 'price']].set_index('timestamp').plot(figsize=(18,9))
price_change = df_sort['price'].diff()
price_change.hist()
price_change.describe()
abs_price_change = price_change.abs()
ratio = float(sum(abs_price_change > 1)) / len(abs_price_change)
print "ratio is " + str(ratio)

f = open(file_name, "r")
lines = f.readlines()
for line in lines[:1:-1]:
    line_list = line.split(",")
    direction = line_list[1]
    order_price = line_list[2]
    order_volume = line_list[3]
    update_time = line_list[4]
    print line_list[0]