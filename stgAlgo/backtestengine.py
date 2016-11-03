# coding:utf-8
from support.dataManager import Manager
import time
from support.talibs import getInd,getIndicator
from account import Account,Order

class ActiveData(object):


    def __init__(self,name,maxLength=100):
        self.name=name
        self.maxLength=maxLength
        self.columns=[]

    def importData(self,**kwargs):
        for k in kwargs:
            self.__getattribute__(k).insert(0,kwargs[k])

    def importOther(self,other,**kwargs):
        self[other].importData(**kwargs)

    def __getitem__(self, item):
        if item is None:
            return self

        return getattr(self,item,None)

    def __setitem__(self, key, value):
        self.__setattr__(key,value)

    def showAll(self):
        for c in self.columns:
            print c,self[c]


class OandaEngine(Manager):

    indinfo=[]
    T=0
    now={}

    others={}

    def __init__(self,**kw):

        self.acc=kw.pop('account',Account())
        if 'db' not in kw:
            kw['db']='Oanda'
        self.initMongoClient(**kw)
        self.projection=['time','closeBid','closeAsk','highBid','highAsk','lowBid','lowAsk','openBid','openAsk']

    def OnInit(self,collection=None,**kw):
        # 设置默认数据
        if collection is not None:
            self.set_collection(collection)

        # 初始化数据服务
        self.data=ActiveData(self.symbol)
        for prj in kw.pop('projection',self.projection):
            self.data[prj]=[]

        for o in self.others:
            self.data[o]=ActiveData(o)
            for c in self.others[o]:
                self.data[o].__setattr__(c,[])

        for info in self.indinfo:
            name=info[0]
            col=info[2]
            self.data[col].__setattr__(name,[])

        # 向account提供数据服务
        self.acc.setDataInterface(self.data)


    def setAccount(self,account):
        # 重设账户
        self.acc=account

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

    def open(self,**kw):

        self.acc.openOrder(code=kw.get('symbol',None),
                           price=kw.pop('price',self.data[kw.pop('symbol',None)][0]),
                           lots=kw.pop('lots',1),
                           **kw
                           )

    def close(self,**kw):
        '''

        :param kw:
            searchBy: default: 'ticket'
            value:
            order: an order object

            if order in kw, searchBy and value is useless
            if order not in kw, order=self.acc.findOrder(value,searchBy)

        :return:
        '''

        order=kw.pop('order') if 'order' in kw else self.acc.findOrder(kw['value'],kw.pop('searchBy','ticket'))
        self.acc.closeOrder(self.data[order.code]['closeBid'],order)

    def addIndicator(self,ind):
        # 添加常驻指标信息

        if ind[2] is not None:
            self.others[ind[2]]=ind[3]

        ind.append(max(ind[4].values()))

        self.indinfo.append(ind)

    def addSymbol(self,symbol,projection):
        # 添加其他常驻数据信息
        self.others[symbol]=projection

    def __refreshOthers(self,t):
        # 刷新常驻数据
        for o in self.others:
            one=self.mDb[o].find_one({'time':{'$lte':t}},projection=self.others[o],sort=[('time',-1)])
            one.pop('_id',0)
            self.data.importOther(o,**one)

    def __refreshIndicator(self):
        # 刷新常驻指标
        for name,indicator,collection,Input,params,Max in self.indinfo:
            inputs=[]
            for ip in Input:
                inputs.append(self.data[collection][ip][Max-1::-1])

            ind=getInd(indicator,*inputs,**params)
            self.data[collection].importData(**{name:ind[-1]})

    def refresh(self,data):
        data.pop('_id',0)

        # 更新主数据
        self.data.importData(**data)
        # 更新常驻数据
        self.__refreshOthers(data['time'])
        # 更新常驻指标
        self.__refreshIndicator()
        # 更新账户
        self.acc.refresh()


if __name__ == '__main__':
    engine=OandaEngine()

    engine.addSymbol('EUR_USD.D',['closeBid'])
    engine.addIndicator(['maFast','MA','EUR_USD.D',['closeBid'],{'timeperiod':10}])
    for i in engine.mDb['GBP_USD.D'].find(projection=['time','closeBid','openBid']).limit(30):
        engine.refresh(i)









