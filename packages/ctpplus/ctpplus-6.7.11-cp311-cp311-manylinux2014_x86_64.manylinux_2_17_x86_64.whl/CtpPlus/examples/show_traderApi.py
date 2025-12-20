# -*- codeing:utf-8 -*-
'''
@author: syealfalfa
@datetime: 2025/10/28 9:37
@log: 接口展示
'''
import datetime
import threading
import time
from typing import Dict, List

from CtpPlus.CTP.ApiConst import (InstrumentStatus_Continous,
                                  InstrumentStatus_Closed,
                                  PosiDirection_Long,
                                  Direction_Buy,
                                  PosiDirection_Short,
                                  Direction_Sell)
from CtpPlus.CTP.MdApiBase import MdApiBase
from CtpPlus.ta.time_bar import tick_to_bar
from CtpPlus.utils.base_field import to_bytes

import numpy as np
from multiprocessing import Process, Queue

from CtpPlus.CTP.ApiStruct import (QryInstrumentMarginRateField,
                                   QryInstrumentCommissionRateField,
                                   QryOrderField,
                                   QryTradeField,
                                   QryExchangeField,
                                   QryInvestorField, QryDepthMarketDataField)

from CtpPlus.CTP.TraderApiBase import TraderApiBase, to_str, HedgeFlag_Speculation

from CtpPlus.CTP.FutureAccount import FutureAccount, get_simulate_account


class TickEngine(MdApiBase):
    """行情接口类"""
    def __init__(self, broker_id, md_server, investor_id=b'', password=b'', app_id=b'', auth_code=b'',
                 subscribe_list=None, md_queue_list=None, flow_path='', using_udp=False, multicast=False,
                 production_mode=True, period='1m'):
        super(TickEngine, self).__init__()

    def init_extra(self):
        pass

    def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
        """登录请求响应"""
        self.write_log('OnRspUserLogin', pRspUserLogin)

        # # 退订合约
        # self.UnSubscribeMarketData([b'ag2512'])
        # # 重新订阅合约
        # self.SubscribeMarketData([b'ag2512'])

    def OnRspUserLogout(self, pUserLogout, pRspInfo, nRequestID, bIsLast):
        """登出请求响应"""
        self.write_log('OnRspUserLogout', pUserLogout)

    def OnRtnDepthMarketData(self, pDepthMarketData):
        """深度行情通知"""
        # 将行情放入共享队列
        # self.write_log('OnRtnDepthMarketData', pDepthMarketData)
        for md_queue in self.md_queue_list:
            md_queue.put(pDepthMarketData)

    def OnRspQryMulticastInstrument(self, pMulticastInstrument, pRspInfo, nRequestID, bIsLast):
        """请求查询组播合约响应"""
        self.write_log('OnRspQryMulticastInstrument', pMulticastInstrument)

    def OnRspUnSubMarketData(self, pSpecificInstrument, pRspInfo, nRequestID, bIsLast):
        """取消订阅行情应答"""
        self.write_log('OnRspUnSubMarketData', pSpecificInstrument)


