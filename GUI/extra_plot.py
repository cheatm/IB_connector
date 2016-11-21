from bokeh.plotting import figure
from datetime import timedelta

def candle(df,c_width,upColor='#AA1111',downColor='#1188AA',**kwargs):
    '''

    :param df:
    :param c_width:
    :param upColor:
    :param downColor:
    :param kwargs:
    :return:
    '''
    trans=kwargs.pop(
        'trans',
        {'high':'highMid','low':'lowMid','open':'openMid','close':'closeMid'}
    )

    df['left']=df['datetime']-c_width
    df['right']=df['datetime']+c_width

    up=getUp(df,trans)
    down=getDown(df,trans)

    plot=figure(**kwargs)
    plot.quad(left=up.left,right=up.right,top=up[trans['close']],bottom=up[trans['open']],color=upColor)
    plot.quad(left=down.left,right=down.right,top=down[trans['close']],bottom=down[trans['open']],color=downColor)
    plot.segment(x0=up.datetime,x1=up.datetime,y0=up[trans['high']],y1=up[trans['low']],color=upColor)
    plot.segment(x0=down.datetime,x1=down.datetime,y0=down[trans['high']],y1=down[trans['low']],color=downColor)

    return plot

def getUp(df,trans):
    return df[df[trans['open']]<=df[trans['close']]]

def getDown(df,trans):
    return df[df[trans['open']]>df[trans['close']]]

def histogram(df,c_width,value='value',dt='datetime',color='#115599',**kwargs):
    df['left']=df[dt]-c_width
    df['right']=df[dt]+c_width

    up=df[df[value]>=0]
    down=df[df[value]<0]

    plot=figure(**kwargs)
    plot.quad(left=up.left,right=up.right,top=up[value],bottom=0,color=color)
    plot.quad(left=down.left,right=down.right,top=0,bottom=down[value],color=color)

    return plot

def direction_histogram(df,c_width,value='value',dt='datetime',upColor='#aa1122',downColor='#22aa11',**kwargs):
    df['left']=df[dt]-c_width
    df['right']=df[dt]+c_width

    df['dir']=0.0
    for i in df.index[1:]:
        df.set_value(i,'dir',df.get_value(i,value)-df.get_value(i-1,value))


    up=df[df[value]>=0]
    up_u=up[up['dir']>=0]
    up_d=up[up['dir']<0]
    down=df[df[value]<0]
    down_u=down[down['dir']>=0]
    down_d=down[down['dir']<0]


    plot=figure(**kwargs)
    plot.quad(left=up_u.left,right=up_u.right,top=up_u[value],bottom=0,color=upColor)
    plot.quad(left=up_d.left,right=up_d.right,top=up_d[value],bottom=0,color=downColor)
    plot.quad(left=down_u.left,right=down_u.right,top=0,bottom=down_u[value],color=upColor)
    plot.quad(left=down_d.left,right=down_d.right,top=0,bottom=down_d[value],color=downColor)
    return plot