# coding:utf-8
import time

class Strategy(object):

    def __init__(self,engine,**kw):

        self.engine=engine

    def set_params(self,**params):
        for p in params:
            if hasattr(self,p):
                self.__setattr__(p,params[p])
            else:
                raise AttributeError("No param names '%s' " % p)

    def set_engine(self,engine):
        self.engine=engine

    def OnInit(self,**kw):
        '''
        初始化策略，在策略启动前调用，
        某些function需要写在当中，需要用户重写

        :param kw:
        :return:
        '''
        pass

    def setIndicator(self,name,indicator,collection,*inputs,**params):
        '''
        添加常驻指标信息
        需要重写OnInit方法并在OnInit中调用该方法设置常驻指标

        :param name: 名字，可以通过onBar(Data) 中的data[name] 调用
        :param indicator:  talib中的指标
        :param collection: 计算指标的数据库 None表示默认
        :param inputs:  计算指标的数据：'closeBid' ...
        :param params: 计算指标所需的参数 参考talib
        :return:

        在onBar(data)中的调用方法：
            data[collection][name][item]
            data[name][item]

        '''
        self.engine.addIndicator([name,indicator,collection,inputs,params])

    def addSymbol(self,symbol,projection):
        '''
        添加其他常驻数据信息
        需要重写OnInit方法并在OnInit中调用该方法添加其他常驻数据

        :param symbol: 其他常驻数据的来源数据 collection
        :param projection: collection中需要获取的数据
        :return:

        在onBar中调用方法：
            data[symbol][item]

        '''
        self.engine.addSymbol(symbol,projection)
        pass

    def onBar(self,data):
        pass

    def open(self,**order):
        self.engine.open(**order)

    def close(self,**order):
        self.engine.close(**order)

    def get(self,**kw):
        return self.engine.get(**kw)

class StrategyDemo(Strategy):

    fast=5
    slow=10

    def OnInit(self,**kw):
        self.setIndicator('maFast','MA',None,'closeBid',timeperiod=self.fast)
        self.setIndicator('maSlow','MA',None,'closeBid',timeperiod=self.slow)
        self.setIndicator('maSlow','MA','EUR_USD.D','closeBid',timeperiod=self.slow)


    def onBar(self,data):

        if data.maFast[0]>data.maSlow[0] and data.maFast[0]>data.maFast[1]:
            self.open()



# if __name__ == '__main__':
#     s=Strategy()