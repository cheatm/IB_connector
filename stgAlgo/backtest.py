# coding:utf-8
import time
import datetime
from sTree import Params
import pandas

class BackTestSystem():

    def __init__(self):
        pass

    @staticmethod
    def analysis(acc,**kwargs):
        log=acc.getLog()
        history=acc.getHistoryOrders()

        log.insert(2,'MAX',[log['capital'].loc[0:i].max() for i in log.index])
        log['return']=log['MAX']-log['capital']
        log['return_per']=log['return']/log['MAX']
        MAX_return=log['return'].max()
        kwargs['Calmar_Ratio']=(log.get_value(log.index[-1],'capital')-log.get_value(log.index[0],'capital'))/MAX_return
        profit=history['profit']
        kwargs['Profit_Factor']=profit[history['profit']>0].sum()/abs(profit[history['profit']<0].sum())
        kwargs['Lots_Total']=int(history['lots'].abs().sum())
        kwargs['Trade_Times']=len(history.index)

        return kwargs

    def optimize(self,strategy,engine,colletion,start=0,end=datetime.datetime.now(),begin=0,point=1,
                 analysis=None,**params):
        if analysis is None:
            analysis=BackTestSystem.analysis
        eParame=params.pop('engine_param',{})
        print params
        opParams=Params(**params)

        output=pandas.DataFrame(columns=list(params.keys()))

        n=1.0
        l=len(opParams)
        for p in opParams:
            Engine=engine(**eParame)
            Engine.acc=Engine.acc.copy()
            acc=self.run(strategy,Engine,colletion,start,end,begin,**p)
            output=output.append(analysis(acc,**p),True)
            print '%.2f%%' % (n/l*100)
            n+=1
        return output



    def run(self,strategy,engine,collection,start=0,end=datetime.datetime.now(),begin=0,point=1,**params):
        '''

        :param collection: 基础数据
        :param start: 开始时间 timestamp or datetime
        :param end: 结束时间 timestamp or datetime
        :param params: 策略参数 (包括点数point，point默认为1)
        :return:
        '''
        strategy=strategy(engine)

        # 初始化engine
        engine.OnInit(collection=collection,point=point)

        # 初始化策略，包括将设置好的默认数据和指标信息传入engine
        strategy.set_params(**params)
        strategy.OnInit(collection=collection,data=engine.data)

        if engine.collection is None:
            raise AttributeError('No specific collection, try set_collection()')

        start=engine.collection.find({'datetime':{'$lte':start}},sort=[('datetime',-1)]).skip(begin)[0]['datetime']

        cursor=engine.collection.find(
            {'datetime':{'$gte':start,'$lte':end}},
            engine.projection
        )

        for c in cursor.clone()[:begin]:
            engine.refresh(c)

        for c in cursor[begin:]:
            engine.refresh(c)
            strategy.onBar(engine.data)


        engine.finish()

        return engine.acc



if __name__ == '__main__':
    from stgAlgo.strategy import StrategyDemo
    from stgAlgo.backtestengine import OandaEngine
    import oanda_point as op

    backtest=BackTestSystem()
    # 回测 输出账户返回回测完后的账户（包含交易信息）
    acc=backtest.run(StrategyDemo,OandaEngine(),collection='GBP_USD.D',start=datetime.datetime(2016,9,1),point=op.GBP_USD)

    # 输出账户中的交易信息
    print acc.getHistoryOrders()
    for log in sorted(acc.log.keys()):
        print log,acc.log[log]