class TraderEngine(TraderApiBase):
    """交易接口类"""
    def __init__(self, broker_id, td_server, investor_id, password, app_id, auth_code, md_queue=None, flow_path='',
                 private_resume_type=2, public_resume_type=2, production_mode=True):
        super(TraderEngine, self).__init__()

    def init_extra(self):
        """
        初始化策略参数
        :return:
        """
        self.parameter_dict = self.md_queue.get(block=False)

    def scheduled_task(self):
        """定时任务"""
        task = threading.Thread(target=self.init_ctp_data)
        task.start()

    def init_ctp_data(self) -> None:
        """初始化数据"""
        # 查询投资者
        pQryInvestor = QryInvestorField(BrokerID=self.broker_id, InvestorID=self.investor_id)
        self.ReqQryInvestor(pQryInvestor)

        # 请求查询报单
        # self.query_order()
        pQryOrder = QryOrderField(BrokerID=self.broker_id, InvestorID=self.investor_id, ExchangeID=b'SHFE')
        self.ReqQryOrder(pQryOrder)
        time.sleep(1)

        # 请求查询成交
        # self.query_trade()
        pQryTrade = QryTradeField(BrokerID=self.broker_id, InvestorID=self.investor_id, ExchangeID=b'SHFE')
        self.ReqQryTrade(pQryTrade)
        time.sleep(1)

        # 请求查询资金账户
        self.query_trading_account()
        time.sleep(1)

        # 查询总持仓
        self.query_position()
        time.sleep(1)

        # 查询所有持仓明细
        self.query_position_detail()
        time.sleep(1)

        pre_symbols = self.parameter_dict['ProfitLossParameter'].keys()  # 获取订阅的合约
        for symbol in pre_symbols:
            # 请求查询合约保证金率（投机）
            p_instrument_margin_rate = QryInstrumentMarginRateField(BrokerID=self.broker_id,
                                                                    InvestorID=self.investor_id,
                                                                    HedgeFlag=HedgeFlag_Speculation,
                                                                    InstrumentID=symbol)
            self.ReqQryInstrumentMarginRate(p_instrument_margin_rate)
            time.sleep(1)

            # 请求查询合约手续费率
            p_qry_instrument_commission_rate = QryInstrumentCommissionRateField(BrokerID=self.broker_id,
                                                                                InvestorID=self.investor_id,
                                                                                InstrumentID=symbol)
            self.ReqQryInstrumentCommissionRate(p_qry_instrument_commission_rate)
            time.sleep(1)

        # 查询全部合约信息
        self.query_instrument()
        time.sleep(1)

        # 请求查询行情
        # pQryDepthMarketData = QryDepthMarketDataField(InstrumentID=b'ag2412', ProductClass=b'1')
        # self.ReqQryDepthMarketData(pQryDepthMarketData)
        # time.sleep(1)

        # 查询交易所
        # pQryExchange = QryExchangeField(ExchangeID=b'SHFE')
        # self.ReqQryExchange(pQryExchange)
        # time.sleep(1)

        # 查询API版本信息
        # version = self.GetApiVersion(self)
        # self.write_log('GetApiVersion', version)
        # time.sleep(1)

        # 请求查询经纪公司交易参数
        # pQryBrokerTradingParams = QryBrokerTradingParamsField(BrokerID=self.broker_id, InvestorID=self.investor_id)
        # self.ReqQryBrokerTradingParams(pQryBrokerTradingParams)
        # time.sleep(1)

        # 投资者申报费阶梯收取记录查询
        # pQryInvestorInfoCommRec = QryInvestorInfoCommRecField()
        # self.ReqQryInvestorInfoCommRec(pQryInvestorInfoCommRec)

    def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
        """投资者结算结果确认响应（自动确认）"""
        self.write_log('OnRspSettlementInfoConfirm', pSettlementInfoConfirm)

        # 启动查询任务
        self.scheduled_task()

    def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
        self.write_log('OnRspUserLogin', pRspUserLogin)

    def OnRspQryInstrument(self, pInstrument, pRspInfo, nRequestID, bIsLast):
        """请求查询合约响应"""
        if pInstrument['ProductClass'] == b'1':
            if pInstrument['InstrumentID'] in self.parameter_dict['ProfitLossParameter'].keys():
                self.write_log('OnRspQryInstrument', pInstrument)

    def OnRspQryTradingAccount(self, pTradingAccount, pRspInfo, nRequestID, bIsLast):
        """请求查询资金响应"""
        self.write_log('OnRspQryTradingAccount', pTradingAccount)

    def OnRspQryInstrumentMarginRate(self, pInstrumentMarginRate, pRspInfo, nRequestID, bIsLast):
        """请求查询合约保证金率响应"""
        self.write_log('OnRspQryInstrumentMarginRate', pInstrumentMarginRate)

    def OnRspQryInstrumentCommissionRate(self, pInstrumentCommissionRate, pRspInfo, nRequestID, bIsLast):
        """请求查询合约手续费率响应"""
        self.write_log('OnRspQryInstrumentCommissionRate', pInstrumentCommissionRate)

    def OnRspQryInvestorPosition(self, pInvestorPosition, pRspInfo, nRequestID, bIsLast):
        """请求查询投资者持仓响应"""
        self.write_log('OnRspQryInvestorPosition', pInvestorPosition)

    def OnRspQryInvestorPositionDetail(self, pInvestorPositionDetail, pRspInfo, nRequestID, bIsLast):
        """请求查询投资者持仓明细响应"""
        self.write_log('OnRspQryInvestorPositionDetail', pInvestorPositionDetail)

    def OnRspQryDepthMarketData(self, pDepthMarketData, pRspInfo, nRequestID, bIsLast):
        """请求查询行情响应"""
        self.write_log('OnRspQryDepthMarketData', pDepthMarketData)

    def OnRspQryOrder(self, pOrder, pRspInfo, nRequestID, bIsLast):
        """请求查询报单响应"""
        self.write_log('OnRspQryOrder', pOrder)

    def OnRspQryTrade(self, pTrade, pRspInfo, nRequestID, bIsLast):
        """请求查询成交响应"""
        self.write_log('OnRspQryTrade', pTrade)

    def OnRspQryExchange(self, pExchange, pRspInfo, nRequestID, bIsLast):
        """请求查询交易所响应"""
        pExchange['ExchangeName'] = to_str(pExchange['ExchangeName'])
        self.write_log('OnRspQryExchange', pExchange)

    def OnRspQryInvestor(self, pInvestor, pRspInfo, nRequestID, bIsLast):
        """请求查询投资者响应"""
        self.write_log('OnRspQryInvestor', pInvestor)

    def OnRspOrderInsert(self, pInputOrder, pRspInfo, nRequestID, bIsLast):
        """报单录入请求响应"""
        self.write_log('OnRspOrderInsert', pInputOrder)

    def OnRspOrderAction(self, pInputOrderAction, pRspInfo, nRequestID, bIsLast):
        """报单操作请求响应"""
        self.write_log('OnRspOrderAction', pInputOrderAction)

    def OnRtnInstrumentStatus(self, pInstrumentStatus):
        """
        合约交易状态通知，主动推送。公有流回报
        开盘时合约状态为: 2
        """
        self.write_log('OnRtnInstrumentStatus', pInstrumentStatus)

    def OnRtnOrder(self, pOrder):
        """报单通知"""
        self.write_log('OnRtnOrder', pOrder)

    def OnRtnTrade(self, pTrade):
        """成交通知"""
        self.write_log('OnRtnTrade', pTrade)


