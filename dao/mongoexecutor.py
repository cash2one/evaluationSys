#/***************************************************************************
# * 
# * Copyright (c) 2016 Baidu.com, Inc. All Rights Reserved
# * 
# **************************************************************************/
# 
# 
# 
#/**
# * @file dbHelper.py
# * @author lihuipeng(com@baidu.com)
# * @date 2016/03/21 19:48:51
# * @brief 
# *  
# **/

import os
import sys
import pymongo
import threading
import json
from conf.db import MONGO

class MongoExecutor(object):
    instance = None
    mutex = threading.Lock()
    def __init__(self, dbCfg):
        #self.conn = pymongo.Connection(dbCfg['host'], dbCfg['port'])
        self.conn = pymongo.MongoClient(dbCfg['host'], dbCfg['port'])
        self.db = self.conn[dbCfg['db']]
        self.collection = self.db['intentionCustomer']

    @staticmethod
    def getInstance(dbCfg=MONGO):
        if (MongoExecutor.instance == None):
            MongoExecutor.mutex.acquire()
            if (MongoExecutor.instance == None):
                MongoExecutor.instance = MongoExecutor(dbCfg)
            MongoExecutor.mutex.release()
        return MongoExecutor.instance

    def __del__(self):
        pass

    def test(self):
        return self.collection.find_one()
    
    def insert(self, recordJson):
        try:
            self.collection.insert(recordJson)
            return True
        except Exception as e:
            print e
        return False

    def replace_one(self, filter, replacement, upsert=False):
        try:
            self.collection.replace_one(filter, replacement, upsert)
            return True
        except Exception as e:
            print e
        return False
