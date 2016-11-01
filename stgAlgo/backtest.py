# coding:utf-8
import time

class BackTestSystem():

    def __init__(self,strategy):
        self.strategy=strategy
        self.engine=strategy.engine

    def set_collection(self,collection):
        self.engine.set_collection(collection)

    def run(self,start=0,end=time.time(),collection=None,**params):

        cursor=self.engine.collection.find(
            {'time':{'$gte':start,'$lte':end}}
        )

        if collection is not None:
            self.set_collection(collection)

        if self.engine.collection is None:
            raise AttributeError('No specific collection, try set_collection()')

        self.strategy.onInit()
        self.strategy.set_params(**params)

        for c in cursor:
            self.engine.refresh(c)
            self.strategy.onBar(**c)
