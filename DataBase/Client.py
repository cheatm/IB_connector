import pymongo
import os,os.path
import json


def getRootDir(path=os.getcwd()):
    if os.path.exists('%s/ROOT' % path):
        return path
    else:
        return getRootDir(os.path.dirname(path))

db_info_dir='%s/DataBase' % getRootDir()

def connectDB(dbname='FinanceData'):
    info= getDBinfo(dbname)
    return connect(**info)


def connect(**info):
    users=info.pop('user',{})
    client=pymongo.MongoClient(**info)

    for db in users:
        client[db].authenticate(users[db]['id'],users[db]['password'])

    return client

def getDBinfo(dbname):
    filepath='%s/%s.json' % (db_info_dir,dbname)
    info=json.load(open(filepath))
    return info
