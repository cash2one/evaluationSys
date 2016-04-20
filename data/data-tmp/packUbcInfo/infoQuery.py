#!/usr/bin/python
#-*-coding:utf-8 -*-

"""
File: hbaseAccessor.py 
hbaseAccessor class
"""

#####################################################################
#
#Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
#
#####################################################################
import preloadmodule

import os
import sys
import json
import re
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from hbase import THBaseService  
from hbase.ttypes import *
reload(sys)
sys.setdefaultencoding('utf-8')

class HbaseDataDrive(object):

    """
            IP address
            port
            table name
    """
    def __init__(self, address, port, table):
        self.tableName = table

        #connect hbase
        self.transport = TTransport.TBufferedTransport(TSocket.TSocket(address, port))

        self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)

        self.client = THBaseService.Client(self.protocol)
        self.transport.open()

    #close transport
    def __del__(self):
        self.transport.close()

    #create Table
    def __createTable(self):
        col1 = ColumnDescriptor(name="applist:", maxVersions=1)
        col2 = ColumnDescriptor(name="lbs:", maxVersions=1)
        col3 = ColumnDescriptor(name="zhidahao:", maxVersions=1)
        self.client.createTable(self.tableName, [col1, col2, col3])

    def write(self, content):
        """write content """
        row = content['cuid']
        mutations = [Mutation(column="applist:apps", value=content['apps'])]
        self.client.mutateRow(self.tableName, row, mutations, None)

    def read(self):
        """read data"""
        scanner = TScan()
        scannerId = self.client.scannerOpenWithScan(self.tableName, scanner, None)
        result = True
        while result:
            try:
                result = self.client.scannerGetList(scannerId, 500)
                for rowRet in result:
                    print "%s" % rowRet.row
            except:
                print "fail"
                #break
            #contents = result
            #print contents
        self.client.scannerClose(scannerId)

    def scanAndHandle(self,key):
        """scanAndHandle"""
        print key
        tget = TGet()
        tget.row=key
        dataRet = self.client.get(self.tableName,tget)
        if dataRet:
                    sourceData = {}
                    sourceData['rowkey'] = dataRet.row
                    columnsDict={}
                    for columnItem in dataRet.columnValues:
                            key=columnItem.family+":"+columnItem.qualifier
                            columnsDict[key]=columnItem.value
                    if columnsDict.has_key("bdinput:inputstring"):
                            sourceData["bdinput:inputstring"]=json.loads(columnsDict["bdinput:inputstring"])
                    if columnsDict.has_key("wisequery:querystring"):
                            sourceData["wisequery:querystring"]=json.loads(columnsDict["wisequery:querystring"])
                    if columnsDict.has_key("applist:operation"):
                            sourceData["applist:operation"]=json.loads(columnsDict["applist:operation"])
                    if columnsDict.has_key("lbs:homeplace"):
                            sourceData["lbs:homeplace"]=re.sub("\"","",columnsDict["lbs:homeplace"])
                    if columnsDict.has_key("lbs:workplace"):
                            sourceData["lbs:workplace"]=re.sub("\"","",columnsDict["lbs:workplace"])
                    if columnsDict.has_key("erised:fig"):
                            sourceData["erised"]=json.loads(columnsDict["erised:fig"])
                    print json.dumps(sourceData,ensure_ascii=False).encode("utf-8")


if __name__ == "__main__":
    client = HbaseDataDrive("dbl-sumeru-qingpai01.dbl01.baidu.com", "9090", "user_behavior_collect")
    for line in sys.stdin:
        line=line.strip()
        line=line.upper()
        client.scanAndHandle(line)
