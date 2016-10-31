from support.dataManager import Manager
import time
from support.talibs import getInd,getIndicator

class BackTestEngine(Manager):

    ind={}

    def __init__(self,**kw):

        self.initMongoClient(**kw)



    def get(self,shift=0,range=None,projection=None):
        return self.__get(self.collection,shift,range,projection)

    def get_mongo(self,db,collection,shift=0,range=None,projection=None):
        return self.__get(self.mClient[db][collection],shift,range,projection)

    def __get(self,collection,shift=0,range=None,projection=None):
        cursor=collection.find({'time':{'$lte':self.T}},projection=projection).sort('time',-1)
        if range is None:
            return cursor[shift]
        else:
            return cursor[range[0]:range[1]]


    def set_ind(self,start,end,name,ind,db,collection,*inputs,**params):
        dataf=self.mClient[db][collection].find({'time':{'$gte':start,'$lte':end}},
                                                 projection=['time'].extend(*inputs)).toDataFrame()

        indInput=[]
        for i in inputs:
            indInput.append(dataf[i])

        indicator=getIndicator(ind,dataf['time'],*indInput,**params)
        self.ind[name]=indicator

    def get_ind(self,name,shift):
        indicator=self.ind[name]
        return indicator[indicator.time<=self.T]



class BackTestSystem():

    def __init__(self):
        pass