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
from dao.mongoexecutor import MongoExecutor
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

    positiveSampleCount = 0 
    negativeSampleCount = 0 
    posiviteResultCount = 0 
    negativeResultCount = 0 
    truePosiviteResultCount = 0 
    trueNegativeResultCount = 0 

    def run(self):
        try:
            #1. 调度一个job
            self.jobInfo = self.schedule()
            if self.jobInfo:
                print '********* start schedule job:', self.jobInfo['id'] 
            else:
                print '*********** no job can be dispatched'
                return

            self.preExecute(self.jobInfo['id'], self.jobInfo['strategy_version'])
            self.execute(self.jobInfo['id'])
            self.afterExecute(self.jobInfo['id'])
        except Exception as e:
            print e
            self.updateJobStatus(jobId, JOB_STATUS['UNSCHEDULED'])
        else:
            pass
        finally:
            pass

    def preExecute(self, jobId, strategyVersion):
        try:
            print '********** prepare for job'
            strategyManager = StrategyManager()
            strategyInfo = strategyManager.getVersionInfo(strategyVersion)
            if not strategyInfo:
                print '********** strategyVersion invalid:', strategyVersion
                return
       
            self.jobDir = self.makeJobDir(jobId)

            self.strategySrc = self.getStrategySrc(strategyInfo)
            self.strategyAction = self.getActionData(strategyInfo)
        except Exception as e:
            print 'preExecute error', e
            raise e


    def execute(self, jobId):
        print '********* job executing'
        cmd = 'cd {0} && python {1} {2} > {3}'.format(self.jobDir, self.strategySrc, self.strategyAction, self.getJobResultFile(jobId))
        print cmd
        cmdStatus, cmdOutput = commands.getstatusoutput(cmd)
        print cmdStatus, cmdOutput
        if (cmdStatus != 0):
            raise Exception('execute failed')
        print '********* job executed'

    def afterExecute(self, jobId):
        try:
            self.saveResultData(jobId)
        except Exception as e:
            print 'afterExecute error', e
            raise e

    def saveResultData(self, jobId):
        resultFile = self.getJobResultFile(jobId)
        mongoExecutor = MongoExecutor.getInstance()
        #print mongoExecutor.test()
        f = open(resultFile, 'r')
        line = f.readline()
        while line:
            ret = mongoExecutor.insert(line)
            if not ret:
                print 'saveResultData error'
            line = f.readline()
        f.close()
  
    #得到正样本
    def getPositiveSample(self, jobId):
        sampleFile = self.strategySample
        pSampleFile = self.getJobPositiveSampleFile(jobId)
        cmd = "awk '{if($2 == 1){print $1}}'"
        cmd = '{0} {1} > {2}'.format(cmd, sampleFile, pSampleFile)
        print cmd
        os.popen(cmd)

    #得到负样本
    def getNegativeSample(self, jobId):
        sampleFile = self.strategySample
        nSampleFile = self.getJobNegativeSampleFile(jobId)
        cmd = "awk '{if($2 == 0){print $1}}'"
        cmd = '{0} {1} > {2}'.format(cmd, sampleFile, nSampleFile)
        print cmd
        os.popen(cmd)

    #得到挖掘出的正结果(有购房意愿)
    def getPositiveResult(self, jobId):
        resultFile = self.getJobResultFile(jobId)
        pResultFile = self.getJobPositiveResultFile(jobId)
        cmd = "awk '{if($2 == 1){print $1}}'"
        cmd = '{0} {1} > {2}'.format(cmd, resultFile, pResultFile)
        print cmd
        os.popen(cmd)

    #得到挖掘出的负结果(没有买房意愿)
    def getNegativeResult(self, jobId):
        resultFile = self.getJobResultFile(jobId)
        nResultFile = self.getJobNegativeResultFile(jobId)
        cmd = "awk '{if($2 == 0){print $1}}'"
        cmd = '{0} {1} > {2}'.format(cmd, resultFile, nResultFile)
        print cmd
        os.popen(cmd)

    #得到挖掘出的正结果(有购房意愿)数量
    def getPositiveResultCount(self, jobId):
        pResultFile = self.getJobPositiveResultFile(jobId)
        cmd = "awk 'END{print NR}'"
        cmd = '{0} {1}'.format(cmd, pResultFile)
        cmdStatus, cmdOutput = commands.getstatusoutput(cmd)
        if (cmdStatus != 0):
            raise Exception('getPositiveResultCount failed')
        return cmdOutput 

    #得到挖掘出的负结果(没有买房意愿)数量
    def getNegativeResultCount(self, jobId):
        nResultFile = self.getJobNegativeResultFile(jobId)
        cmd = "awk 'END{print NR}'"
        cmd = '{0} {1}'.format(cmd, nResultFile)
        cmdStatus, cmdOutput = commands.getstatusoutput(cmd)
        if (cmdStatus != 0):
            raise Exception('getNegativeResultCount failed')
        return cmdOutput 

    #得到正样本数量
    def getPositiveSampleCount(self, jobId):
        pSampleFile = self.getJobPositiveSampleFile(jobId)
        cmd = "awk 'END{print NR}'"
        cmd = '{0} {1}'.format(cmd, pSampleFile)
        cmdStatus, cmdOutput = commands.getstatusoutput(cmd)
        if (cmdStatus != 0):
            raise Exception('getPositiveSampleCount failed')
        return cmdOutput 

    #得到负样本数量
    def getNegativeSampleCount(self, jobId):
        nSampleFile = self.getJobNegativeSampleFile(jobId)
        cmd = "awk 'END{print NR}'"
        cmd = '{0} {1}'.format(cmd, nSampleFile)
        cmdStatus, cmdOutput = commands.getstatusoutput(cmd)
        if (cmdStatus != 0):
            raise Exception('getNegativeSampleCount failed')
        return cmdOutput 

    #正确的识别为购房用户的cuid,即混淆矩阵中的TP
    def getTruePositiveResult(self, jobId):
        pSampleFile = self.getJobPositiveSampleFile(jobId)
        pResultFile = self.getJobPositiveResultFile(jobId)
        tpResultFile = self.getJobTruePositiveResultFile(jobId)
        cmd = "sort {0} {1} | uniq -d > {2}".format(pSampleFile, pResultFile, tpResultFile)
        print cmd
        os.popen(cmd)

    #正确的识别为非购房用户的cuid,即混淆矩阵中的TN
    def getTrueNegativeResult(self, jobId):
        nSampleFile = self.getJobNegativeSampleFile(jobId)
        nResultFile = self.getJobNegativeResultFile(jobId)
        tnResultFile = self.getJobTrueNegativeResultFile(jobId)
        cmd = "sort {0} {1} | uniq -d > {2}".format(nSampleFile, nResultFile, tnResultFile)
        print cmd
        os.popen(cmd)

    #得到正样本数量
    def getTruePositiveResultCount(self, jobId):
        tpResultFile = self.getJobTruePositiveResultFile(jobId)
        cmd = "awk 'END{print NR}'"
        cmd = '{0} {1}'.format(cmd, tpResultFile)
        cmdStatus, cmdOutput = commands.getstatusoutput(cmd)
        if (cmdStatus != 0):
            raise Exception('getTruePositiveResultCount failed')
        return cmdOutput 

    #得到负样本数量
    def getTrueNegativeResultCount(self, jobId):
        tnResultFile = self.getJobTrueNegativeResultFile(jobId)
        cmd = "awk 'END{print NR}'"
        cmd = '{0} {1}'.format(cmd, tnResultFile)
        cmdStatus, cmdOutput = commands.getstatusoutput(cmd)
        if (cmdStatus != 0):
            raise Exception('getTrueNegativeResultCount failed')
        return cmdOutput 


    def doCommonCompute(self, jobId):
        self.getPositiveSample(jobId)
        self.getNegativeSample(jobId)
        self.getPositiveResult(jobId)
        self.getNegativeResult(jobId)
        self.getTruePositiveResult(jobId)
        self.getTrueNegativeResult(jobId)

        self.positiveSampleCount = int(self.getPositiveSampleCount(jobId))
        self.negativeSampleCount = int(self.getNegativeSampleCount(jobId))
        self.posiviteResultCount = int(self.getPositiveResultCount(jobId))
        self.negativeResultCount = int(self.getNegativeResultCount(jobId))
        self.truePosiviteResultCount = int(self.getTruePositiveResultCount(jobId))
        self.trueNegativeResultCount = int(self.getTrueNegativeResultCount(jobId))
        print '*'*100
        print '*'*100
        print '正样本数量positiveSampleCount={0}'.format(self.positiveSampleCount)
        print '负样本数量negativeSampleCount={0}'.format(self.negativeSampleCount) 
        print '挖掘出的意向用户数量posiviteResultCount={0}'.format(self.posiviteResultCount) 
        print '挖掘出的非意向用户数量negativeResultCount={0}'.format(self.negativeResultCount) 
        print '正确挖掘出的意向用户数量truePosiviteResultCount={0}'.format(self.truePosiviteResultCount) 
        print '正确挖掘出的非意向用户数量trueNegativeResultCount={0}'.format(self.trueNegativeResultCount) 
        print '*'*100
        print '*'*100

    def getAccuracyRate(self, jobId):
        accuracyRate = float(self.truePosiviteResultCount + self.trueNegativeResultCount) / float(self.positiveSampleCount + self.negativeSampleCount)
        print '准确率=', accuracyRate
        return accuracyRate 

    def getPrecisionRate(self, jobId):
        precisionRate = float(self.truePosiviteResultCount) / float(self.posiviteResultCount)
        print '精度=', precisionRate 
        return precisionRate 

    def getRecallRate(self, jobId):
        recallRate = float(self.truePosiviteResultCount) / float(self.positiveSampleCount)
        print '召回率=', recallRate
        return recallRate 

    def makeJobDir(self, jobId):
        print '********* create job dir'
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

    def getJobPositiveResultFile(self, jobId):
        return self.jobDir + 'pResult.txt'
    
    def getJobNegativeResultFile(self, jobId):
        return self.jobDir + 'nResult.txt'
    
    def getJobPositiveSampleFile(self, jobId):
        return self.jobDir + 'pSample.txt'

    def getJobNegativeSampleFile(self, jobId):
        return self.jobDir + 'nSample.txt'
    
    def getJobTrueNegativeResultFile(self, jobId):
        return self.jobDir + 'tnResult.txt'
    
    def getJobTruePositiveResultFile(self, jobId):
        return self.jobDir + 'tpResult.txt'

    def getStrategySrc(self, strategyInfo):
        print '********* get src file'
        cmd = 'cd {0} && svn co https://svn.baidu.com/inf/yun/trunk/lightapp/fang/fangdm/script/strategy -r {1}'.format(self.jobDir, strategyInfo['svn_version'])
        print cmd
        os.popen(cmd)
        return self.jobDir + 'strategy/fangstrategy.py'

    def getFeatureData(self, strategyInfo):
        print '********* get feature file'
        dataManager = DataManager()
        data = dataManager.get('feature', strategyInfo['feature_version'])
        data = self.moveFromTmpToJobDir(data)
        print data 
        return data 


    def getSampleData(self, strategyInfo):
        print '********* get sample file'
        dataManager = DataManager()
        data = dataManager.get('sample', strategyInfo['sample_version'])
        data = self.moveFromTmpToJobDir(data)
        print data 
        return data 

    def getActionData(self, strategyInfo):
        print '********* get action file'
        cmd = 'cd {0} && sh run.sh'.format(TMP_DATA_PATH + '/packUbcInfo')
        print cmd
        os.popen(cmd)
        data = self.moveFromTmpToJobDir('/packUbcInfo/action.data')
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

    def saveJobResult(self, jobId, accuracyRate, precisionRate, recallRate):
        print 'job result: 准确率: {0}, 精度: {1}, 召回率: {2}'.format(accuracyRate, precisionRate, recallRate)
        try:
            sqlExecutor = SqlExecutor.getInstance()
            sql = 'update jobpool set accuracy_rate={0}, precision_rate={1}, recall_rate={2} where id={3}'.format(int(accuracyRate * 10000) / 100.0, int(precisionRate * 10000) / 100.0, int(recallRate * 10000) / 100.0, int(jobId))
            ret = sqlExecutor.update(sql)
            return ret
        except Exception as e:
            print e
            return False

if __name__ == '__main__':
    try:
        jobWorker = JobWorker()
        #jobWorker.saveResultData(1)
        jobWorker.run()
    except:
        sys.exit('Error encountered.')
