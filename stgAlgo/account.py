# coding:utf-8
from datetime import datetime as dt
import pandas
from datetime import datetime

class Order():

        def __init__(self,ticket,code,openPrice,lots,deposit,time,stoplost=0,takeprofit=0,comment=None,point=1):

            self.code=code
            self.openPrice=openPrice
            self.lots=lots
            self.stoplost=self.openPrice-stoplost*lots/abs(lots) if stoplost else None
            self.takeprofit=self.openPrice+takeprofit*lots/abs(lots) if takeprofit else None
            self.ticket=ticket
            self.deposit=deposit
            self.openTime=dt.fromtimestamp(time)
            self.comment=comment
            self.point=point

        def close(self,price,time):
            self.closeTime=dt.fromtimestamp(time)
            self.closePrice=price
            self.profit=(self.closePrice-self.openPrice)*self.lots/self.point



class Account():

    orders=[]
    ordersHistory=[]
    Time=0
    capital=[]
    log=[]

    def __init__(self,initCash=1000000,lever=1,**kwargs):
        '''

        :param initCash: initial cash
        :param lever: >1
        :return:

        How to use:
            # create an account with default setting:
            acc=Account()

            # create an account:
            acc=Account(initCash=9999999,lever=50,close='closeBid',high='highBid',low='lowBid')


        '''


        self.lever=lever
        self.cash=initCash
        self.initCash=initCash
        self.nextTicket=0

        self.CLOSE=kwargs.pop('close','close')
        self.HIGH=kwargs.pop('high','high')
        self.LOW=kwargs.pop('low','low')
        if 'data' in kwargs:
            self.data=kwargs['data']

    def setDataInterface(self,data):
        self.data=data

    def closeOrder(self,price,order,closeType='close'):
        '''

        :param price:
        :param order:
        :param ticket:
        :return:
        '''

        order.close(price,self.Time)
        order.closeType=closeType
        self.cash=self.cash+order.profit+order.deposit
        self.ordersHistory.append(order)
        self.orders.remove(order)

    def openOrder(self,code,price,lots,stoplost=0,takeprofit=0,ticket=None,comment=None,point=1):
        '''
        open an order
        :param price:
        :param lots:
        :param stoplost:
        :param takeprofit:
        :param ticket:
        :return:
        '''
        if isinstance(ticket,int) and ticket>=self.nextTicket:
            pass
        else:
            ticket=self.nextTicket


        deposit=abs(lots*price/self.lever/point)
        if deposit>self.cash:
            return

        order=Order(ticket,code,price,lots,deposit,self.Time,stoplost,takeprofit,comment,point)
        self.cash=self.cash-deposit
        self.orders.append(order)

        self.nextTicket=ticket+1

    def getOrders(self):
        attrs=['ticket','code','openPrice','lots','stoplost','takeprofit','deposit']
        orders=[]
        for  o in self.orders:
            order=[]
            for a in attrs:
                order.append(getattr(o,a))
            orders.append(order)

        return pandas.DataFrame(orders,columns=attrs)

    def getHistoryOrders(self):
        attrs=['ticket','code','openTime','closeTime','openPrice','closePrice','lots','stoplost','takeprofit','deposit','profit']
        orders=[]
        for o in self.ordersHistory:
            order=[]
            for a in attrs:
                order.append(getattr(o,a))
            orders.append(order)

        return pandas.DataFrame(orders,columns=attrs)

    def marginLog(self):
        log=[self.initCash]
        for o in self.ordersHistory:
            log.append(log[-1]+o.profit)

        return(log)

    def refreshOrder(self,order):

        if order.lots>0:
            if order.stoplost and order.stoplost>self.data[order.code][self.LOW]:
                self.closeOrder(order.stoplost,order,'SL')
                return
            if order.takeprofit and order.takeprofit<self.data[order.code][self.HIGH]:
                self.closeOrder(order.takeprofit,order,'TP')
                return
        else:
            if order.stoplost and order.stoplost<self.data[order.code][self.HIGH]:
                self.closeOrder(order.stoplost,order,'SL')
                return
            if order.takeprofit and order.takeprofit>self.data[order.code][self.LOW]:
                self.closeOrder(order.takeprofit,order,'TP')
                return

        order.profit=(self.data[order.code]['closeMid'][-1]-order.openPrice)*order.lots/\
            self.data[order.code].point

        pass

    def refresh(self):
        self.Time=self.data.time[-1]

        for o in self.orders:
            self.refreshOrder(o)

        capital=self.cash
        for o in self.orders:
            capital=capital+o.profit+o.deposit

        self.log.append(
            {
                'cash':self.cash,
                'capital':capital,
                'time':self.Time,
                'datetime':datetime.fromtimestamp(self.Time)
            }
        )


    def finish(self):
        # 结束时调用，平掉未平仓的订单
        for order in self.orders:
            self.closeOrder(self.data[order.code].closeMid[-1],order,'close at stop')

        self.log.append(
            {
                'cash':self.cash,
                'capital':self.cash,
                'time':self.Time,
                'datetime':datetime.fromtimestamp(self.Time)
            }
        )


    def findOrder(self,value,searchBy='ticket',mode='orders'):
        for o in getattr(self,mode):
            if getattr(o,searchBy)==value:
                return o

    def findOrders(self,mode='orders',**how):
        out=[]
        for o in getattr(self,mode):
            isOrder=True
            for k in how.keys():
                if getattr(o,k)!=how[k]:
                    isOrder=False
                    break
            if isOrder:
                out.append(o)

        return out

    def mergeOrders(self,*orders,**kw):
        stoplost=kw.pop('stoplost',0)
        takeprofit=kw.pop('takeprofit',0)

        code = orders[0].code
        lots,price,comment,deposit=0,0,'',0

        for order in orders:
            if code != order.code:
                print('Cannot merge orders with different code')
                return
            lots=lots+order.lots
            price=price+order.lots*order.price
            deposit+=order.deposit
            comment='%s_%s_' % (comment,order.comment)
            self.orders.remove(order)
        newOrder=Order(orders[0].ticket,code,price/lots,lots,deposit,self.Time,stoplost,takeprofit,comment)
        self.orders.append(newOrder)
