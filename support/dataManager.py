 #coding=utf-8
from oandapy import oandapy
from pyoanda import Client
import json,os,time
import DataBase.Client
import threading
import Queue,pandas
from datetime import datetime,timedelta

def getRootDir(path=os.getcwd()):
    if os.path.exists('%s/ROOT' % path):
        return path
    else:
        return getRootDir(os.path.dirname(path))

class Manager():

    run=False
    requests=Queue.Queue()
    running=[]
    accomplish=[]
    lock=threading.RLock()

    def initMongoClient(self,**kw):
        '''

        :param kw:
            mClient: name of json file contains MongoDB information
            ClientObject: existed MongoClient Object
            db: default mongodb to be set
            collection: default collection to be set in default db

        :return:
        '''

        self.mClient=DataBase.Client.connectDB(kw.pop('mClient','FinanceData'))\
        if 'ClientObject' not in kw else kw.pop('ClientObject')

        if 'db' not in kw:
            return

        self.setDefaultMdb(kw['db'])

        if 'col' not in kw:
            return

        self.setDefaultCollection(kw['db'],kw['col'])

    def setDefaultMdb(self,db):
        self.mDb=self.mClient[db]

    def setDefaultCollection(self,db,col):
        self.collection=self.mClient[db][col]

    @staticmethod
    def _multiFunctionrun(funcList,Max=5,sleep=1):
        '''

        :param funcList:
            [(function,params),......]
            params:{}
        :param Max: 最大并行
        :param sleep: 最大并行时休眠时间
        :return:
        '''
        queue=Queue.Queue()

        for func,params in funcList:

            queue.put(threading.Thread(target=func,kwargs=params))

        running=[]

        for i in range(0,max(Max,queue.qsize())):
            t=queue.get()
            t.start()
            running.append(t)
            t.join(0)
            time.sleep(0.5)

        while len(running)>0:

            for t in running:
                if t.isAlive():
                    continue

                running.remove(t)
                if queue.qsize():
                    t=queue.get()
                    t.start()
                    running.append(t)
                    t.join(0)

            if len(running)==Max:
                time.sleep(sleep)

        del running

    @staticmethod
    def _multiThreadRun(paramList,function,Max=5,sleep=1):
        '''
        以不同的参数(paramList)调用同一个方法(funcion),最大并行为Max
        :param paramList:
             [
                param, # func(single)
                [param1,param2,...], # func(*args)
                {key1:value1,key2:value2,...}, # func(**kwargs)
                ([param1,param2,...],{key1:value1,key2:value2,...}), # func(*args,**kwargs)
                ......
             ]
        :param function: 调用的方法
        :param Max: 最大并行数
        :return:
        '''

        queue=Queue.Queue()

        for params in paramList:
            if isinstance(params,tuple):
                thread=threading.Thread(target=function,args=params[0],kwargs=params[1])
                queue.put(thread)
            elif isinstance(params,dict):
                thread=threading.Thread(target=function,kwargs=params)
                queue.put(thread)
            elif isinstance(params,list):
                thread=threading.Thread(target=function,args=params)
                queue.put(thread)
            else:
                thread=threading.Thread(target=function,args=[params],name=params)
                queue.put(thread)

        running=[]

        def release(running):
            for t in running:
                if not t.isAlive():
                    running.remove(t)

        while queue.qsize():
            if len(running)<Max:
                t=queue.get()
                t.start()
                running.append(t)
                t.join(0)
                continue
            else:
                release(running)

        while len(running):
            release(running)
            time.sleep(0.1)

    def execute(self,Max):
        while self.run or self.requests.qsize():
            while len(self.running)<Max and self.requests.qsize():
                self.lock.acquire()
                try:
                    thread=self.requests.get()
                    thread.start()
                    self.running.append(thread)
                    thread.join(0)
                except Exception as e:
                    print e
                self.lock.release()
        print 'executing accomplish'

    def clean(self):
        while self.run or self.requests.qsize() or len(self.running):
            for thread in self.running:
                if not thread.isAlive():
                    self.lock.acquire()
                    self.running.remove(thread)
                    self.lock.release()
                    self.accomplish.append(thread.name)
        print 'cleaning accomplish'


    def putRequest(self,function,name=None,*args,**kw):
        self.requests.put(
            threading.Thread(target=function,name=name,args=args,kwargs=kw)
        )


    def start(self,Max=5):
        self.run=True
        self.executor=threading.Thread(target=self.execute,kwargs={'Max':Max})
        self.cleaner=threading.Thread(target=self.clean)
        self.executor.start()
        self.cleaner.start()

    def stop(self):
        self.run=False
        self.executor.join()
        self.cleaner.join()

    def changeData(self,collection,db=None,how=None,*args,**kwargs):
        '''

        :param collection:
        :param db:
        :param how:
            projection=func
        :return:
        '''

        print kwargs

        if not db:
            collection=self.mDb[collection] if isinstance(collection,str) else collection
        else:
            if isinstance(db,str):
                collection=self.mClient[db][collection]
            else:
                collection=db[collection]

        for doc in collection.find(*args,**kwargs):

            collection.update_one({'_id':doc['_id']},how(doc))

        print collection.name,'finish'

