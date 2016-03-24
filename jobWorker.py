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
from sqlexecutor import SqlExecutor
from strategyManager import StrategyManager
from dataManager import DataManager

reload(sys)
sys.setdefaultencoding('utf8')


CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

JOB_STATUS = {
        'UNSCHEDULED'   :   10,
        'SCHEDULED'     :   20,
        'PREPARING'     :   30,
        'PREPARED'      :   40,
        'COMPUTING'     :   50,
        'DONE'          :   100,
}

class JobWorker(object):
   
    jobInfo = None
    strategySrc = None 
    strategyFeature = None 
    strategySample = None 
    strategyAction = None 

    def run(self):
        #argp = ArgumentParser()
        #argp.add_argument('-m', '-method', dest='method', choices=['add', 'list', 'check'])
        #argp.add_argument('-v', '-vesion', '-strategy_version', dest='strategy_version')
        #argp.add_argument('-i', '-id', '-job_id', dest='job_id')
    
        #args = argp.parse_args()
       
        try:
            #1. 调度一个job
            self.jobInfo = self.schedule()
            if self.jobInfo:
                print 'start schedule job:', self.jobInfo['id']
            else:
                print 'no job can be dispatched'
                return

            self.preExecute(self.jobInfo['id'], self.jobInfo['strategy_version'])
            self.execute(self.jobInfo['id'])
            self.afterExecute(self.jobInfo['id'])
        except Exception as e:
            print e
        else:
            pass
        finally:
            pass

    def preExecute(self, jobId, strategyVersion):
        try:
            strategyManager = StrategyManager()
            strategyInfo = strategyManager.getVersionInfo(strategyVersion)
            if not strategyInfo:
                print 'strategyVersion invalid:', strategyVersion
                return

            self.strategySrc = self.getStragetySrc(strategyInfo)
            self.strategyFeature = self.getFeatureData(strategyInfo)
            self.strategySample = self.getSampleData(strategyInfo)
            self.strategyAction = self.getActionData(strategyInfo)

            #self.strategyMergedData = self.getStrategyMergedData()
        except Exception as e:
            print 'preExecute error', e


    def execute(self, jobId):
        pass

    def afterExecute(self, jobId):
        pass

    def getStragetySrc(self, strategyInfo):
        pass

    def getFeatureData(self, strategyInfo):
        #cmd = 'python dataManager.py feature -m get -v {0}'.format(strategyInfo['feature_version'])
        #print cmd
        #cmdStatus, cmdOutput = commands.getstatusoutput(cmd)
        #print 'getFeatureData result:' , cmdOutput
        #if (cmdStatus != 0):
        #    raise Exception('getFeatureData error')
        dataManager = DataManager()
        data = dataManager.get('feature', strategyInfo['feature_version'])
        print data 
        return data 


    def getSampleData(self, strategyInfo):
        #cmd = 'python dataManager.py sample -m get -v {0}'.format(strategyInfo['sample_version'])
        #print cmd
        #cmdStatus, cmdOutput = commands.getstatusoutput(cmd)
        #print 'getSampleData result:' , cmdOutput
        #if (cmdStatus != 0):
        #    raise Exception('getSampleData error')
        dataManager = DataManager()
        data = dataManager.get('sample', strategyInfo['sample_version'])
        print data 
        return data 

    def getActionData(self, strategyInfo):
        #cmd = 'python dataManager.py action -m get -v {0}'.format(strategyInfo['action_version'])
        #print cmd
        #cmdStatus, cmdOutput = commands.getstatusoutput(cmd)
        #print 'getActionData result:' , cmdOutput
        #if (cmdStatus != 0):
        #    raise Exception('getActionData error')
        dataManager = DataManager()
        data = dataManager.get('action', strategyInfo['action_version'])
        print data 
        return data 

    def schedule(self):
        jobInfo = self.getUnscheduledJob()
        if jobInfo:
            jobId = jobInfo['id']
            upRet = self.updateJobStatus(jobId, JOB_STATUS['SCHEDULED'])
            if upRet == 1:
                return jobInfo
        else:
            return {}

    ##添加新job
    #def addNewJob(self, strategyVersion):
    #    try:
    #        sqlExecutor = SqlExecutor.getInstance()
    #        curTime = int(time.time())
    #        sql = 'insert into jobpool(strategy_version, ctime, mtime) values({0}, {1}, {2})'.format(strategyVersion, curTime, curTime)
    #        #print sql
    #        ret = sqlExecutor.insert(sql)
    #        lastId = sqlExecutor.getLastRowId()
    #        return lastId
    #    except Exception as e:
    #        raise Exception('addNewJob error')

    ##查询job列表
    #def getJobList(self, offset=0, size=50):
    #    try:
    #        sqlExecutor = SqlExecutor.getInstance()
    #        sql = 'select * from jobpool limit {0}, {1}'.format(int(offset), int(size))
    #        ret = sqlExecutor.select(sql)
    #        return ret
    #    except Exception as e:
    #        raise Exception('getJobList error')

    def getUnscheduledJob(self):
        try:
            sqlExecutor = SqlExecutor.getInstance()
            sql = 'select * from jobpool where job_status={0} order by ctime asc limit 1'.format(JOB_STATUS['UNSCHEDULED'])
            ret = sqlExecutor.select(sql)
            if ret:
                return ret[0]
            else:
                return {}
        except Exception as e:
            return False

    def updateJobStatus(self, jobId, jobStatus):
        try:
            sqlExecutor = SqlExecutor.getInstance()
            sql = 'update jobpool set job_status={0} where id={1}'.format(int(jobStatus), int(jobId))
            ret = sqlExecutor.update(sql)
            return ret
        except Exception as e:
            print e
            return False


if __name__ == '__main__':
    try:
        jobWorker = JobWorker()
        jobWorker.run()
    except:
        sys.exit('Error encountered.')
