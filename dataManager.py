# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import logging
import logging.config
import os
import sys
import time
import datetime
import commands

from conf.common import *
from dao.sqlexecutor import SqlExecutor

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

class DataManager(object):
    
    def run(self):
        argp = ArgumentParser()
        argp.add_argument('data_type', choices=['feature', 'sample', 'action'])
        argp.add_argument('-m', '-method', dest='method', choices=['add', 'list', 'get'])
        argp.add_argument('-f', '-file', dest='file')
        argp.add_argument('-v', '-version', '-data_version', dest='data_version')
        argp.add_argument('-name', dest='version_name')
        argp.add_argument('-desc', dest='version_desc')
        args = argp.parse_args()

        try:
            self.do(args)
        except Exception as e:
            print e
        finally:
            pass

    def do(self, args):
        try:
            if args.method == 'add':
                strDataType = args.data_type
                versionName = args.version_name if args.version_name else ''
                versionDesc = args.version_desc if args.version_desc else ''
                srcFile = args.file if args.file else ''
                self.add(strDataType, versionName, versionDesc, srcFile)
            elif args.method == 'list':
                strDataType = args.data_type
                self.list(strDataType)
            elif args.method == 'get':
                strDataType = args.data_type
                versionCode = args.data_version if args.data_version else ''
                self.get(strDataType, versionCode)
        except Exception as e:
            print e

    #添加新版本
    def add(self, strDataType, versionName, versionDesc, srcFile):
        if srcFile == None or srcFile == '':
            raise Exception('no src file is set')
  
        intDataType = DATA_TYPE[strDataType]
        versionCode = datetime.datetime.now().strftime('%Y%m%d%H%M')
        destFile = '{0}_{1}.txt'.format(strDataType, versionCode)
        try:
            #1. copy file to dest
            self.persistFile(srcFile, destFile)

            #2. add version info
            self.addNewVersion(intDataType, destFile, versionCode, versionName, versionDesc)
            print 'add new version success! version code =', versionCode

            self.deleteTmpFile(srcFile)

        except Exception as e:
            print e

    #查看版本列表
    def list(self, strDataType):
        try:
            intDataType = DATA_TYPE[strDataType]
            ret = self.getVersionList(intDataType)
            print '*' * 100
            print '{0:20s}{1:30s}{2:30s}{3:30s}'.format('version_code', 'version_name', 'file', 'create_time')
            print '*' * 100
            for versionRecord in ret:
                strTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(versionRecord['ctime']))
                print '{0:20s}{1:30s}{2:30s}{3:30s}'.format(str(versionRecord['version_code']), versionRecord['version_name'], versionRecord['file_path'], strTime)
            print '*' * 100
        except Exception as e:
            raise Exception('list error')

    def get(self, strDataType, versionCode):
        try:
            intDataType = DATA_TYPE[strDataType]
            dataVersionInfo = self.getVersionInfo(intDataType, versionCode)
            if not dataVersionInfo:
                print 'dataVersion not found:', versionCode
                return

            return self.getPersistedFile(dataVersionInfo['file_path'])
        except Exception as e:
            print e

    #持久化原始数据文件到文件系统
    def persistFile(self, srcFile, destFile):
        try:
            if srcFile[0] != '/':
                srcFile = TMP_DATA_PATH + srcFile 
            destFile = WAREHOUSE_DATA_PATH + destFile
            cmd = 'mv {0} {1}'.format(srcFile, destFile)
            print cmd
            cmdStatus, cmdOutput = commands.getstatusoutput(cmd)
            if (cmdStatus != 0):
                raise Exception('copy file error')
        except Exception as e:
            print e
            raise Exception('persist file error')

    def deleteTmpFile(self, srcFile):
        if srcFile[0] != '/':
            srcFile = TMP_DATA_PATH + srcFile 
        cmd = 'rm -f {0}'.format(srcFile)
        print cmd
        cmdStatus, cmdOutput = commands.getstatusoutput(cmd)

    def getPersistedFile(self, destFile):
        try:
            localFile = TMP_DATA_PATH + destFile
            destFile = WAREHOUSE_DATA_PATH + destFile
            cmd = 'mv {0} {1}'.format(destFile, localFile)
            print cmd
            cmdStatus, cmdOutput = commands.getstatusoutput(cmd)
            if (cmdStatus != 0):
                raise Exception('copy file error')
            return localFile
        except Exception as e:
            print e
            raise Exception('getPersistedFile error')

    #添加新数据版本
    def addNewVersion(self, intDataType, destFile, versionCode, versionName='', versionDesc=''):
        try:
            sqlExecutor = SqlExecutor.getInstance()
            sql = 'insert into data_version(data_type, version_code, version_name, version_desc, file_path, ctime) values({data_type},{version_code},\'{version_name}\',\'{version_desc}\', \'{file_path}\', {ctime})'.format(data_type=intDataType, version_code=versionCode, version_name=versionName, version_desc=versionDesc, file_path=destFile, ctime=int(time.time()))
            #print sql
            ret = sqlExecutor.insert(sql)
        except Exception as e:
            raise Exception('addNewVersion error')

    #根据数据类型得到版本列表
    def getVersionList(self, intDataType):
        try:
            sqlExecutor = SqlExecutor.getInstance()
            sql = 'select * from data_version where data_type={0:1d} order by version_code desc'.format(intDataType)
            ret = sqlExecutor.select(sql)
            return ret
        except Exception as e:
            raise Exception('getVersionList error')
    
    def getVersionInfo(self, intDataType, versionCode):
        try:
            sqlExecutor = SqlExecutor.getInstance()
            sql = 'select * from data_version where data_type={0} and version_code={1}'.format(int(intDataType), int(versionCode))
            ret = sqlExecutor.select(sql)
            if len(ret) > 0:
                return ret[0]
            else:
                return {}
        except Exception as e:
            raise Exception('getVersionList error')


if __name__ == '__main__':
    try:
        dataManager = DataManager()
        dataManager.run()
    except:
        sys.exit('Error encountered.')