class InstantManager(Manager):


    def __init__(self,**kw):
        '''

        :param kw:
            MongoClient: A MongoClient Object. Default:  pymongo.MongoClient(port=10001)
            db: select default database in MongoClient. Default: None
            col: select default collection in selected database. Default: None
            mode: 'paper' or 'trade' . Default 'paper'

        Example:
            import DataBase.Client
            client=DataBase.Client.connectDB('FinanceData')
            rd=ReqData(MongoClient=client,db='Oanda',col='GBP_USD.D')

        :return:
        '''

        self.initMongoClient(**kw)

        self.initMode(kw.pop('mode','paper'))

    def initMode(self,mode):
        modes={'paper':self.__initPaper,
               'trade':self.__initTrade}

        if mode in modes:
            modes[mode]()
            self.mode=mode

    def __initPaper(self):
        self.get=self.__get_paper
        self.get_mongo=self.__get_mongo_paper

    def __initTrade(self):
        pass

    def get(self,*args,**kw):
        pass

    def get_mongo(self,*args,**kw):
        pass

    def __get_paper(self,t=time.time(),shift=0,range=None,projection=None):
        return self.__get(self.collection,t,shift,range,projection)

    def __get_mongo_paper(self,db,collection,t=time.time(),shift=0,range=None,projection=None):
        return self.__get(self.mClient[db][collection],t,shift,range,projection)

    def __get(self,collection,t=time.time(),shift=0,range=None,projection=None):
        cursor=collection.find({'time':{'$lt':t}},projection=projection).sort('time',-1)
        if range is None:
            return cursor[shift]
        else:
            return cursor[range[0]:range[1]]


