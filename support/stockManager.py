from dataManager import Manager
import pandas,requests,time
from datetime import datetime,timedelta
from pymongo.collection import Collection

class StockManager(Manager):

    def __init__(self,**kw):

        if 'db' not in kw:
            kw['db']='Data'
        self.initMongoClient(**kw)

    @staticmethod
    def getHKStockBar(code,retype='dict',**f):
        '''

        :param code: stockCode (0700.hk, 600000.ss .....)
        :param f:
            a = begin month - 1
            b = begin day
            c = begin year
            d = end month - 1
            e = end day
            f = end year
            g = timeframe(w:week, d:day, w:week, m:month)
        :return: DataFrame()
        '''

        print(code,f)

        url='http://table.finance.yahoo.com/table.csv?s=%s' % code

        param=''
        for k in f.keys():
            param=param+'&%s=%s' % (k,f[k])

        url=url+param+'&ignore=.csv'
        data=requests.get(url,timeout=10)
        lines=data.text.split('\n')
        lines.pop()
        columns=lines[0].split(',')
        docs=[]
        for line in lines[1:]:
            line=line.split(',')
            doc={'Date':datetime.strptime(line[0],'%Y-%m-%d')}

            for i in range(1,len(columns)):
                doc[columns[i]]=float(line[i])
            if doc['Volume']==0:
                continue

            doc['time']=time.mktime(doc['Date'].timetuple())

            docs.append(doc)

        docs.reverse()

        if retype=='dict':
            return docs
        elif retype=='pandas':
            return pandas.DataFrame(docs)

    def collection_adapt(self,collection):
        return self.mDb[collection] \
            if not isinstance(collection,Collection) else collection

    def updateHistory(self,collection):
        collection=self.collection_adapt(collection)

        last=collection.find_one(projection=['Date'],sort=[('time',-1)])['Date']
        bars=self.getHKStockBar(
            '.'.join(collection.name.split('.')[:-1]),
            a=last.month-1,b=last.day,c=last.year
        )
        self.save(collection,bars)
        print collection.name,'update to',bars[-1]


    def save(self,collection,documents):
        collection=self.collection_adapt(collection)

        collection.insert(documents)
        collection.create_index('time')

    def update_manny(self,*collections):
        collections=list(collections)
        if len(collections)==0:
            for col in self.mDb.collection_names(False):
                if col.endswith('hk.Day'):
                    collections.append(col)
        self._multiThreadRun(collections,self.updateHistory)



if __name__ == '__main__':
    sManager=StockManager()
    # print sManager.getHKStockBar('0700.hk',retype='pandas',a=0,b=1,c=2016)
    # sManager.update_manny()