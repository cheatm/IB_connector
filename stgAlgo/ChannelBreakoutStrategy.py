# coding:utf-8
from backtest import BackTestSystem
from backtestengine import OandaEngine
from strategy import Strategy
from support.talibs import getInd,getIndicator
from datetime import datetime

def CI(cur,pre,high,low):
    '''

    :param cur: 当前
    :param pre: 末尾
    :param high: 最高
    :param low: 最低
    :return:
    '''
    return  (cur-pre)/pre*100/((high-low)/low)


class BreakOut(Strategy):

    ci_p=50
    high=150
    low=150
    atr_period=14

    def OnInit(self,**kw):
        self.setIndicator('ci')

        pass

    def onBar(self,data):

        self.Exit(data)

        direction=self.Filter(data)

        if direction:

            self.Entry(data,direction)


    def Exit(self,data):
        highest=max(data.highMid[-self.high:-1])
        lowest=min(data.lowMid[-self.low:-1])
        # 当前最高大于过去最高
        if data.highMid[-1]>highest:
            for order in self.getAccount().orders:
                if order.lots<0:
                    self.close(order=order) #平空

        if data.lowMid[-1]<lowest:
            for order in self.getAccount().orders:
                if order.lots<0:
                    self.close(order=order)


    def Entry(self,data,direction):
        # 计算当前atr
        atr=getInd('ATR',
                   data.highMid[-self.atr_period-1:],
                   data.lowMid[-self.atr_period-1:],
                   data.closeMid[-self.atr_period-1:],
                   timeperiod=self.atr_period
                   )[-1]
        # 做多
        if direction==1 :
            highest=max(data.highMid[-self.high:-1])
            if data.highMid[-1]>highest:
                # print data.datetime[-1],'ATR',atr
                self.open(price=highest,lots=1,stoplost=atr,takeprofit=atr*3)
            return
        # 做空
        if direction==-1:
            lowest=min(data.lowMid[-self.low:-1])
            if data.lowMid[-1]<lowest:
                # print data.datetime[-1],'ATR',atr
                self.open(price=lowest,lots=1,stoplost=atr,takeprofit=atr*3)


    def Filter(self,data):
        # 计算CI
        ci = CI(data.closeMid[-1],
                data.closeMid[-self.ci_p],
                max(data.highMid[-self.ci_p:]),
                min(data.lowMid[-self.ci_p:]),
                )
        print data.datetime[-1],ci
        data.importData(ci={'ci':ci,'datetime':data.datetime[-1]})

        # 返回direction
        if ci>20:
            return 1
        elif ci<-20:
            return -1
        else:
            return 0

from oanda_point import EUR_USD
import pandas
if __name__ == '__main__':
    engine=OandaEngine()
    stg=BreakOut(engine)
    system=BackTestSystem(stg)
    acc=system.run('EUR_USD.D',start=datetime(2014,1,1),begin=150,point=EUR_USD,atr_period=14)
    collection=engine.mClient.OutPut['CI']
    collection.insert(engine.data.ci)

    history= acc.getHistoryOrders()

    collection=engine.mClient.OutPut['breakout']
    history.drop(['ticket','lots'],1,inplace=True)
    for i in history.index:
        collection.insert_one( history.loc[i].to_dict())

    # print pandas.DataFrame(acc.log)



    # print getInd('ATR',data.highMid[0:16],data.lowMid[0:16],data.closeMid[0:16],timeperiod=14)
    # print getInd('ATR',data.highMid,data.lowMid,data.closeMid,timeperiod=14)

