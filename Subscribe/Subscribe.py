import json
import os,os.path
from ib.ext.Contract import Contract



def getRootDir(path=os.getcwd()):
    if os.path.exists('%s/ROOT' % path):
        return path
    else:
        return getRootDir(os.path.dirname(path))

contractDir='%s\Contracts' % getRootDir()

def makeContract(**kw):
    '''

    :param args:
    :param kw:
    :return:

    '''
    # defaltAttributes=['m_symbol','m_secType','m_expiry','m_currency','m_exchange','m_strike','m_right']
    contract=Contract()

    # n=0
    # for attr in defaltAttributes:
    #     contract.__setattr__(attr,args[n])
    #     n+=1

    for k in kw.keys():
        contract.__setattr__(k,kw[k])

    return contract


def saveContract(name=None,subscribe=0,period=[],**kwds):
    name = name if name is not None else kwds['m_symbol'] if 'm_symbol' in kwds else None
    if name is None:
        return

    name='%s.json' % name
    filepath='%s\%s' % (contractDir,name)

    if os.path.exists(filepath):
        print name[:-5],'exits, try another name'
        return

    cdict={'contract':kwds}
    cdict['subscribed']=subscribe
    cdict['period']=period

    jsting=json.dumps(cdict)

    file=open(filepath,'w')
    file.write(jsting)
    file.close()

def readContract(name):

    filepath='%s\%s.json' % (contractDir,name)
    print(filepath)
    if os.path.exists(filepath):
        cdict = json.load(open(filepath),encoding='utf-8')['contract']

        for k in cdict:
            cdict[k]=str(cdict[k])
        return makeContract(**cdict)

def u2s(x):
    for a in range(0,len(x)):
        x[a]=str(x[a])

def readSubscribed():
    subdict={}
    for cont in tuple(os.walk(contractDir))[0][2]:
        if 'json' in cont:
            filepath='%s/%s' % (contractDir,cont)
            cdict=json.load(open(filepath))

            if  not cdict['subscribed']:
                continue

            contractDict=cdict['contract']
            for k in contractDict:
                contractDict[k]=str(contractDict[k])
            u2s(cdict['period'])
            subdict[cont[:-5]]=((makeContract(**contractDict),
                            cdict['period']))

    return subdict





if __name__ == '__main__':
    pass