def run_td_api(api_cls, account, md_queue=None):
    if isinstance(account, FutureAccount):
        trader_engine = api_cls(
            account.broker_id,
            account.server_dict['TDServer'],
            account.investor_id,
            account.password,
            account.app_id,
            account.auth_code,
            md_queue,
            account.td_flow_path,
            production_mode=account.production_mode
        )

        return trader_engine


def run_md_api(api_cls, account, md_queue_list=None):
    if isinstance(account, FutureAccount):
        tick_engine = api_cls(
            account.broker_id,
            account.server_dict['MDServer'],
            account.investor_id,
            account.password,
            account.app_id,
            account.auth_code,
            account.subscribe_list,
            md_queue_list,
            account.md_flow_path,
            production_mode=account.production_mode,
            period=account.period
        )

        return tick_engine


def run_trader_engine(account, md_queue=None):
    return run_td_api(TraderEngine, account, md_queue)


def run_bar_engine(account, md_queue_list):
    return run_md_api(TickEngine, account, md_queue_list)


class Test:
    def __init__(self):
        # 止盈止损参数
        pl_parameter = {
            'StrategyID': 9,
            'ProfitLossParameter': {
                b'ag2512': {'0': [10], '1': [10]},  # 沪银    # '0'代表止盈, '1'代表止损
                b'SA601': {'0': [20], '1': [20]},   # 纯碱
                # b'i2601': {'0': [20], '1': [20]},   # 铁矿石
                # b'rb2601': {'0': [20], '1': [20]},  # 螺纹
            }
        }

        self.share_queue = Queue(maxsize=100)  # 共享队列(存放行情数据)
        self.share_queue.put(pl_parameter)

        self.instrument_id_list = list(pl_parameter['ProfitLossParameter'].keys())

        future_account = get_simulate_account(
            investor_id='',  # SimNow账户
            password='',  # SimNow账户密码
            subscribe_list=self.instrument_id_list,  # 合约列表
            server_name='电信1'  # 电信1、电信2、移动、TEST
        )
        self.mdApi = run_bar_engine(future_account, [self.share_queue])  # 行情接口API
        self.traderApi = run_trader_engine(future_account, self.share_queue)  # 交易接口API

        self.traderApi.GetApiVersion(self.traderApi)

    def run(self):
        """算法逻辑"""
        while True:
            if not self.share_queue.empty():
                print(self.share_queue.get(block=False))  # 打印行情数据

            # self.traderApi.insert_order(exchange_id, instrument_id, order_price, order_vol, Direction_Buy, OffsetFlag_Open)

            # 买开仓
            # self.traderApi.buy_open(b'SHFE', b'ag2512', 12000, 1)
            #
            # # 卖开仓
            # self.traderApi.sell_open(b'SHFE', b'ag2512', 12000, 1)
            #
            # # 买平仓
            # self.traderApi.buy_close(b'SHFE', b'ag2512', 12000, 1)
            #
            # # 卖平仓
            # self.traderApi.sell_close(b'SHFE', b'ag2512', 12000, 1)

            # 撤单
            # order_ref和order_sysid 出现在报单通知OnRtnOrder中
            # self.traderApi.cancel_order(b'SHFE', b'ag2512', order_ref, order_sysid=b'')


if __name__ == '__main__':
    test = Test()
    test.run()

