# coding: utf-8

import MySQLdb
from pylab import *
import  xml.dom.minidom
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

mpl.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题

database_ip = "10.47.102.126"

def get_k_daily_data_from_database(instrument_id_1, instrument_id_2):
    # 连接数据库
    con = MySQLdb.connect(host=database_ip, user="root", passwd="123456", port=3306, db="info1", local_infile=1,
                          charset='gbk')
    cursor = con.cursor()
    command = "select instrument_id, trading_day, close_price from daily_k_data_test where instrument_id = \'%s\' or instrument_id = \'%s\' order by trading_day, instrument_id" % (instrument_id_1, instrument_id_2)
    cursor.execute(command)

    con.commit()
    data_get = cursor.fetchall()
    con.close()
    return data_get

# 接口供改变价差的计算方式, 返回的是价差
def change_price_delta_calculation(price1, price2):
    delta = price1 - 2 * price2 - 1000
    return delta


if __name__ == '__main__':
    # 打开xml文档
    dom = xml.dom.minidom.parse('config.xml')
    # 得到文档元素对象
    root = dom.documentElement
    instrument_id_1 = root.getElementsByTagName('instrument_id_1')
    instrument_id_2 = root.getElementsByTagName('instrument_id_2')
    # 读取配置文件的合约号
    id_1 = str(instrument_id_1[0].firstChild.data)
    id_2 = str(instrument_id_2[0].firstChild.data)

    # id_1 = 'PP1709'
    # id_2 = 'MA709'

    price_data_list = get_k_daily_data_from_database(id_1, id_2)

    x_list = []
    y_list = []
    price_1 = 0
    price_2 = 0
    trading_day_control = 0
    for data in price_data_list:
        print data
        if trading_day_control == 0:
            trading_day_control = data[1]
            price_1 = data[2]
            continue
        if trading_day_control ==  data[1]:
            price_2 = data[2]
            price_delta = change_price_delta_calculation(price_1, price_2)
            x_list.append(trading_day_control)
            y_list.append(price_delta)
        else:
            trading_day_control = data[1]


    # length_of_two_instrument_id = len(price_data_list)
    # length_of_one_instrument_id = length_of_two_instrument_id / 2
    #
    # x_list = []
    # y_list = []
    # for index in range(length_of_one_instrument_id):
    #     price_1_index = 2*index
    #     price_2_index = 2*index+1
    #     if price_data_list[price_1_index][0] != id_1:
    #         price_1_index = 2*index+1
    #         price_2_index = 2*index
    #     trading_date_1 = price_data_list[price_1_index][1]
    #     trading_date_2 = price_data_list[price_2_index][1]
    #     if trading_date_1 == trading_date_2:
    #         # 第一个合约的价格
    #         price_1 = price_data_list[price_1_index][2]
    #         # 第二个合约的价格
    #         price_2 = price_data_list[price_2_index][2]
    #         ###
    #         ### 自定义的价差方式
    #         price_delta = change_price_delta_calculation(price_1, price_2)
    #         # print trading_date_1, price_1, price_2, price_delta
    #
    #         x_list.append(str(trading_date_1))
    #         y_list.append(price_delta)


    group_labels = []
    i = 0
    for index in range(len(x_list)):
        if i % 5 == 0:
            group_labels.append(x_list[index])
        else:
            group_labels.append('')
        i += 1

    # xy标签
    plt.xlabel(u"日期")
    plt.ylabel(u"价差")
    # 标题
    title11 = id_1 + u"和" + id_2 + u"的价差关系曲线"
    plt.title(title11)

    x_list_last = range(0, len(y_list))

    # group_labels = x_list

    plt.plot(x_list_last, y_list, 'b', linewidth=0.5)


    # 横坐标设置(坐标代替,倾斜度)
    plt.xticks(x_list_last, group_labels, rotation=30)
    # 网格线
    plt.grid()

    plt.show()
