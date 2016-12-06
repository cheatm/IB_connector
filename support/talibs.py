import talib
import pandas
import numpy

def getInd(indicator,*inputs,**params):
    '''

    :param indicator: name of indicator in talib
    :param inputs:
        datas for talib input
        get more in TAlib_indicators.txt
    :param params:
        params to be used
        get more in TAlib_indicators.txt

    How to use:
        Find 'RSI' in TAlib_indicators.txt:
            ------------------------------------------------------------------------------------
            RSI:
            RSI([input_arrays], [timeperiod=14])

            Relative Strength Index (Momentum Indicators)

            Inputs:
                price: (any ndarray)
            Parameters:
                timeperiod: 14
            Outputs:
                real
            ------------------------------------------------------------------------------------

                            (Inputs)  (Parameters)
            rsi=getInd('RSI',pricelist,timeperiod=10)

    :return: DataFrame
    '''

    arrayValues=[]

    for v in inputs:

        if isinstance(v,numpy.ndarray):
            arrayValues.append(v)
        else:
            arrayValues.append(numpy.array(v))

    ind=getattr(talib,indicator)(*arrayValues,**params)

    return ind


def getIndicator(indicator,time,*inputs,**params):

    '''

    :param indicator: name of indicator in talib
    :param time: TimeArray in seconds
    :param names:

    :param inputs:
        datas to caculate,
        get more in TAlib_indicators.txt
    :param params:
        params to be used
        get more in TAlib_indicators.txt

    How to use:
        Find 'RSI' in TAlib_indicators.txt:
            ------------------------------------------------------------------------------------
            RSI:
            RSI([input_arrays], [timeperiod=14])

            Relative Strength Index (Momentum Indicators)

            Inputs:
                price: (any ndarray)
            Parameters:
                timeperiod: 14
            Outputs:
                real
            ------------------------------------------------------------------------------------

                                           (Inputs)  (Parameters)
            rsi=getIndicator('RSI',timelist,pricelist,timeperiod=10)

    :return: DataFrame
    '''



    if len(time)!=len(inputs[0]):
        print 'length not equal'
        return

    ind = getInd(indicator,*inputs,**params)

    try:
        data={time.name:time}
    except:
        data={'time':time}

    if not isinstance(ind,tuple):
        data[0]=ind
    else:
        for d in range(0,len(ind)):
            data[d]=ind[d]

    ind=pandas.DataFrame(data).dropna()

    return ind


if __name__ == '__main__':
    # import pymongo
    # client=pymongo.MongoClient(port=10001)
    # data=client.Oanda['GBP_USD.D'].find(projection=['closeBid']).toDataFrame()
    # print data['closeBid']



    pass