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
from strategyManager import StrategyManager

reload(sys)
sys.setdefaultencoding('utf8')


CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

class JobManager(object):
    
    def run(self):
        argp = ArgumentParser()
        argp.add_argument('-m', '-method', dest='method', choices=['add', 'list', 'check'])
        argp.add_argument('-v', '-vesion', '-strategy_version', dest='strategy_version')
        argp.add_argument('-i', '-id', '-job_id', dest='job_id')
    
        args = argp.parse_args()
       
        try:
            self.do(args)
        except Exception as e:
            print e
        else:
            pass
        finally:
            pass

    def do(self, args):
        try:
            if args.method == 'add':
                strategyVersion = args.strategy_version if args.strategy_version else 0
                self.add(strategyVersion)
            elif args.method == 'list':
                self.list()
            elif args.method == 'check':
                jobId = args.job_id if hasattr(args, 'job_id') else ''
                self.check(jobId)
                pass
        except Exception as e:
            print e

    #添加新job
    def add(self, strategyVersion):
        if not strategyVersion:
            raise Exception('no strategyVersion is set')
  
        try:
            #check if strategyVersion exists
            strategyManager = StrategyManager()
            strategyVersionInfo = strategyManager.getVersionInfo(strategyVersion)
            print strategyVersionInfo
            if strategyVersionInfo:
                #add new job 
                jobId = self.addNewJob(strategyVersion)
                print 'add new job success! jobId =', jobId
            else:
                print 'no strategyVersion is found:', strategyVersion
        except Exception as e:
            print e

    #查看job列表
    def list(self, pn=0, ps=50):
        try:
            offset = int(pn) * int(ps)
            size = int(ps)
            ret = self.getJobList(offset, size)
            print '*' * 200
            print '{0:20s}{1:30s}{2:30s}{3:30s}{4:30s}{5:30s}{6:30s}'.format('strategy_version', 'create_time', 'update_time', 'job_status', 'accuracy_rate', 'precision_rate', 'recall_rate')
            print '*' * 200
            for jobRecord in ret:
                strcTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jobRecord['ctime']))
                strmTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jobRecord['mtime']))
                print '{0:20s}{1:30s}{2:30s}{3:30s}{4:30s}{5:30s}{6:30s}'.format(str(jobRecord['strategy_version']), strcTime, strmTime, str(jobRecord['job_status']), str(jobRecord['accuracy_rate']), str(jobRecord['precision_rate']), str(jobRecord['recall_rate']))
            print '*' * 200
        except Exception as e:
            raise Exception('list error')

    def check(self, jobId):
        try:
            jobInfo = self.getJobInfo(jobId)
            if jobInfo:
                strcTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jobInfo['ctime']))
                strmTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(jobInfo['mtime']))
                print '*' * 200
                print '{0:20s}{1:30s}{2:30s}{3:30s}{4:30s}{5:30s}{6:30s}'.format('strategy_version', 'create_time', 'update_time', 'job_status', 'accuracy_rate', 'precision_rate', 'recall_rate')
                print '*' * 200
                print '{0:20s}{1:30s}{2:30s}{3:30s}{4:30s}{5:30s}{6:30s}'.format(str(jobInfo['strategy_version']), strcTime, strmTime, str(jobInfo['job_status']), str(jobInfo['accuracy_rate']), str(jobInfo['precision_rate']), str(jobInfo['recall_rate']))
                print '*' * 200
                print 'check job success!'
            else:
                print 'jobId not exists:', jobId
        except Exception as e:
            raise Exception('check error')
        pass

    #添加新job
    def addNewJob(self, strategyVersion):
        try:
            sqlExecutor = SqlExecutor.getInstance()
            curTime = int(time.time())
            sql = 'insert into jobpool(strategy_version, ctime, mtime) values({0}, {1}, {2})'.format(strategyVersion, curTime, curTime)
            #print sql
            ret = sqlExecutor.insert(sql)
            lastId = sqlExecutor.getLastRowId()
            return lastId
        except Exception as e:
            raise Exception('addNewJob error')

    #查询job列表
    def getJobList(self, offset=0, size=50):
        try:
            sqlExecutor = SqlExecutor.getInstance()
            sql = 'select * from jobpool limit {0}, {1}'.format(int(offset), int(size))
            ret = sqlExecutor.select(sql)
            return ret
        except Exception as e:
            raise Exception('getJobList error')

    #查询job
    def getJobInfo(self, jobId):
        try:
            sqlExecutor = SqlExecutor.getInstance()
            sql = 'select * from jobpool where id={0}'.format(int(jobId))
            ret = sqlExecutor.select(sql)
            if len(ret) > 0:
                return ret[0]
            else:
                return {}
        except Exception as e:
            raise Exception('getJobInfo error')


if __name__ == '__main__':
    try:
        jobManager = JobManager()
        jobManager.run()
    except:
        sys.exit('Error encountered.')
