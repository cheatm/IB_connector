# coding:utf-8
from datetime import datetime,timedelta
import Queue
import threading
import pymongo

class TimeJoiner(object):

    __waiting=Queue.Queue()
    __finish=Queue.Queue()
    __run=False

    def __init__(self,**how):
        if 'collection' in how:
            self.collection=how.pop('collection')
            self.dealFinished=self.__saveCollection
        else:
            self.dealFinished=self.__putQueueFinished

        self.setUnit(**how)
        self.doc={}
        self.__run=False
        self.__joinThread=threading.Thread(target=self.joiner)

    def setUnit(self,**how):
        index=0
        Times=['month','week','day','hour','minute','second']

        self.slip=how
        for t in how:
            newi=Times.index(t)
            if index<newi:
                index=newi
            how['%ss' % t]=how.pop(t)

        self.ignore={}

        for t in Times[index+1:]:
            self.ignore[t]=0

        self.delta=timedelta(**how)
        print self.delta

    def start(self):
        self.__run=True
        self.__joinThread.start()

    def stop(self):
        self.__run=False
        self.__joinThread.join()

    def joiner(self):
        while self.__run or self.__waiting.qsize():
            doc=self.__waiting.get()
            self.join(doc)

    def join(self,doc):
        self.doc=doc
        self.periodEnd=doc['datetime'].replace(**self.ignore)+self.delta
        self.join=self.__join

    def __join(self,doc):
        if doc['datetime']<self.periodEnd:
            if doc['highMid']>self.doc['highMid']:
                self.doc['highMid']=doc['highMid']
            if doc['lowMid']<self.doc['lowMid']:
                self.doc['lowMid']=doc['lowMid']
            self.doc['volume']+=doc['volume']
            self.doc['closeMid']=doc['closeMid']
        else:
            self.dealFinished(self.doc.copy())
            self.doc=doc
            self.periodEnd=doc['datetime'].replace(**self.ignore)+self.delta

    def dealFinished(self,doc):
        pass

    def __saveCollection(self,doc):
        self.collection.insert_one(doc)

    def __putQueueFinished(self,doc):
        self.__finish.put(self.doc.copy())

    def getFinished(self):
        import pandas
        finish=[]
        while self.__finish.qsize():
            finish.append( self.__finish.get())
        return pandas.DataFrame(finish)

    def put(self,doc):
        self.__waiting.put(doc)

if __name__ == '__main__':
    # client=pymongo.MongoClient(port=10001)
    # joiner=TimeJoiner(hour=1,collection=client.test['EUR_USD.H1'])
    # collection=client.Oanda['EUR_USD.M1']
    #
    # joiner.start()
    # for doc in collection.find({'datetime':{'$gte':datetime(2016,11,12)}}):
    #     doc.pop('_id')
    #     joiner.put(doc)
    #
    # joiner.stop()

    dt=datetime.now()
    dt.replace()

