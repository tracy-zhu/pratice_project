# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 09:14:58 2018

@author: Tracy Zhu
"""
from WindPy import w

import sys

# 导入用户库：
sys.path.append("..")
out_file_folder = "..\\wind_api\\picture\\"
from python_base.plot_method import *


def download_data_wind(start_date, end_date, var_list):
    if w.isconnected() == False:
        w.start()
    raw = w.edb(var_list, start_date, end_date)
    raw_df = pd.DataFrame(raw.Data, index=raw.Codes, columns=raw.Times)
    raw_df = raw_df.T
    return raw_df


def eb_tb_dl(start_date, end_date, var_list):
    if w.isconnected() == False:
        w.start()
    csv_file_name = start_date + '_' + end_date + '.csv'
    if os.path.isfile(csv_file_name) is False:
        raw = w.edb(var_list, start_date, end_date)
        raw_df = pd.DataFrame(raw.Data, index=raw.Codes, columns=raw.Times)
        raw_df = raw_df.T
        close_df = raw_df
        close_df['time'] = close_df.index
        close_df.to_csv(csv_file_name, encoding='utf-8')
    else:
        close_df = pd.DataFrame.from_csv(csv_file_name)
    return close_df


def nation_debt_spread_and_index(start_date, end_date):
    """
    函数将10年期和2年期的国债收益率的利差作为一个序列
    另外一个序列是沪深300指数的序列日数据
    将这两个序列绘到一张图中
    代码列表分别是2年期国债，10年期国债，和沪深300指数
    :param start_date:
    :param end_date:
    :return:
    """
    var_list = ["M1001647", "M1001654", "M0020209"]
    raw_df = download_data_wind(start_date, end_date, var_list)
    yield_spread = raw_df[var_list[0]] - raw_df[var_list[1]]
    hs300_index = raw_df[var_list[2]]
    fig, ax = plt.subplots()
    ax.plot(yield_spread, color='r', label="yield_spread_2y_10y")
    ax1 = ax.twinx()
    ax1.plot(hs300_index, color="b", label="HS300index")
    ax.legend(loc="upper left")
    ax1.legend(loc="upper right")
    title = "HS300_index & 2y_10y_yield_spread"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)
    out_file_name = out_file_folder + title + ".png"
    plt.savefig(out_file_name)


def credit_spread_china(start_date, end_date):
    """
    用于画出中国1年期AAA级债券和AA级债券的利差
    双坐标轴，左坐标轴是两个债券的利率，右坐标轴是利差
    变量名列表分别是：中债企业债到期收益率AAA， 中债企业债到期收益率AA
    :param start_date:
    :param end_date:
    :return:
    """
    var_list = ["S0059771", "S0059761"]
    raw_df = download_data_wind(start_date, end_date, var_list)
    yield_spread = raw_df[var_list[1]] - raw_df[var_list[0]]
    fig, ax = plt.subplots()
    ax.plot(raw_df[var_list[0]], color='r', label="AAA bond 1 year")
    ax.plot(raw_df[var_list[1]], color='c', label="AA bond 1 year")
    ax1 = ax.twinx()
    ax1.plot(yield_spread, color="b", label="yield_spread")
    ax.legend(loc="upper left")
    ax1.legend(loc="upper right")
    title = "AAA bond and AA bond & spread in China"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)
    out_file_name = out_file_folder + title + ".png"
    plt.savefig(out_file_name)


def credit_spread_usa(start_date, end_date):
    """
    用于画出美国1年期国债和CCC级债券利差
    双坐标轴，左坐标轴是两个债券的利率，右坐标轴是利差
    变量名列表分别是：美国国债到期收益率：10年，美国：企业债收益率：美银美国高收益CCC或以下级企业债有效收益率
    :param start_date:
    :param end_date:
    :return:
    """
    var_list = ["M1001791", "G1139841"]
    raw_df = download_data_wind(start_date, end_date, var_list)
    yield_spread = raw_df[var_list[1]] - raw_df[var_list[0]]
    fig, ax = plt.subplots()
    ax.plot(raw_df[var_list[0]], color='r', label="usa 10Y bond")
    ax1 = ax.twinx()
    ax1.plot(yield_spread, color="b", label="yield_spread")
    ax.legend(loc="upper left")
    ax1.legend(loc="upper right")
    title = "USA national bonds 10Y and spread between CCC"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)
    out_file_name = out_file_folder + title + ".png"
    plt.savefig(out_file_name)


def credit_spread_eur(start_date, end_date):
    """
    用于画出欧洲德国一年期国债和意大利一年期国债差值收益率
    双坐标轴，左坐标轴是两个债券的利率，右坐标轴是利差
    变量名列表分别是：德国：国债收益率：10年，意大利：国债收益率：10年
    :param start_date:
    :param end_date:
    :return:
    """
    var_list = ["G0008068", "G1700020"]
    raw_df = download_data_wind(start_date, end_date, var_list)
    yield_spread = raw_df[var_list[1]] - raw_df[var_list[0]]
    fig, ax = plt.subplots()
    ax.plot(raw_df[var_list[0]], color='r', label="Germany 10Y bond")
    # ax.plot(raw_df[var_list[1]], color='c', label="Italy 10Y bond")
    ax1 = ax.twinx()
    ax1.plot(yield_spread, color="b", label="yield_spread")
    ax.legend(loc="upper left")
    ax1.legend(loc="upper right")
    title = "Germany&Italy national bonds 10Y and spread"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)
    out_file_name = out_file_folder + title + ".png"
    plt.savefig(out_file_name)


def eur_financial_condition(start_date, end_date):
    """
    欧洲金融条件：
    希腊：国债收益率10年： G8520070
    意大利：国债收益率10年：G1700020
    :param start_date:
    :param end_date:
    :return:
    """
    var_list = ["G8520070", "G1700020"]
    greece_10y_bond = download_data_wind(start_date, end_date, var_list[0])
    italy_10y_bond = download_data_wind(start_date, end_date, var_list[1])
    fig, ax = plt.subplots()
    ax.plot(greece_10y_bond, color='r', label="Greece 10Y bond")
    # ax.plot(raw_df[var_list[1]], color='c', label="Italy 10Y bond")
    ax1 = ax.twinx()
    ax1.plot(italy_10y_bond, color="b", label="Italy 10y bond")
    ax.legend(loc="upper left")
    ax1.legend(loc="upper right")
    title = "Greece&Italy national bonds 10Y and spread"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)
    out_file_name = out_file_folder + title + ".png"
    plt.savefig(out_file_name)


def A_bond_and_inverse_pe_index(start_date, end_date):
    """
    将中债商业银行普通收益率曲线（A): 1年 和 沪深300指数的PE值的倒数画在一张图上
    中债商业银行普通收益率曲线（A): 1 year : M1007749
    沪深300 PE: M0330172
    :param start_date:
    :param end_date:
    :return:
    """
    var_list = ["M1007749", "M0330172"]
    a_bond_yield = download_data_wind(start_date, end_date, var_list[0])
    pe_series = download_data_wind(start_date, end_date, var_list[1])
    inverse_pe = 1 / pe_series
    fig, ax = plt.subplots()
    ax.plot(a_bond_yield, color='r', label="A 1_year Bond Yield")
    # ax.plot(raw_df[var_list[1]], color='c', label="Italy 10Y bond")
    ax1 = ax.twinx()
    ax1.plot(inverse_pe, color="b", label="inverse_pe of HS300")
    ax.legend(loc="upper left")
    ax1.legend(loc="upper right")
    title = "A 1_year Bond Yield and Inverse_PE of HS300"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)
    out_file_name = out_file_folder + title + ".png"
    plt.savefig(out_file_name)


def total_match_volume_a_share_market(start_date, end_date):
    """
    双坐标：A股日换手率 和 A股日成交量
    成交量：上证A股指数： M0020198
    :param start_date:
    :param end_date:
    :return:
    """
    var_list = ["M0020198"]
    total_match_volume = download_data_wind(start_date, end_date, var_list[0])
    return total_match_volume


def TIPS_and_inflation_expecation(start_date, end_date):
    """
    双坐标： 10年期TIPS 和 10年期通胀预期
    10年期通胀预期 = 10年期国债 - 10年期TIPS
    国债名义收益率 = 实际收益率 + 预期通货膨胀率 + 通货风险溢价
    TIPS名义收益率 = 实际收益率 + 滞后的实际通胀率 + 流动性风险补偿
    TIPS: G0005428
    美国：国债收益率：10年： G0000891
    :param start_date:
    :param end_date:
    :return:
    """
    var_list = ["G0005428", "G0000891"]
    TIPS_value = download_data_wind(start_date, end_date, var_list[0])
    bond_10y = download_data_wind(start_date, end_date, var_list[1])
    inflation_expectation = bond_10y["G0000891"] - TIPS_value["G0005428"]
    fig, ax = plt.subplots()
    ax.plot(TIPS_value, color='r', label="TIPS 10 year bond")
    # ax.plot(raw_df[var_list[1]], color='c', label="Italy 10Y bond")
    ax1 = ax.twinx()
    ax1.plot(inflation_expectation, color="b", label="inflation_expectation")
    ax.legend(loc="upper left")
    ax1.legend(loc="upper right")
    title = "TIPS 10 year bond and inflation_expectation"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)
    out_file_name = out_file_folder + title + ".png"
    plt.savefig(out_file_name)


def NDF_and_CNH(start_date, end_date):
    """
    NDF和离岸人名币汇率
    USDCNH: 即期汇率 ： M0290205
    NDF 1 年期: M0068014
    :param start_date:
    :param end_date:
    :return:
    """
    var_list = ["M0290205", "M0068014"]
    CNH = download_data_wind(start_date, end_date, var_list[0])
    NDF_1y = download_data_wind(start_date, end_date, var_list[1])
    fig, ax = plt.subplots()
    ax.plot(CNH, color='r', label="offshore Yuan")
    # ax.plot(raw_df[var_list[1]], color='c', label="Italy 10Y bond")
    ax1 = ax.twinx()
    ax1.plot(NDF_1y, color="b", label="NDF 1 year")
    ax.legend(loc="upper left")
    ax1.legend(loc="upper right")
    title = "NDF 1 year and offshore Yuan"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)
    out_file_name = out_file_folder + title + ".png"
    plt.savefig(out_file_name)


def ivix_and_index(start_date, end_date):
    """
    函数是IVIX指数的变化和上证50和中证500指数的差值变化
    参考文献：海通证券：A股市场特征研究（三）--基于vix指数的风格轮动
    上证50指数： M0020223
    中证500指数：M0062541
    ivix: M0329695
    统计的结果为价差似乎是领先于ivix指数的，可以对50ETF期权的IVIX指数进行交易
    """
    var_list = ["M0020223", "M0062541", "M0329695"]
    index_50 = download_data_wind(start_date, end_date, var_list[0])
    index_500 = download_data_wind(start_date, end_date, var_list[1])
    ivix_index = download_data_wind(start_date, end_date, var_list[2])
    index_spread = 2 * index_50["M0020223"] - index_500["M0062541"]
    fig, ax = plt.subplots()
    ax.plot(ivix_index, color='r', label="ivix index")
    # ax.plot(raw_df[var_list[1]], color='c', label="Italy 10Y bond")
    ax1 = ax.twinx()
    ax1.plot(index_spread, color="b", label="spread between 2*SZ50 and ZZ500")
    ax.legend(loc="upper left")
    ax1.legend(loc="upper right")
    title = "ivix index and spread between 2*SZ50 and ZZ500"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)
    out_file_name = out_file_folder + title + ".png"
    plt.savefig(out_file_name)


def PMI_stat(start_date, end_date):
    """
    统计全球主要经济体PMI在50以上的国家，还有摩根大通全球加总的PMI指数
    都采用制造业PMI指数
    :return:
    wind代码表：
    {
    全球：摩根大通全球综合PMI: G8400008
    中国PMI指数： M0017126
    美国PMI: G0002323
    欧元区：制造业PMI: G0002299
    日本： 制造业PMI: G0002322
    中国香港：制造业PMI： G8300081
    中国台湾：制造业PMI: G0161979
    韩国：制造业PMI: 季调：G0399901
    马拉西亚：制造业PMI: G0719037
    印度：制造业： G0234905
    澳大利亚：G0006783
    英国： G0006318
    俄罗斯：G2000003
    土耳其：G2500001
    南非： G2317093
    加拿大：G1800212
    巴西：G0007421
    墨西哥：G2100341
    爱尔兰：G4200078
    沙特：G2400160
    阿联酋：G8459404
    捷克：G8500128
    波兰：G4500125
    埃及：G8459403
    西班牙：制造业PMI: G2700088
    德国：制造业PMI： G1500013
    法国：制造业PMI: G1400007
    意大利：制造业PMI: G1700004
    }
    """

    pmi_ratio_list = []
    pmi = None
    var_list = ["M0017126", "G0002323", "G0002299", "G0002322", "G8300081",
                "G0161979", "G0399901", "G0719037", "G0234905", "G0006783", "G0006318",
                "G2000003", "G2500001", "G2317093", "G1800212", "G0007421", "G2100341",
                "G4200078", "G2400160", "G8459404", "G8500128", "G4500125", "G8459403",
                "G2700088", "G1500013", "G1400007", "G1700004"]
    var_code = ["G8400008"]
    global_pmi_series = download_data_wind(start_date, end_date, var_code)
    index_date_list = global_pmi_series.index
    for index_date in index_date_list:
        n = 0
        pmi_list = []
        for var_code in var_list:
            print index_date, var_code
            pmi = download_data_wind(index_date, index_date, var_code)
            pmi_value = pmi.values[-1][-1]
            pmi_list.append(pmi_value)
            if pmi_value >= 50:
                n = n + 1
        pmi_ratio = float(n) / float(len(var_list))
        pmi_ratio_list.append(pmi_ratio)
    pmi_ratio_series = Series(pmi_ratio_list, index=index_date_list)
    fig, ax = plt.subplots()
    ax.plot(global_pmi_series, color='r', label="global pmi")
    ax1 = ax.twinx()
    ax1.plot(pmi_ratio_series, color="b", label="pmi ratio above 50")
    ax.legend(loc="upper left")
    ax1.legend(loc="upper right")
    title = "global pmi and pmi ratio above 50"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)
    out_file_name = out_file_folder + title + ".png"
    plt.savefig(out_file_name)



def different_country_stock(start_date, end_date):
    """
    画出美国，欧洲，摩根大通PMI
    :param start_date:
    :param end_date:
    :return:
    """
    global_var_code = ["G8400008"]
    global_pmi_series = download_data_wind(start_date, end_date, global_var_code)
    usa_var_code = ["G0002323"]
    usa_pmi_series = download_data_wind(start_date, end_date, usa_var_code)
    eur_var_code = ["G0002299"]
    eur_pmi_series = download_data_wind(start_date, end_date, eur_var_code)
    fig, ax = plt.subplots()
    ax.plot(global_pmi_series, color='r', label="JPMorgan global pmi")
    ax.plot(usa_pmi_series, color="b", label="usa pmi")
    ax.plot(eur_pmi_series, color="y", label="eur pmi")
    ax.legend(loc="upper left")
    title = "global PMI and usa , eur PMI"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)


def open_account_statics(start_date, end_date):
    """
    以周为单位统计投资者开户统计
    :param start_date:
    :param end_date:
    :return:
    """
    var_list = ["TR001827"]
    open_account = download_data_wind(start_date, end_date, var_list[0])
    return open_account


def revenue_generation(start_date, end_date):
    """
    计算财政税收收入，税收同比，税收收入：当月， 税收收入：累计同比
    税收收入：当月同比： M0024065
    税收收入：当月值：M0024057
    税收收入：累计同比：M0046171
    :param start_date:'2016-01-01"
    :param end_date:
    :return:
    """
    var_list = ["M0024065", "M0024057", "M0046171"]
    raw_df = download_data_wind(start_date, end_date, var_list)
    fig, ax = plt.subplots(figsize=(23.2, 14.0))
    ax.plot(raw_df["M0024065"], color='r', label='on year-on-year basis revenue')
    ax.legend(loc='best')
    title = "on year-on-year basis revenue"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)
    out_file_name = out_file_folder + title + ".png"
    plt.savefig(out_file_name)


def bank_yield_plot(start_date, end_date):
    """
    绘制银行理财产品预期年收益率：人民币：全市场：1周的利率
    :param start_date:
    :param end_date:
    :return:
    理财产品预期年收益率：人民币：全市场：1周          “M0074409"
    大型商业银行 ”M0074418"
    股份制银行 ：M0074427
    城市银行： “M0074436
    农村商业银行： M0075859
    外资银行： M0074445
    """
    var_list = ['M0074417', 'M0074426', 'M0074435', 'M0074444', 'M0075867']
    raw_df = download_data_wind(start_date, end_date, var_list)
    raw_df.columns = ["all_markets", "large commercial banks", "stock_holding_bank", "city bank", "country_bank"]
    raw_df.plot()
    fig1, ax1 = plt.subplots(figsize=(23.2, 14.0))
    yield_spread = raw_df['stock_holding_bank'] - raw_df['large commercial banks']
    ax1.plot(yield_spread, label='yield_spread')


def download_credit_and_loan_CHI(start_date, end_date):
    """
    下载国内的信贷数据，数据来源中国人民银行；
    数据为月调
    :param start_date:
    :param end_date:
    :return:
    """
    var_list = ["M0001486"]
    credit_and_loan = download_data_wind(start_date, end_date, var_list[0])
    fig, ax = plt.subplots(figsize=(23.2, 14.0))
    ax.plot(credit_and_loan, color='r', label='credit and loan')
    ax.legend(loc='best')
    title = "credit and loan in china"
    plt.title(title)
    fig.set_size_inches(23.2, 14.0)
    out_file_name = out_file_folder + title + ".png"
    plt.savefig(out_file_name)


if __name__ == '__main__':
    # var_list = pd.DataFrame.from_csv('for_haoran.csv')
    start_date = '2012-01-01'
    end_date = '2018-08-20'
    # eb_tb_dl(start_date, end_date, list(var_list['var']))
    # nation_debt_spread_and_index(start_date, end_date)
        # credit_spread_china(start_date, end_date)
        # credit_spread_usa(start_date, end_date)
        # credit_spread_eur(start_date, end_date)
    # TIPS_and_inflation_expecation(start_date, end_date)
    credit_spread_china(start_date, end_date)
    # A_bond_and_inverse_pe_index(start_date, end_date)
    # credit_spread_usa(start_date, end_date)
    # download_credit_and_loan_CHI(start_date, end_date)