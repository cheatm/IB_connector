# coding:utf-8
import time

class Strategy(object):

    def __init__(self,engine,**kw):

        self.engine=engine
        self.point=kw.pop('point',1)

    def set_params(self,**params):

        self.point=params.pop('point',1)
        for p in params:
            if hasattr(self,p):
                self.__setattr__(p,params[p])
            else:
                raise AttributeError("No param names '%s' " % p)

    def set_engine(self,engine):
        self.engine=engine

    def OnInit(self,**kw):
        '''
        初始化策略，在策略启动前调用，
        某些function需要写在当中，需要用户重写

        :param kw:
        :return:
        '''
        pass

    def setIndicator(self,name,*args,**kwargs):
        '''
        添加常驻指标信息
        需要重写OnInit方法并在OnInit中调用该方法设置常驻指标

        self.setIndicator('ma')

        self.setIndicator('ma','EUR_USD.D')

        在onBar(data)中的调用方法：
            data[collection][name][item]
            data[name][item]

        '''
        self.engine.addIndicator(name,*args,**kwargs)

    def addSymbol(self,symbol,projection,**kw):
        '''
        添加其他常驻数据信息
        需要重写OnInit方法并在OnInit中调用该方法添加其他常驻数据

        :param symbol: 其他常驻数据的来源数据 collection
        :param projection: collection中需要获取的数据
        :param **kw:
            point: 点数 默认 1

        调用：

            self.addSymbol('EUR_USD.D',['closeBid','closeAsk'],point=0.00001)

        在onBar中获取数据：
            data[symbol]['closeBid'][item]

        '''
        self.engine.addSymbol(symbol,projection,**kw)

    def onBar(self,data):
        pass

    def open(self,**order):
        '''

        :param order:
            symbol: 品种，不填代表当前品种
            lots: 手数，默认为1
            price: 价格，默认为该品种当前收盘价
            stoplost: 止损，默认0
            takeprofit: 止盈，默认0


        :return:
        '''
        self.engine.open(**order)

    def close(self,**order):
        '''

        :param order:
            searchBy: 查找方式 默认 ticket
            value: 查找值
                close(value=1,searchby='ticket')
                平仓ticket==1的订单

            or

            order: <Order>类型的对象，如果输入了order前2个可省略
                close(order=order1)
                将order1平仓

        :return:
        '''
        self.engine.close(**order)

    def get(self,**kw):
        return self.engine.get(**kw)

    def getAccount(self):
        '''
        获取账户对象
        :return: class<Account>
        '''
        return self.engine.acc



from support.talibs import getInd
import stgAlgo.oanda_point as point

class StrategyDemo(Strategy):

    # 参数
    fast=5
    slow=10

    # 调用给方法添加常驻策略
    def OnInit(self,**kw):
        # 添加品种 'EUR_USD.D' 获取数据库中的closeBid列 点数为EUR_USD的点数
        self.addSymbol('EUR_USD.D',['closeBid'],point=point.EUR_USD)
        # 在data['EUR_USD.D']中添加ma列
        self.setIndicator('ma','EUR_USD.D')
        # 在data中添加ma列
        self.setIndicator('ma')

    def onBar(self,data):

        # 计算当前ma
        ma=getInd('MA',data.closeBid[-10:],timeperiod=10)[-1]
        # 将当前ma插入data中的ma列
        data.importData(ma=ma)

        # 扫描订单
        for order in self.getAccount().orders:
            # 平仓
            self.close(order=order)

        # 如果当前ma大于前一根ma
        if len(data.ma)>=2 and ma>data.ma[-2]:
            # 开多
            self.open(lots=1)
            print 'open +1 at %s in %s ' % (data.closeBid[-1],data.time[-1])

        if len(data.ma)>=2 and ma<data.ma[-2]:
            # 开空
            self.open(lots=-1)
            print 'open -1 at %s in %s ' % (data.closeAsk[-1],data.time[-1])















# if __name__ == '__main__':
#     s=Strategy()