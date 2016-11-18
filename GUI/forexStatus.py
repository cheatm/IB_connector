from GUI.extra_plot import candle,histogram,direction_histogram
from bokeh.plotting import figure,output_file,show
from bokeh.layouts import gridplot
from support.dataManager import OandaManager
from datetime import datetime,timedelta

om=OandaManager()
symbols=['EUR_USD','AUD_USD','GBP_USD','NZD_USD','USD_JPY','USD_CAD']
cot_column='l-s'

def getData(symbol,manager=om,cot_column=cot_column):
    candle_=manager.mDb['%s.D' % symbol].find(
        {'datetime':{'$gte':datetime(2016,1,1)}},
        projection=['datetime','highMid','openMid','closeMid','lowMid']
    ).toDataFrame()
    sentiment=manager.mDb['%s.HPR' % symbol].find(
        {'datetime':{'$gte':datetime(2016,1,1)}},
        projection=['datetime','position']
    ).toDataFrame()
    cot=manager.mDb['%s.COT' % symbol].find(
        {'datetime':{'$gte':datetime(2016,1,1)}},
        projection=['datetime',cot_column]
    ).toDataFrame()
    candle_.pop('_id')
    sentiment.pop('_id')
    cot.pop('_id')

    return candle_,cot,sentiment

def symbol_chart(symbol,candle_,cot,sentiment):
    candlePlot=candle(candle_,c_width=timedelta(hours=10),title=symbol,height=200,x_axis_type="datetime")
    cotPlot=direction_histogram(cot,c_width=timedelta(days=3),value=cot_column,height=200,title='COT',
                      x_axis_type="datetime",x_range=candlePlot.x_range)
    sentimentPlot=direction_histogram(sentiment,c_width=timedelta(hours=10),value='position',height=200,title='sentiment',
                      x_axis_type="datetime",x_range=candlePlot.x_range)

    grid=gridplot([[candlePlot],[cotPlot],[sentimentPlot]])

    return grid

def main_chart(symbols):
    charts=[]
    for s in symbols:
        charts.append(
            symbol_chart(s,*getData(s))
        )
    grid=gridplot(charts,ncols=3)
    return grid

if __name__ == '__main__':
    output_file('forex_status.html')
    # plot1=symbol_chart(symbols[0],*getData(symbols[0]))
    # plot2=symbol_chart(symbols[1],*getData(symbols[1]))
    # grid=gridplot([plot1,plot2],ncols=2)
    show(
        main_chart(symbols)
    )