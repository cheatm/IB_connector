from oandapy import oandapy
import json,os,time
import DataBase.Client

def getRootDir(path=os.getcwd()):
    if os.path.exists('%s/ROOT' % path):
        return path
    else:
        return getRootDir(os.path.dirname(path))

class Manager():

    def initMongoClient(self,**kw):

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


    def __init__(self,**kw):

        doc="%s/support/%s.json" % (getRootDir(),kw.pop('doc','oandapyClient'))
        cInfo=kw.pop('info',json.load(open(doc)))
        self.opclient=kw.pop('client',oandapy.API(**cInfo))

        self.initMongoClient(**kw)
        if 'db' not in kw:
            self.db=self.mClient['Oanda']

    def __getattr__(self, item):
        try:
            return getattr(self.opclient,item)
        except Exception as e:
            raise AttributeError(e.message)
            pass

    def save_mongo(self,data,collection,db=None):
        collection=self.db[collection] if db is None else self[db][collection]
        collection.insert(data)



if __name__ == '__main__':
    om =OandaManager(mClient='New',db='Oanda')

    print om.opclient.get_commitments_of_traders(instrument='EUR_USD')



