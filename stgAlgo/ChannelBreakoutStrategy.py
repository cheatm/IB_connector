# coding:utf-8
from backtest import BackTestSystem
from backtestengine import OandaEngine
from strategy import Strategy
from support.talibs import getInd,getIndicator
from datetime import datetime,timedelta
from GUI.backtestFigure import BackTestOutPut
from bokeh.plotting import figure,output_file,show
import oanda_point

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
    direction=0

    def OnInit(self,**kw):
        self.setIndicator('ci')
        self.setIndicator('highest',value=[2])
        self.setIndicator('lowest',value=[0])

        pass

    def onBar(self,data):
        data.importData(highest=max(data.highMid[-self.high:]))
        data.importData(lowest=min(data.lowMid[-self.low:]))

        self.Exit(data)

        direction=self.Filter(data)


        if direction:

            self.Entry(data,direction)

    def Exit(self,data):

        # 当前最高大于过去最高
        if data.highest[-1]>data.highest[-2]:
            for order in self.getAccount().orders:
                if order.lots<0:
                    self.close(order=order) #平空

        if data.lowest[-1]<data.lowest[-2]:
            for order in self.getAccount().orders:
                if order.lots>0:
                    self.close(order=order)

    def Entry(self,data,direction):
        # 计算当前atr
        atr=getInd('ATR',
                   data.highMid,
                   data.lowMid,
                   data.closeMid,
                   timeperiod=self.atr_period
                   )[-1]
        # 做多
        if direction==1 and self.direction!=-1:
            for o in self.getAccount().orders:
                if o.lots>0:
                    return
            if data.highest[-1]>data.highest[-2]:
                self.open(price=data.highest[-2],lots=1,stoplost=atr,takeprofit=atr*4)
            return
        # 做空
        if direction==-1 and self.direction!=1:
            for o in self.getAccount().orders:
                if o.lots<0:
                    return
            if data.lowest[-1]<data.lowest[-2]:
                self.open(price=data.lowest[-2],lots=-1,stoplost=atr,takeprofit=atr*4)



    def Filter(self,data):
        # 计算CI
        ci = CI(data.closeMid[-1],
                data.closeMid[-self.ci_p],
                max(data.highMid[-self.ci_p:]),
                min(data.lowMid[-self.ci_p:]),
                )
        data.importData(ci={'ci':ci,'datetime':data.datetime[-1]})

        # 返回direction
        if ci>20:
            return 1
        elif ci<-20:
            return -1
        else:
            return 0

def analysis(acc,**kwargs):
        log=acc.getLog()
        history=acc.getHistoryOrders()

        log.insert(2,'MAX',[log['capital'].loc[0:i].max() for i in log.index])
        log['return']=log['MAX']-log['capital']
        log['return_per']=log['return']/log['MAX']
        MAX_return=log['return'].max()
        kwargs['Calmar_Ratio']=log.get_value(log.index[-1],'capital')/MAX_return
        profit=history['profit']
        kwargs['Profit_Factor']=profit[history['profit']>0].sum()/abs(profit[history['profit']<0].sum())
        kwargs['Lots_Total']=int(history['lots'].abs().sum())
        kwargs['Trade_Times']=len(history.index)

        return kwargs

from account import Account

def Sample():
    engine=OandaEngine(account=Account(10000,50))
    system=BackTestSystem()
    timeSlip=engine.mClient.OutPut['COT_ROC_25_cur'].find().toDataFrame()

    upRange=[]
    downRange=[]

    up=[timeSlip['1'][0],timeSlip['datetime'][0]]
    down=[timeSlip['-1'][0],timeSlip['datetime'][0]]
    for i in timeSlip.index[1:]:
        if timeSlip['-1'][i]!=down[0]:
            down.append(timeSlip['datetime'][i])
            if down[0]!='---':
                downRange.append(down)
                print 'down',down
            down=[timeSlip['-1'][i],timeSlip['datetime'][i]]
        if timeSlip['1'][i]!=up[0]:
            up.append(timeSlip['datetime'][i])
            if up[0]!='---':
                upRange.append(up)
                print 'up',up
            up=[timeSlip['1'][i],timeSlip['datetime'][i]]

    for s,start,end in downRange:
        collection='%s_USD.H1' % s if s not in ['CAD','JPY'] else 'USD_%s.H1' % s

        acc_down=system.run(BreakOut,engine,collection,
            start=start,end=end,begin=150,point=getattr(oanda_point,collection[:-3]),direction=-1)

    # return acc_down


    engine=OandaEngine(account=Account(10000,50))

    for s,start,end in upRange:
        collection='%s_USD.H1' % s
        direction=1

        if s in ['CAD','JPY']:
            collection='USD_%s.H1' % s
            direction=-1


        acc_up=system.run(BreakOut,engine,collection,
            start=start,end=end,begin=150,point=getattr(oanda_point,collection[:-3]),direction=direction)

    return acc_up,acc_down




if __name__ == '__main__':
    # engine=OandaEngine()
    # engine.acc.lever=50
    # system=BackTestSystem()
    # acc=system.run(BreakOut,engine,
    #     'EUR_USD.H4',start=datetime(2014,1,1),begin=150,point=oanda_point.EUR_USD,atr_period=14)
    # print acc.getHistoryOrders()

    # print analysis(acc)
    # output=system.optimize(BreakOut,OandaEngine,
    #     'EUR_USD.D',start=datetime(2014,1,1),begin=150,point=EUR_USD,atr_period=list(range(12,15)),
    #     ci_p=list(range(40,61,5)))
    # print output

    # BackTestOutPut(acc,engine.data,height=200).plot(y='ci',n=1,legend='ci')\
    #     .plot(y='highest',color='#dd99cc').plot(y='lowest',color='#dd99cc')\
    #     .show('breakout.html')

    import pandas

    acc_up,acc_down=Sample()
    history_up=acc_up.getHistoryOrders()
    log_up=acc_up.getLog()
    history_down=acc_down.getHistoryOrders()
    log_down=acc_down.getLog()
    log=pandas.merge(log_up[['datetime','capital']],log_down[['datetime','capital']],'outer','datetime')
    log=log.sort('datetime').drop_duplicates('datetime').set_index('datetime')
    log['capital_x'][log.index[0]]=10000
    last_x=10000
    last_y=10000
    for i in log.index[1:]:
        x=log.get_value(i,'capital_x')
        y=log.get_value(i,'capital_x')
        if not x>0:
            log.set_value(i,'capital_x',last_x)
        else:
            last_x=x
        if not y>0:
            log.set_value(i,'capital_y',last_y)
        else:
            last_y=y

    log['capital']=log['capital_y']+log['capital_x']
    print log

    # print acc.getLog()

    # output_file('timeSlip.html')
    # plot=figure(width=1400,height=300,x_axis_type='datetime')
    #
    # plot.line(x=log['datetime'],y=log['capital'])
    # show(plot)





