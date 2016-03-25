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
from dataManager import DataManager

reload(sys)
sys.setdefaultencoding('utf8')


CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

class JobWorker(object):
   
    jobInfo = None
    jobDir = None
    strategySrc = None 
    strategyFeature = None 
    strategySample = None 
    strategyAction = None 

    def run(self):
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
        
            self.jobDir = self.makeJobDir(jobId)

            self.strategySrc = self.getStragetySrc(strategyInfo)
            #self.strategyFeature = self.getFeatureData(strategyInfo)
            self.strategySample = self.getSampleData(strategyInfo)
            self.strategyAction = self.getActionData(strategyInfo)


            #self.strategyMergedData = self.getStrategyMergedData()
        except Exception as e:
            print 'preExecute error', e
            raise e


    def execute(self, jobId):
        cmd = 'cd {0} && sh {1} < {2} > {3}'.format(self.jobDir, self.strategySrc, self.strategyAction, self.getJobResultFile(jobId))
        print cmd
        cmdStatus, cmdOutput = commands.getstatusoutput(cmd)
        print cmdStatus, cmdOutput
        if (cmdStatus != 0):
            raise Exception('execute failed')

    def afterExecute(self, jobId):
        try:
            accuracyRate = self.getAccuracyRate()
            precisionRate = self.getPrecisionRate()
            recallRate = self.getRecallRate()
            self.saveJobResult(accuracyRate, precisionRate, recallRate)
            upRet = self.updateJobStatus(jobId, JOB_STATUS['DONE'])
            if upRet == 1:
                print 'Well Done!'
        except Exception as e:
            print 'afterExecute error', e
            raise e

   
    def getPositiveSample(self, sampleFile):
        pass

    def getNegativeSample(self, sampleFile):
        pass

    def getPositiveResult(self, resultFile):
        pass

    def getNegativeResult(self, resultFile):
        pass

    def saveJobResult(accuracyRate, precisionRate, recallRate):
        print 'job result: accuracyRate: {0}, precisionRate: {1}, RecallRate: {2}'.format(accuracyRate, precisionRate, recallRate)
        pass

    def getAccuracyRate(self):
        return 0.1

    def getPrecisionRate(self):
        return 0.2

    def getRecallRate(self):
        return 0.3

    def makeJobDir(self, jobId):
        jobDir = TMP_DATA_PATH + str(jobId) + '/'
        if os.path.exists(jobDir):
            os.popen('rm -rf {0}'.format(jobDir))
        if not os.path.exists(jobDir):
            os.makedirs(jobDir)
        return jobDir

    def moveFromTmpToJobDir(self, srcData):
        tmpData = TMP_DATA_PATH + srcData
        cmd = 'mv {0} {1}'.format(tmpData, self.jobDir)
        print cmd
        cmdStatus, cmdOutput = commands.getstatusoutput(cmd)
        if (cmdStatus != 0):
            raise Exception('moveToJobDir failed')
        return self.jobDir + srcData

    def getJobResultFile(self, jobId):
        return self.jobDir + 'result.txt'

    def getStragetySrc(self, strategyInfo):
        cmd = 'cd {0} && cp -f testStrategy.sh {1}'.format(TMP_DATA_PATH, self.jobDir)
        print cmd
        os.popen('cd {0} && cp -f testStrategy.sh {1}'.format(TMP_DATA_PATH, self.jobDir))
        return self.jobDir + 'testStrategy.sh'
        pass

    def getFeatureData(self, strategyInfo):
        dataManager = DataManager()
        data = dataManager.get('feature', strategyInfo['feature_version'])
        data = self.moveFromTmpToJobDir(data)
        print data 
        return data 


    def getSampleData(self, strategyInfo):
        dataManager = DataManager()
        data = dataManager.get('sample', strategyInfo['sample_version'])
        data = self.moveFromTmpToJobDir(data)
        print data 
        return data 

    def getActionData(self, strategyInfo):
        dataManager = DataManager()
        data = dataManager.get('action', strategyInfo['action_version'])
        data = self.moveFromTmpToJobDir(data)
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
