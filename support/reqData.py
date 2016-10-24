import pymongo
import time

class ReqData():


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

        self.mClient=kw.pop('MongoClient',pymongo.MongoClient(port=10001))

        self.mDb=self.mClient[kw['db']] if 'db' in kw else None
        self.collection=self.mDb[kw['col']] if 'col' in kw and self.mDb is not None else None

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

    def setDefaultMdb(self,db):
        self.mDb=self.mClient[db]

    def setDefaultCollection(self,db,col):
        self.collection=self.mClient[db][col]



if __name__ == '__main__':
    pass








