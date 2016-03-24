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

import MySQLdb

#class SqlExecutor(object):
#    def __init__(self, dbCfg):
#        self.conn = MySQLdb.connect(host=dbCfg['host'], user=dbCfg['user'], passwd=dbCfg['passwd'], port=dbCfg['port'], db=dbCfg['db'])
#        self.cursor = self.conn.cursor()
#
#
#    def select(self, sql):
#        ret = []
#        try:
#            self.cursor.execute(sql)
#            results = self.cursor.fetchall()
#            for row in results:
#                ret.append(row)
#        except Exception as e:
#            print e
#            return False
#        return ret
#
#    def insert(self, sql):
#        try:
#            ret = self.cursor.execute(sql)
#            self.conn.commit()
#            return ret
#        except Exception as e:
#            self.conn.rollback()
#            print e
#            return False

import threading
from conf.common import CFG

class SqlExecutor(object):
    instance = None
    mutex = threading.Lock()
    def __init__(self, dbCfg):
        self.conn = MySQLdb.connect(host=dbCfg['host'], user=dbCfg['user'], passwd=dbCfg['passwd'], port=dbCfg['port'], db=dbCfg['db'])
        self.cursor = self.conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)

    @staticmethod
    def getInstance(dbCfg=CFG['db']):
        if (SqlExecutor.instance == None):
            SqlExecutor.mutex.acquire()
            if (SqlExecutor.instance == None):
                SqlExecutor.instance = SqlExecutor(dbCfg)
            SqlExecutor.mutex.release()
        return SqlExecutor.instance

    def __del__(self):
        pass

    def select(self, sql):
        ret = []
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            for row in results:
                ret.append(row)
        except Exception as e:
            print e
            return False
        return ret

    def insert(self, sql):
        try:
            ret = self.cursor.execute(sql)
            self.conn.commit()
            return ret
        except Exception as e:
            print e
            return False

    def update(self, sql):
        try:
            ret = self.cursor.execute(sql)
            self.conn.commit()
            return ret
        except Exception as e:
            print e
            return False

    def getLastRowId(self):
        try:
            return int(self.cursor.lastrowid)
        except Exception as e:
            print e
            return False

