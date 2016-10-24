import thread
import threading
import time
import Queue

class Engine():

    __timing={}
    __timingControl={}
    __singleQueue=Queue.Queue()
    __runing=False


    def __init__(self):
        self.__singleThread=threading.Thread(target=self.__run)

    def __run(self):

        while self.__runing or not self.__singleQueue.empty() :
            try :
                task,args,kw=self.__singleQueue.get(block=True,timeout=2)
                task(*args,**kw)
            except Queue.Empty:
                pass

    def startSingle(self):
        self.__runing=True
        self.__singleThread.start()

    def stopSingle(self):
        self.__runing=False
        self.__singleThread.join(0)

    def put(self,task,*args,**kw):
        self.__singleQueue.put((task,args,kw))

    def registerTiming(self,name,timing,*args,**kw):
        self.__timingControl[name]=True
        kw['control']=self.__timingControl
        kw['name']=name
        self.__timing[name]=threading.Thread(target=timing,args=args,kwargs=kw)

    def startTiming(self,*names):
        if len(names)==0:
            names=self.__timing.keys()

        for name in names:
            if name in self.__timing:
                self.__timing[name].start()

    def stopTiming(self,*names):
        if len(names)==0:
            names=self.__timing.keys()

        for name in names:
            if name in self.__timing:
                self.__timingControl[name]=False
                self.__timing[name].join(timeout=0)

def func1(control,name):
    while control[name]:
        print 'timing1:',time.clock()
        time.sleep(2)

def func2(control,name):
    while control[name]:
        print 'timing2:',time.clock()
        time.sleep(3)

def func3(a):
    print 'sleep',a,':',time.clock()
    time.sleep(a)


if __name__ == '__main__':
    engine=Engine()
    engine.startSingle()
    time.sleep(4)
    engine.stopSingle()
