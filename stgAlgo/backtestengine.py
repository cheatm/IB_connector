# coding:utf-8
from support.dataManager import Manager
import time
from support.talibs import getInd,getIndicator
from account import Account,Order
import pandas



class OandaEngine(Manager):

    indinfo=[]
    T=0
    now={}
    data=pandas.DataFrame()
    others={}

    def __init__(self,**kw):

        self.acc=kw.pop('account',Account())
        if 'db' not in kw:
            kw['db']='Oanda'
        self.initMongoClient(**kw)


    def set_collection(self,collection):
        self.collection=self.mDb[collection]
        self.symbol=collection

    def setDefaultCollection(self,db,col):
        self.set_collection(col)

    def get(self,shift=0,range=None,projection=None):
        # 获取默认collection的数据
        return self.__get(self.collection,shift,range,projection)

    def get_mongo(self,db,collection,shift=0,range=None,projection=None):
        # 获取指定定db和collection的数据
        return self.__get(self.mClient[db][collection],shift,range,projection)

    def __get(self,collection,shift=0,range=None,projection=None):
        cursor=collection.find({'time':{'$lte':self.now['time']}},projection=projection).sort('time',-1)
        if range is None:
            return cursor[shift]
        else:
            return cursor[range[0]:range[1]]

    def buy(self,**kw):

        self.acc.openOrder(code=kw.pop('symbol',self.symbol),
                           price=kw.pop('price',self.now['cloesBid']),
                           lots=kw.pop('lots',1),
                           **kw
                           )

    def sell(self,**kw):

        self.acc.closeOrder(kw.pop('price',self.now['closeBid']),**kw)

    def addIndicator(self,ind):
        if ind[2] is None:
            ind[2]=self.symbol
        else:
            obj=self.others.get(ind[2],[])
            if isinstance(ind[3],tuple):
                obj.extend(ind[3])
            else:
                obj.append(ind[3])
            self.others[ind[2]]=obj



        self.indinfo.append(tuple(ind))

    def refresh(self,data):
        self.now=data
        self.data=self.data.append(pandas.DataFrame([data]))
        for info in self.indinfo:
            pass


if __name__ == '__main__':
    engine=OandaEngine()
    engine.addIndicator(['ma1','ma','GBP_USD.D',('closeBid')])
    # engine.addIndicator(['ma2','ma','GBP_USD.D',('closeBid')])
    print engine.others
