# coding:utf-8
from support.dataManager import Manager
import time
from support.talibs import getInd,getIndicator
from account import Account,Order
import stgAlgo.oanda_point as point

class ActiveData(object):


    def __init__(self,name,point=1):
        '''

        :param name: 服务名
        :param point: 点数
        :return:
        '''

        self.name=name
        self.point=point

        # 表示存储的数据
        self.columns=[]
        # 表示存储的其他数据服务
        self.child=[]

    def importData(self,**kwargs):
        '''
        向数据服务的列表中添加数据
        :param kwargs:
            a=x,b=y,...
            a,b:数据服务中的列表名
            x,y:要添加的数据
        :return:
        '''
        for k in kwargs:
            self.__getattribute__(k).append(kwargs[k])

    def importOther(self,other,**kwargs):
        '''
        向子服务添加数据
        :param other: 子服务对象名
        :param kwargs: 同importData
        :return:
        '''
        self[other].importData(**kwargs)

    def create(self,attr,*attrs):
        '''
        创建空数据列
        :param attr: 列名
        :param attrs: 列所在的服务，不输入代表当前服务

            ActiveData.create('name','ad1','ad2')
            表示在当前服务的ad1服务的ad2服务中创建空数据列

        :return:
        '''
        if len(attrs):
            if hasattr(self,attrs[0]):
                if isinstance(self[attrs[0]],ActiveData):
                    self[attrs[0]].create(attr,*attrs[1:])
                else:
                    raise TypeError("self.%s is not class<ActiveData>" % attrs[0])
            else:
                raise AttributeError("ActiveData<%s> does not have attribute: %s" % (self.name,attrs[0]) )

        else:
            self[attr]=[]
            self.columns.append(attr)

    def createChild(self,name,point=1):
        '''
        创建名为name的子服务
        :param name: 服务名
        :param point: 点数
        :return:
        '''

        self[name]=ActiveData(name,point)
        self.child.append(name)

    def clear(self,keep=100,*columns):
        '''
        清除本服务的列表中的数据，每列只保留keep个最新数据
        :param keep:
        :param columns: 需要清除的列表，不输入代表全部
        :return:
        '''
        columns=self.columns if columns.__len__() == 0 else columns
        for c in columns:
            while self[c].__len__()>keep:
                self[c].pop(0)

    def clearAll(self,keep=100):
        '''
        清除本服务及所有子服务中的列表中的数据，每列只保留keep个最新数据
        :param keep:
        :return:
        '''
        self.clear(keep)
        for child in self.child:
            self[child].clearAll(keep)

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

    def initDataSerivce(self,symbol,data=None,**kw):
        self.data=ActiveData(symbol,kw.pop('point',1)) if data==None else data
        for prj in kw.pop('projection',self.projection):
            self.data[prj]=[]

        self.acc.setDataInterface(self.data)

    def OnInit(self,collection=None,**kw):
        # 设置默认数据
        if collection is not None:
            self.set_collection(collection)

        # 初始化数据服务
        self.initDataSerivce(collection,**kw)

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

        symbol=kw.get('symbol',None)
        self.acc.openOrder(code=symbol,
                           price=kw.pop('price',self.data[symbol]['closeBid'][-1]),
                           lots=kw.pop('lots',1),
                           point=self.data[symbol].point,
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
        self.acc.closeOrder(self.data[order.code]['closeBid'][-1],order)

    def addIndicator(self,name,*args,**kw):
        # 添加常驻指标信息
        kw.pop('data',self.data).create(name,*args)


    def addSymbol(self,symbol,projection,**kw):
        # 添加其他常驻数据信息
        self.others[symbol]=projection
        self.data.createChild(symbol,kw.pop('point',1))
        for prj in projection:
            self.data[symbol][prj]=[]

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

    def finish(self):
        self.acc.finish()

    def refresh(self,data):
        data.pop('_id',0)

        # 更新主数据
        self.data.importData(**data)
        # 更新常驻数据
        self.__refreshOthers(data['time'])
        # 更新账户
        self.acc.refresh()


if __name__ == '__main__':

    engine=OandaEngine()

    engine.addSymbol('EUR_USD.D',['closeBid'])
    for i in engine.mDb['GBP_USD.D'].find(projection=['time','closeBid','openBid']).limit(30):
        engine.refresh(i)









