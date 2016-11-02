# coding:utf-8
from support.dataManager import Manager
import time
from support.talibs import getInd,getIndicator
from account import Account,Order

class ActiveData(object):


    def __init__(self,maxLength=100):
        self.maxLength=maxLength
        self.columns=[]

    def importData(self,**kwargs):
        for k in kwargs:
            if k in self.columns:
                self.__getattribute__(k).insert(0,kwargs[k])
            else:
                self.__setattr__(k,[kwargs[k]])
                self.columns.append(k)

    def importOther(self,other,**kwargs):
        if hasattr(self,other):
            self[other].importData(**kwargs)
        else:
            self.__setattr__(other,ActiveData())
            self[other].importData(**kwargs)

    def __getitem__(self, item):
        if item is None:
            return self

        return getattr(self,item,None)

    def showAll(self):
        for c in self.columns:
            print self[c]


class OandaEngine(Manager):

    indinfo=[]
    T=0
    now={}
    data=ActiveData()
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
        # if ind[2] is None:
        #     ind[2]=self.symbol
        # else:
        #     obj=self.others.get(ind[2],[])
        #     if isinstance(ind[3],tuple):
        #         obj.extend(ind[3])
        #     else:
        #         obj.append(ind[3])
        #     self.others[ind[2]]=obj
        #
        # self.indinfo.append(tuple(ind))

        if ind[2] is not None:
            self.others[ind[2]]=ind[3]
        else:
            ind[2]=''

        self.indinfo.append(ind)

    def addSymbol(self,symbol,projection):
        self.others[symbol]=projection

    def __refreshOthers(self,t):
        for o in self.others:
            one=self.mDb[o].find_one({'time':{'$lte':t}},projection=self.others[o],sort=[('time',-1)])
            one.pop('_id',0)
            self.data.importOther(o,**one)

    def __refreshIndicator(self):
        for name,indicator,collection,Input,params in self.indinfo:
            inputs=[]
            Max=max(params.values())
            for ip in Input:
                inputs.append(self.data[collection][ip][Max-1::-1])

            ind=getInd(indicator,*inputs,**params)
            self.data[collection].importData(**{name:ind[-1]})

    def refresh(self,data):
        data.pop('_id',0)

        # 更新主数据
        self.data.importData(**data)
        # 更新附加数据
        self.__refreshOthers(data['time'])
        # 更新默认指标
        self.__refreshIndicator()


if __name__ == '__main__':
    engine=OandaEngine()

    engine.addSymbol('EUR_USD.D',['closeBid'])
    engine.addIndicator(['maFast','MA','EUR_USD.D',['closeBid'],{'timeperiod':10}])
    for i in engine.mDb['GBP_USD.D'].find(projection=['time','closeBid','openBid']).limit(30):
        engine.refresh(i)

    engine.data['EUR_USD.D'].showAll()
    print sum(engine.data['EUR_USD.D']['closeBid'][0:10])/10




