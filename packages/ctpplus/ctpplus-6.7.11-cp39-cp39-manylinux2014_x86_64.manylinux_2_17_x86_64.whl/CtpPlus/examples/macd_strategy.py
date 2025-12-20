# -*- codeing:utf-8 -*-
'''
@author: syealfalfa
@datetime: 2024/7/11 9:44
@Blog: lhxtApi提供历史行情数据
'''
import copy
import datetime

from dateutil.relativedelta import relativedelta

import csv
import os

import talib as tb
import numpy as np
import pandas as pd
from multiprocessing import Process, Queue

from CtpPlus.CTP.ApiStruct import QryInstrumentField
from CtpPlus.CTP.MdApi import run_bar_engine
from CtpPlus.CTP.TraderApiBase import TraderApiBase, to_str

from CtpPlus.CTP.FutureAccount import FutureAccount, get_simulate_account


from lhxtApi.futures_base import FuturesBase


class Client(FuturesBase):
    def __init__(self):
        super().__init__()

    def on_futures_day_data(self, data):
        print(data)

    def on_futures_bar_data(self, data):
        print(data)

    def on_futures_tick_data(self, data):
        print(data)


def calculate_kdj(df):
    """计算kdj"""
    low_list = df['LowestPrice'].rolling(9, min_periods=9).min()
    low_list.fillna(value=df['LowestPrice'].expanding().min(), inplace=True)
    high_list = df['HighestPrice'].rolling(9, min_periods=9).max()
    high_list.fillna(value=df['HighestPrice'].expanding().max(), inplace=True)
    rsv = (df['ClosePrice'] - low_list) / (high_list - low_list) * 100
    df['K'] = pd.DataFrame(rsv).ewm(com=2).mean()
    df['D'] = df['K'].ewm(com=2).mean()
    df['J'] = 3 * df['K'] - 2 * df['D']

    k = np.array(df['K'])
    d = np.array(df['D'])
    j = np.array(df['J'])

    return k, d, j


def calculate_macd(df, fast_period=12, slow_period=26, signal_period=9):
    """计算MACD"""
    # 计算快速移动平均线
    ema_fast = df['ClosePrice'].ewm(span=fast_period, min_periods=fast_period).mean()
    # 计算慢速移动平均线
    ema_slow = df['ClosePrice'].ewm(span=slow_period, min_periods=slow_period).mean()
    # 计算离散化MACD
    macd = ema_fast - ema_slow
    # 计算MACD信号线
    signal = macd.ewm(span=signal_period, min_periods=signal_period).mean()
    # 计算MACD柱状图
    hist = (macd - signal) * 2
    return pd.DataFrame({'DIFF': macd, 'DEA': signal, 'MACD': hist})


def change_instrumentID(datas):
    """修改合约ID"""
    SYMBOLS = {}
    for data in datas:
        symbol = to_str(data)
        letters = ''.join(ch for ch in symbol if ch.isalpha())
        numbers = ''.join(num for num in symbol if num.isdigit())
        if len(numbers) <= 3:
            new_numbers = '2' + numbers
            symbol = letters.lower() + new_numbers
        else:
            symbol = letters.lower() + numbers
        SYMBOLS[data] = symbol
    return SYMBOLS


def bar_to_csv(bar):
    """将bar数据保存至本地"""
    bar['InstrumentID'] = to_str(bar['InstrumentID'])
    bar['UpdateTime'] = to_str(bar['UpdateTime'])
    bar['TradingDay'] = to_str(bar['TradingDay'])
    bar['ActionDay'] = to_str(bar['ActionDay'])
    file_name = '.'.join([bar['InstrumentID'], 'csv'])
    flag = os.path.exists(f'./{file_name}')
    print(os.path.join(os.getcwd(), file_name))
    with open(file_name, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=bar.keys())
        if not flag:
            # 写入表头
            writer.writeheader()

        writer.writerow(bar)


def read_csv(file_name):
    """读取csv文件数据"""
    df = pd.read_csv(file_name, encoding='utf-8')
    return df


