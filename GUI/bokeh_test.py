# from bokeh.charts import Bar,output_file,show
from bokeh.plotting import figure,output_file,show
from bokeh.models import HoverTool,BoxSelectTool
from bokeh.layouts import gridplot
from DataBase.Client import connectDB
from datetime import datetime,timedelta
import pandas
from support.talibs import getIndicator




if __name__ == '__main__':
    client=connectDB('FinanceData')
    data=client.Data['HSI'].find(
        {'tradeDate':{'$gte':datetime(2015,1,1),'$lte':datetime(2016,11,1)}},
        projection=['tradeDate','closeIndex','highestIndex','lowestIndex','openIndex']
    ).toDataFrame()
    from extra_plot import candle,histogram
    output_file('plot.html')
    data['datetime']=data.pop('tradeDate')
    plot=candle(data,c_width=timedelta(hours=10),width=1500,x_axis_type="datetime",title='candle',height=350,
                trans={'high':'highestIndex','low':'lowestIndex','open':'openIndex','close':'closeIndex'}
                )

    # for i in data.index[1:]:
    #     data

    data['range']=0
    for i in data.index[1:]:
        data.set_value(i,'range',
                       data.get_value(i,'closeIndex')-data.get_value(i-1,'closeIndex'))
    data['range']=data['range']/data['closeIndex']

    plot2=histogram(data[['datetime','range']],c_width=timedelta(hours=10),value='range',
                    width=1500,height=350,x_axis_type="datetime")

    plot2.x_range=plot.x_range

    grid=gridplot([[plot],[plot2]])
    show(grid)

