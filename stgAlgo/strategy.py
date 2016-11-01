import time

class Strategy(object):

    def __init__(self,engine,**kw):

        self.engine=engine

    def set_params(self,**params):
        for p in params:
            if hasattr(self,p):
                self.__setattr__(p,params[p])
            else:
                raise AttributeError("No param names '%s' " % p)

    def set_engine(self,engine):
        self.engine=engine

    def OnInit(self,**kw):
        pass

    def setIndicator(self,name,indicator,collection,*inputs,**params):
        self.engine.addIndicator([name,indicator,collection,inputs,params])


    def onBar(self,**data):
        pass

    def buy(self,**order):
        self.engine.buy(**order)

    def sell(self,**order):
        self.engine.sell(**order)

    def get(self,**kw):
        return self.engine.get(**kw)




# if __name__ == '__main__':
#     s=Strategy()