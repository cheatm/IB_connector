import pymongo

import time,datetime
from ib.opt.connection import Connection
from ib.opt import message
from ib.ext.Contract import Contract
from Subscribe import Subscribe
from engine.Engine import Engine
from DataBase import Client

class IBConnection():

    updating={}

    def __init__(self):

        self.engine=Engine()

        self.connectIB()
        self.connectDB('FinanceData')
        self.setTiming()

    def connectDB(self,dbname):
        self.db=Client.connectDB(dbname)

    def setTiming(self):
        self.setDataUpdate()
        pass

    def setDataUpdate(self):
        subscribed=Subscribe.readSubscribed()
        now=time.strftime('%Y%m%d %H:%M:%S')
        for symbol in subscribed:
            contract=subscribed[symbol][0]
            for p in subscribed[symbol][1]:
                self.tickid+=1
                print(symbol)
                self.updating[self.tickid]=(symbol,p)

                self.con.reqHistoricalData(self.tickid,contract,
                          now,'2 D',p,'MIDPOINT',0,1)

    def connectIB(self,port=7497,clientId=123):
        self.con=Connection.create(port=port,clientId=clientId)

        self.watchDict={
            self.autoDataUpdate:message.historicalData
        }

        self.con.registerAll(self.watcher)
        for watcher in self.watchDict:
            self.con.unregister(self.watcher,self.watchDict[watcher])
            self.con.register(watcher,self.watchDict[watcher])

        self.con.connect()
        self.tickid=0

    def watcher(self,msg):
        print msg

    def autoDataUpdate(self,msg):

        info=self.updating[msg.reqId]

        if 'finish' in msg.date:
            self.db.IB[info[0]][info[1]].find_and_dropDups('time')
            return

        dt=datetime.datetime.strptime(msg.date,'%Y%m%d %H:%M:%S')
        timestamp=time.mktime(dt.timetuple())
        self.db.IB[info[0]][info[1]].insert({
            'time':timestamp,'date':msg.date,
            'open':msg.open,'high':msg.high,'low':msg.low,'close':msg.close
        })
        print 'update:',msg



def watcher(msg):
    print(msg)

def dataUpdate(msg):
    print msg

def autoReqData(func,control,name,args,**kw):
    sleep=5
    if 'sleep' in kw:
        sleep=kw['sleep']

    while control[name]:
        func(*args,**kw)
        time.sleep(sleep)

def createConnection():
    engine=Engine()
    con=Connection.create(port=7497,clientId=123)
    con.register(dataUpdate,message.historicalData)
    con.register(watcher,message.tickPrice)
    # con.registerAll(watcher)

    con.connect()

    tickid=1

    cd=Subscribe.makeContract(m_symbol='EUR',m_secType='CASH',m_currency='USD',
                              m_exchange='IDEALPRO')

    engine.registerTiming('autoReqData',autoReqData,con.reqHistoricalData,args=[tickid,cd,
                          '20161017 23:59:59','3 D','1 hour','MIDPOINT',0,1],sleep=10)

    engine.startTiming()
    time.sleep(5)
    engine.stopTiming()

    # con.reqHistoricalData(tickid,cd,
    #                       '20160920 23:59:59 GMT','2 D','1 hour','MIDPOINT',0,1)

    time.sleep(3)

if __name__ == '__main__':

    # createConnection()
    iConnection=IBConnection()
    con=iConnection.con

    #
    # gbp=Subscribe.readContract('GBPUSD')
    # con.reqMktData(1,gbp,'',True)
    # now=time.strftime('%Y%m%d %H:%M:%S')
    # con.reqHistoricalData(2,gbp,
    #                       now,'2 D','1 hour','MIDPOINT',0,1)


    time.sleep(10)