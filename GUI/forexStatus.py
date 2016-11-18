# encoding:utf-8
from GUI.extra_plot import candle,histogram,direction_histogram
from bokeh.plotting import figure,output_file,show
from bokeh.layouts import gridplot
from datetime import datetime,timedelta
from DataBase.Client import connectDB

client=connectDB('FinanceData')
symbols=['EUR_USD','AUD_USD','GBP_USD','NZD_USD','USD_JPY','USD_CAD']

def cot_column(symbol):
    if symbol.endswith('USD'):
        return 'l-s'
    else:
        return  's-l'

def getData(symbol,client=client):
    # 获取candle数据
    candle_=client.Oanda['%s.D' % symbol].find(
        {'datetime':{'$gte':datetime(2016,1,1)}},
        projection=['datetime','highMid','openMid','closeMid','lowMid']
    ).toDataFrame()
    # 获取HPR数据
    sentiment=client.Oanda['%s.HPR' % symbol].find(
        {'datetime':{'$gte':datetime(2016,1,1)}},
        projection=['datetime','position']
    ).toDataFrame()
    # 获取COT数据
    cot=client.Oanda['%s.COT' % symbol].find(
        {'datetime':{'$gte':datetime(2016,1,1)}},
        projection=['datetime',cot_column(symbol)]
    ).toDataFrame()
    candle_.pop('_id')
    sentiment.pop('_id')
    cot.pop('_id')

    # 返回数据
    return candle_,cot,sentiment

def symbol_chart(symbol,candle_,cot,sentiment):
    '''

    :param symbol:
    :param candle_: candle数据
    :param cot: cot数据
    :param sentiment: hpr数据
    :return:
    '''

    # 画蜡烛图
    candlePlot=candle(candle_,c_width=timedelta(hours=10),title=symbol,height=200,x_axis_type="datetime")
    # 画cot柱图
    cotPlot=direction_histogram(cot,c_width=timedelta(days=3),value=cot_column(symbol),height=200,title='COT',
                      x_axis_type="datetime",x_range=candlePlot.x_range)
    # 画hpr柱图
    sentimentPlot=direction_histogram(sentiment,c_width=timedelta(hours=10),value='position',height=200,title='sentiment',
                      x_axis_type="datetime",x_range=candlePlot.x_range)

    # 三合一张图
    grid=gridplot([[candlePlot],[cotPlot],[sentimentPlot]])

    # 返回合成的图
    return grid

def main_chart(symbols):
    charts=[]
    for s in symbols:
        # 将各货币对的图添加在一张表里
        charts.append(
            symbol_chart(s,*getData(s))
        )
    # 合成表里的图
    grid=gridplot(charts,ncols=3)
    # 返回图
    return grid

if __name__ == '__main__':
    output_file('forex_status.html')
    # 画图
    show(
        main_chart(symbols)
    )