class AuthenticateHelper(TraderApiBase):
    def __init__(self, broker_id, td_server, investor_id, password, app_id, auth_code, md_queue=None, flow_path='',
                 private_resume_type=2, public_resume_type=2, production_mode=True):
        pass

    def init_extra(self):
        """
        初始化策略参数
        :return:
        """
        self.symbol_day_data = {}   # 日线数据
        self.d_flag = {}  # 日线交叉标记
        self.m30_flag = {}  # 30分钟线交叉标记
        self.m5_flag = {}  # 5分钟线交叉标记
        self.symbol_data = {}  # 分钟线数据
        self.parameter_dict = self.md_queue.get(block=False)

        self.client = Client()
        ip = '101.132.121.188:8080'
        rt = self.client.session('xxxxx', 'xxxxx', ip)
        print(f'rt = {rt}')

        # start_date = '2024.05.01'
        # end_date = '2024.07.24'
        start_date = datetime.datetime.now() - relativedelta(days=20)
        end_date = datetime.datetime.now()
        # start_date = start_date.strftime('%Y.%m.%d')
        # end_date = end_date.strftime('%Y.%m.%d')

        SYMBOLS = change_instrumentID(self.parameter_dict['ProfitLossParameter'].keys())

        struct = {
            'close_list': [],  # 收盘价
            'hight_list': [],  # 最高价
            'low_list': []     # 最低价
        }
        VAL = -200

        for symbol in self.parameter_dict['ProfitLossParameter'].keys():
            self.symbol_data[symbol] = copy.deepcopy(struct)
            df = self.client.get_futures_bar_data(symbols=[to_str(SYMBOLS[symbol])], start_datetime=start_date,
                                                  end_datetime=end_date, frequency='30m', flag=True)

            if not df.empty:
                self.symbol_data[symbol]['close_list'].extend(df['ClosePrice'].tolist()[VAL:])
                self.symbol_data[symbol]['hight_list'].extend(df['HighestPrice'].tolist()[VAL:])
                self.symbol_data[symbol]['low_list'].extend(df['LowestPrice'].tolist()[VAL:])
                # print(self.symbol_data[symbol])
            else:
                print(f'合约：{symbol} ==> 无历史数据')

            file_name = '.'.join([to_str(symbol), 'csv'])
            if os.path.exists(f'./{file_name}'):
                bar = read_csv(file_name)
                self.symbol_data[symbol]['close_list'].extend(bar['LastPrice'].tolist())
                self.symbol_data[symbol]['hight_list'].extend(bar['HighPrice'].tolist())
                self.symbol_data[symbol]['low_list'].extend(bar['LowPrice'].tolist())
            else:
                print(f'{file_name} ：文件不存在！')

    def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
        self.write_log('OnRspUserLogin', pRspUserLogin)

        # 查询合约
        # pQryInstrument = QryInstrumentField()
        # self.ReqQryInstrument(pQryInstrument)

    def OnRspQryInstrument(self, pInstrument, pRspInfo, nRequestID, bIsLast):
        """请求查询合约响应"""
        if pInstrument['ProductClass'] == b'1':
            self.write_log('OnRspQryInstrument', pInstrument['InstrumentID'])

    def OnRtnInstrumentStatus(self, pInstrumentStatus):
        pass

    def OnRtnOrder(self, pOrder):
        self.write_log('OnRtnOrder', pOrder)

    def OnRtnTrade(self, pTrade):
        self.write_log('OnRtnTrade', pTrade)

    def Join(self):
        while True:
            if self.md_queue.empty():
                continue
            else:
                self.bar = self.md_queue.get(block=False)

                if '15:01:00' <= to_str(self.bar["UpdateTime"]) < '21:00:00' or '02:31:00' <= to_str(self.bar["UpdateTime"]) < '09:00:00':
                    continue

                bar_to_csv(copy.deepcopy(self.bar))
                # print(self.bar)

                symbol = self.bar['InstrumentID']
                self.symbol_data[symbol]['close_list'].append(self.bar['LastPrice'])
                self.symbol_data[symbol]['hight_list'].append(self.bar['HighPrice'])
                self.symbol_data[symbol]['low_list'].append(self.bar['LowPrice'])
                ma_5 = tb.SMA(np.array(self.symbol_data[symbol]['close_list']), timeperiod=5)
                ma_34 = tb.SMA(np.array(self.symbol_data[symbol]['close_list']), timeperiod=34)

                dictionary = {
                    'HighestPrice': self.symbol_data[symbol]['hight_list'],
                    'LowestPrice': self.symbol_data[symbol]['low_list'],
                    'ClosePrice': self.symbol_data[symbol]['close_list']
                }
                df = calculate_macd(df=pd.DataFrame.from_dict(dictionary))
                diff, dea, macd = df['DIFF'].tolist(), df['DEA'].tolist(), df['MACD'].tolist()
                print(diff)
                print(dea)
                print(macd)


def run_api(api_cls, account, md_queue=None):
    if isinstance(account, FutureAccount):
        trader_engine = api_cls(
            account.broker_id,
            account.server_dict['TDServer'],
            account.investor_id,
            account.password,
            account.app_id,
            account.auth_code,
            md_queue,
            account.td_flow_path
        )
        trader_engine.Join()


def run_trader_engine(account, md_queue=None):
    run_api(AuthenticateHelper, account, md_queue)


if __name__ == '__main__':
    # 止盈止损参数
    pl_parameter = {
        'StrategyID': 9,
        'ProfitLossParameter': {
            b'ag2504': {'0': [10], '1': [10]},  # 沪银    # '0'代表止盈, '1'代表止损
            # b'SA409': {'0': [20], '1': [20]},   # 纯碱
        },
    }

    # 账户配置
    instrument_id_list = []
    for instrument_id in pl_parameter['ProfitLossParameter']:
        instrument_id_list.append(instrument_id)
    future_account = get_simulate_account(
        investor_id='',  # SimNow账户
        password='',  # SimNow账户密码
        subscribe_list=instrument_id_list,  # 合约列表
        server_name='电信1',  # 电信1、电信2、移动、TEST
        period='1m'  # 1分钟
    )

    # 共享队列
    share_queue = Queue(maxsize=100)
    share_queue.put(pl_parameter)

    # 行情进程
    md_process = Process(target=run_bar_engine, args=(future_account, [share_queue]))
    # 交易进程
    trader_process = Process(target=run_trader_engine, args=(future_account, share_queue))

    #
    md_process.start()
    trader_process.start()

    #
    md_process.join()
    trader_process.join()
