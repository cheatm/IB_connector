import time

class Strategy():

    onBarData={}
    indicators=[]

    def __init__(self,engine,collection=None,**kw):

        self.engine=engine


    def onBar(self,**data):
        pass


    def buy(self):
        self.engine.buy()

    def sell(self):
        self.engine.sell()



if __name__ == '__main__':
    pass