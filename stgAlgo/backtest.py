# coding:utf-8
import time
import datetime

class BackTestSystem():

    def __init__(self,strategy):
        self.strategy=strategy
        self.engine=strategy.engine

    def set_collection(self,collection):
        self.engine.set_collection(collection)

    def run(self,collection,start=0,end=time.time(),**params):
        '''

        :param collection: 基础数据
        :param start: 开始时间 timestamp or datetime
        :param end: 结束时间 timestamp or datetime
        :param params: 策略参数 (包括点数point，point默认为1)
        :return:
        '''

        start=time.mktime(start.timetuple()) if isinstance(start,datetime.datetime) else start
        end=time.mktime(end.timetuple()) if isinstance(end,datetime.datetime) else end

        # 初始化engine
        self.engine.OnInit(collection=collection,point=params.pop('point',1))

        # 初始化策略，包括将设置好的默认数据和指标信息传入engine
        self.strategy.set_params(**params)
        self.strategy.OnInit(collection=collection,data=self.engine.data)

        if self.engine.collection is None:
            raise AttributeError('No specific collection, try set_collection()')

        cursor=self.engine.collection.find(
            {'time':{'$gte':start,'$lte':end}},
            self.engine.projection
        )

        print self.engine.data.point

        times=0
        for c in cursor:
            self.engine.refresh(c)
            self.strategy.onBar(self.engine.data)
            times+=1
            if not times%50:
                self.engine.data.clearAll()

        self.engine.finish()

        return self.engine.acc


if __name__ == '__main__':
    from stgAlgo.strategy import StrategyDemo
    from stgAlgo.backtestengine import OandaEngine
    import oanda_point as op

    # 导入策略，引擎指针给策略
    demo=StrategyDemo(OandaEngine())
    # 策略导入回测系统
    backtest=BackTestSystem(demo)
    # 回测 输出账户返回回测完后的账户（包含交易信息）
    acc=backtest.run(collection='GBP_USD.D',start=datetime.datetime(2016,9,1),point=op.GBP_USD)

    # 输出账户中的交易信息
    print acc.getHistoryOrders()
    for log in sorted(acc.log.keys()):
        print log,acc.log[log]
