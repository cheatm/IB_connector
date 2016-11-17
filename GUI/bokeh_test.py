# from bokeh.charts import Bar,output_file,show
from bokeh.plotting import figure,output_file,show
from bokeh.models import HoverTool,BoxSelectTool
from bokeh.layouts import gridplot
from DataBase.Client import connectDB
from datetime import datetime,timedelta
import pandas
from support.talibs import getIndicator

def candle(up,down):
    output_file('plot.html')

    plot=figure(title='candle',height=300, x_axis_type="datetime",width=1000)
    plot.add_tools(HoverTool(),BoxSelectTool())
    plot.quad(left=up.left,right=up.right,top=up.closeMid,bottom=up.openMid)
    plot.quad(left=down.left,right=down.right,top=down.openMid,bottom=down.closeMid,color='#AA1111')
    plot.segment(x0=up.index,y0=up.lowMid,x1=up.index,y1=up.highMid)
    plot.segment(x0=down.index,y0=down.lowMid,x1=down.index,y1=down.highMid,color='#AA1111')
    return plot


if __name__ == '__main__':
    client=connectDB('FinanceData')
    data=client.Data['HSI'].find(
        {'tradeDate':{'$gte':datetime(2015,1,1),'$lte':datetime(2016,11,1)}},
        projection=['tradeDate','closeIndex']
    ).toDataFrame()
    from extra_plot import candle,histogram
    output_file('plot.html')
    # plot=candle(data,c_width=timedelta(hours=10),width=1000,x_axis_type="datetime",title='candle')
    MACD=getIndicator('MACD',data['tradeDate'],data['closeIndex'])
    MACD=MACD[[2,'time']]
    MACD.columns=['value','datetime']
    plot=histogram(MACD,c_width=timedelta(hours=10),x_axis_type='datetime',width=1000)
    show(plot)