class OandaManager(Manager):

    typeDict={'M':'get_history',
              'D':'get_history',
              'M15':'get_history',
              'H1':'get_history',
              'H4':'get_history',
              'W':'get_history',
              'M1':'get_history',
              'COT':'get_commitments_of_traders',
              'HPR':'get_historical_position_ratios'}


    def __init__(self,**kw):
        '''

        :param kw:
            doc: json file contains OnadaClient infomation
            mClient: name of json file contains MongoDB information
            ClientObject: existed MongoClient Object
            db: default mongodb to be set
            collection: default collection to be set in default db

        :return:
        '''


        infoFile='%s/support/%s.json' % (getRootDir(),kw.pop('doc','OandaClient'))
        info=json.load(open(infoFile))
        self.opclient=oandapy.API(**info['oandapy'])
        self.poclient=Client(**info['pyoanda'])


        self.initMongoClient(**kw)
        if 'db' not in kw:
            self.mDb=self.mClient['Oanda']



    def save_mongo(self,data,collection,db=None):
        collection=self.mDb[collection] if db is None else self.mClient[db][collection]
        collection.insert(data)

    def update(self,collection):
        collection=self.mDb[collection]
        kw = self._get_col_info(collection)
        print kw

    def update_manny(self,*collections,**kwargs):
        '''

        :param collections: 要更新的collection名
        :param kwargs:
            tail=xxx : 更新所有后缀为xxx的collection (default:M1)
            finish=<datetime> : 表示更新到<datetime>的日期之后
        :return:
        '''

        tail=kwargs.pop('tail','M1')
        finish=kwargs.pop('finish',datetime.now()-timedelta(hours=24))

        collections=list(collections)
        if len(collections)==0:
            for col in self.mDb.collection_names(False):
                if col.endswith(tail):
                    collections.append(col)

        self.accomplish=list(collections)
        self.start(5)
        while len(collections):
            for col in collections:
                if not self.mDb[col].find_one({'datetime':{'$gte':finish}}):
                    if col in self.accomplish:
                        self.putRequest(self.update(col))
                        self.accomplish.remove(col)
                else:
                    collections.remove(col)
                    print 'remove',col,'left',len(collections)
        self.stop()


    def get_request_parmams(self,**kw):
        pdict={'get_history':self._save_history,
               'get_commitments_of_traders':self._save_cot,
               'get_historical_position_ratios':self._save_hpr}

        return pdict[kw.pop('func')](**kw)

    def seconds2ts(self,seconds):
        return '%s-%s-%sT%02d:%02d:%02d' % tuple(time.gmtime(seconds))[0:6]

    def _save_cot(self,**kw):
        col=kw.pop('col')
        data=self.opclient.get_commitments_of_traders(instrument=kw['instrument'])[kw['instrument']]
        for d in data:
            print datetime.fromtimestamp(d['date'])
            if col.find_one({'time':d['date']}) is not None:

                continue
            d['time']=d.pop('date')
            d['datetime']=datetime.fromtimestamp(d['time'])
            # d['date']=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(d['time']))
            d['publish']=d['time']+345600
            d['l-s']=float(d['ncl'])-float(d['ncs'])
            d['s-l']=-d['l-s']
            col.insert_one(d)
            sl=col.find_one({'publish':{'$lt':d['time']}},sort=[('publish',-1)])['s-l']
            col.update_one({'publish':d['publish']},{'$set':{'s-l_diff':d['s-l']-sl}})

        return kw

    def _save_hpr(self,**kw):
        col=kw.pop('col')
        data=self.opclient.get_historical_position_ratios(instrument=kw['instrument'],
                                                          period=31536000)

        data= data['data'][kw['instrument']]['data']

        last=col.find_one(projection=['time'],sort=[('time',-1)])['time']
        col.delete_one({'time':last})

        for d in data:
            if col.find_one({'time':d[0]}) is not None:
                continue

            saveDict={'time':d[0],'long_position_ratio':d[1],
                      'short_position_ratio':100-d[1],
                      'position':100-2*d[1],
                      'exchange_rate':d[2]}
            saveDict['datetime']=datetime.fromtimestamp(d[0]).replace(second=0)
            pos=col.find_one(filter={'time':{'$lt':d[0]}},sort=[('time',-1)])['position']
            saveDict['position_diff']=saveDict['position']-pos
            col.insert_one(saveDict)

        return kw

    def saveHistory(self,**kw):
        '''

        :param kw:
            col: collection
            instrument: symbol
            granularity: period
            start: start time
            end: end time
            count: bar count
        :return:
        '''

        col=kw.pop('col','%s.%s' % (kw['instrument'],kw['granularity']))

        if 'start' in kw and 'end' in kw:
            kw['count']=None

        kw['daily_alignment']=kw.get('daily_alignment',0)
        kw['alignment_timezone']=kw.get('alignment_timezone', 'UTC')
        kw['weekly_alignment']=kw.get('weekly_alignment',"Monday")
        kw['candle_format']='midpoint'
        try:
            data=self.poclient.get_instrument_history(**kw)
        except Exception as e:
            print e
            if '5000' in str(e):
                kw.pop('end',None)
                kw['count']=5000
                self.saveHistory(**kw)
            return

        col=self.mClient.Oanda[col]
        for candle in data['candles']:
            if not candle.get('complete',True):
                data['candles'].remove(candle)
                break

            candle['Date']=candle['time'][:-8]
            candle['datetime']=datetime.strptime(candle['Date'],'%Y-%m-%dT%H:%M:%S')
            candle['time']=time.mktime(candle['datetime'].timetuple())

            col.insert_one(candle)

        print kw['instrument'],kw['granularity']

    def _save_history(self,**kw):
        '''
        用于更新历史数据，一次最多5000bar
        :param kw:
        :return:
        '''
        kwcopy=kw.copy()
        kwcopy['try']=kw.pop('try',-1)+1
        col=kw.pop('col')
        lastTime=col.find_one(projection=['time','Date'],sort=[('time',-1)])
        col.delete_one({'time':lastTime['time']})
        kw['start']=lastTime['Date']
        kw['count']=5000
        kw['granularity']=kw.pop('type')
        kw['daily_alignment']=0
        kw['alignment_timezone']='UTC'
        kw['weekly_alignment']="Monday"
        kw['candle_format']='midpoint'
        try:
            data=self.poclient.get_instrument_history(**kw)
        except Exception as e:
            print e.message
            return

        for candle in data['candles']:

            candle['Date']=candle['time'][:-8]
            candle['datetime']=datetime.strptime(candle['Date'],'%Y-%m-%dT%H:%M:%S')
            candle['time']=time.mktime(time.strptime(candle['Date'],'%Y-%m-%dT%H:%M:%S'))

            col.insert_one(candle)

        return kw

    def _get_col_info(self,collection):
        slist= collection.name.split('.')

        if slist[1] in self.typeDict:
            Type=self.typeDict[slist[1]]
            out=self.get_request_parmams(col=collection,instrument=slist[0],type=slist[1],func=Type)

            return out
        else:
            return slist[1],'is not able to update'

    def drop_duplicate(self,collection,on='datetime'):
        collection=self.mDb[collection] if isinstance(collection,str) else collection
        pre=collection.find_one()[on]
        collection.create_index(on)
        for c in collection.find(projection=[on]).sort([(on,1)])[1:]:

            if pre==c[on]:
                collection.delete_one({on:c[on]})
                print 'drop',collection.name,c.get('datetime',None)
            pre=c[on]



if __name__ == '__main__':

    om=OandaManager()
    om.update_manny(tail='.H1',finish=datetime.today()-timedelta(days=2))
    om.update_manny(tail='.H4',finish=datetime.today()-timedelta(days=2))
    om.update_manny(tail='.D',finish=datetime.today()-timedelta(days=2))

    # om.start(5)
    # for col in om.mDb.collection_names(False):
    #     if col.endswith('.D'):
    #         om.putRequest(om.drop_duplicate,col,str(col))
    # om.stop()













