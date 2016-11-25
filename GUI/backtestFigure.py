# encoding:utf-8
import pandas
import GUI.extra_plot as extra
from bokeh.plotting import figure,output_file,show
from bokeh.layouts import gridplot
from datetime import datetime,timedelta


class BackTestOutPut(object):
    figures=[]
    defaultType=dir(extra)

    def __init__(self,acc,data,**kwargs):
        '''

        :param acc: Account()
        :param data: ActiveData() or DataFrame()
        :param kwargs: params for main figure (candle)
        :return:
        '''
        self.acc=acc

        self.data=data if  isinstance(data,pandas.DataFrame) \
            else self.joinFrame(data,'datetime',*data.columns)

        self.x_axis_type=kwargs.pop('x_axis_type','datetime')
        self.width=kwargs.pop('width',1300)
        self.height=kwargs.pop('height',300)

        self.__initChart(
            kwargs.pop('columns',['datetime','closeMid','openMid','highMid','lowMid']),
            c_width=kwargs.pop('c_width',timedelta(hours=10)),
            **kwargs
        )

    def __plotHistory(self,figure0):
        history=self.acc.getHistoryOrders()
        sell= history[history.lots<0]
        buy= history[history.lots>0]
        figure0.segment(x0=buy.openTime,y0=buy.openPrice,
                        x1=buy.closeTime,y1=buy.closePrice,color='#dd2222')
        figure0.inverted_triangle(x=buy.closeTime,y=buy.closePrice,color='#dd2222',angle=270,angle_units='deg')
        figure0.inverted_triangle(x=buy.openTime,y=buy.openPrice,color='#dd2222',angle=90,angle_units='deg')
        figure0.segment(x0=sell.openTime,y0=sell.openPrice,
                        x1=sell.closeTime,y1=sell.closePrice,color='#22cc55')
        figure0.inverted_triangle(x=sell.closeTime,y=sell.closePrice,size=8,color='#22cc55',angle=270,angle_units='deg')
        figure0.inverted_triangle(x=sell.openTime,y=sell.openPrice,size=8,color='#22cc55',angle=90,angle_units='deg')

    def __plotCapital(self,figure0):
        log=self.acc.getLog()
        log=log[log['datetime']>self.data['datetime'][0]]
        self.capital=figure(width=self.width,height=self.height,x_axis_type='datetime',x_range=figure0.x_range)
        self.capital.line(log['datetime'],log['capital'])

    def __initChart(self,columns,c_width,**kw):
        candle_frame=self.data.copy()[columns]
        figure0=extra.candle(candle_frame,c_width,width=self.width,height=400,x_axis_type='datetime')

        self.__plotHistory(figure0)
        self.__plotCapital(figure0)

        self.figures.append(figure0)

    def joinFrame(self,data,on='datetime',*columns):
        side=[]
        main=[]
        length=[]
        for c in columns:
            if isinstance(data[c][0],dict):
                side.append(
                    pandas.DataFrame(data[c])
                )
            else:
                length.append(len(data[c]))
                main.append(c)
        ml=min(length)
        Frame=pandas.DataFrame(
            dict(
                [(key,data[key][-ml:]) for key in main]
            )
        )

        for s in side:
            Frame=pandas.merge(Frame,s,on=on)

        return Frame

    def plot(self,y,x='datetime',Type='line',n=0,**kwargs):
        '''

        :param y: 纵坐标
        :param n: 在第n张figure中画图,默认0
        :param x: 横坐标，默认datetime
        :param Type: 图表类型，详见:
            http://bokeh.pydata.org/en/latest/docs/reference/plotting.html
        :param kwargs: 画图参数
        :return:
        '''
        plot=self.getFigure(n)
        getattr(plot,Type)(x=self.data[x],y=self.data[y],**kwargs)
        self.figures[n]=plot
        return self

    def insert(self,n,figure):
        self.figures.insert(n,figure)


    def show(self,file_name):
        output_file(file_name)
        figures=self.figures
        figures.append(self.capital)
        show(gridplot(figures,ncols=1))


    def getFigure(self,n=0,default=True,**kwargs):
        '''
        :param n: 获取序号为n的figure ，如果没有找到则在创建新的figure，序号为n
        :param default:
            True：按照默认参数创建figure
            False：按照**kwargs创建figure
        :param kwargs: 创建figure的参数
        :return:
        '''
        while n>=len(self.figures):
            self.figures.append(None)
        if self.figures[n] is None:
            if default:
                self.figures[n]=figure(
                    width=self.width,height=self.height,
                    x_axis_type=self.x_axis_type,x_range=self.figures[0].x_range
                )
            else:
                self.figures[n]=figure(**kwargs)
        return self.figures[n]


if __name__ == '__main__':
    pass






