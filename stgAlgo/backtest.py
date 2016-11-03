# coding:utf-8
import time


class BackTestSystem():

    def __init__(self,strategy):
        self.strategy=strategy
        self.engine=strategy.engine

    def set_collection(self,collection):
        self.engine.set_collection(collection)

    def run(self,start=0,end=time.time(),collection=None,**params):

        # 初始化策略，包括将设置好的默认数据和指标信息传入engine
        self.strategy.set_params(**params)
        self.strategy.OnInit()

        # 初始化engine，初始化data服务
        self.engine.OnInit(collection=collection)
        if self.engine.collection is None:
            raise AttributeError('No specific collection, try set_collection()')

        cursor=self.engine.collection.find(
            {'time':{'$gte':start,'$lte':end}},
            self.engine.projection
        )

        for c in cursor:
            self.engine.refresh(c)
            self.strategy.onBar(self.engine.data)

if __name__ == '__main__':
    from stgAlgo.strategy import StrategyDemo
    from stgAlgo.backtestengine import OandaEngine
    demo=StrategyDemo(OandaEngine())
    backtest=BackTestSystem(demo)
    backtest.run(collection='GBP_USD.D')

