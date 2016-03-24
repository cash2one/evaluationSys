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

reload(sys)
sys.setdefaultencoding('utf8')


CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))

class StrategyManager(object):
    
    def run(self):
        argp = ArgumentParser()
        argp.add_argument('-m', '-method', dest='method', choices=['add', 'list'])
        argp.add_argument('-vn', '-name', '-version_name', dest='version_name')
        argp.add_argument('-vd', '-desc', '-version_desc', dest='version_desc')
        argp.add_argument('-gb', '-branch', '-git_branch', dest='git_branch')
        argp.add_argument('-gi', '-git_id', '-git_commit_id', dest='git_commit_id')
        argp.add_argument('-fv', '-feature', '-feature_verison', dest='feature_verison')
        argp.add_argument('-sv', '-sample', '-sample_verison', dest='sample_verison')
        argp.add_argument('-av', '-action', '-action_verison', dest='action_verison')
    
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
                versionName = args.version_name if hasattr(args, 'version_name') else ''
                versionDesc = args.version_desc if hasattr(args, 'version_desc') else ''
                gitBranch = args.git_branch if hasattr(args, 'git_branch') else 'master'
                gitCommitId = args.git_commit_id if hasattr(args, 'git_commit_id') else ''
                featureVersion = args.feature_verison if hasattr(args, 'feature_verison') else 0 
                sampleVersion = args.sample_verison if hasattr(args, 'sample_verison') else 0 
                actionVersion = args.action_verison if hasattr(args, 'action_verison') else 0 
                
                self.add(versionName, versionDesc, gitBranch, gitCommitId, featureVersion, sampleVersion, actionVersion)
            elif args.method == 'list':
                self.list()
        except Exception as e:
            print e

    #添加新版本
    def add(self, versionName, versionDesc, gitBranch, gitCommitId, featureVersion, sampleVersion, actionVersion):
        versionCode = datetime.datetime.now().strftime('%Y%m%d%H%M')
        try:
            #add version info
            self.addNewVersion(versionCode, versionName, versionDesc, gitBranch, gitCommitId, featureVersion, sampleVersion, actionVersion)
            print 'add new version success! version code =', versionCode
        except Exception as e:
            print e

    #查看版本列表
    def list(self, pn=0, ps=50):
        try:
            offset = pn * ps
            pageSize = ps
            ret = self.getVersionList(offset, pageSize)
            print '*' * 200
            print '{0:15s}{1:30s}{2:15s}{3:30s}{4:20s}{5:20s}{6:20s}{7:15s}'.format('version_code', 'version_name', 'git_branch', 'git_commit_id', 'feature_version', 'sample_version', 'action_version', 'create_time')
            print '*' * 200
            for versionRecord in ret:
                strTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(versionRecord['ctime']))
                print '{0:15s}{1:30s}{2:15s}{3:30s}{4:20s}{5:20s}{6:20s}{7:15s}'.format(str(versionRecord['version_code']), versionRecord['version_name'], versionRecord['git_branch'], versionRecord['git_commit_id'], str(versionRecord['feature_version']), str(versionRecord['sample_version']), str(versionRecord['action_version']), strTime)
            print '*' * 200
        except Exception as e:
            raise Exception('list error')

    #添加新数据版本
    def addNewVersion(self, versionCode, versionName, versionDesc, gitBranch, gitCommitId, featureVersion, sampleVersion, actionVersion):
        try:
            sqlExecutor = SqlExecutor.getInstance()
            sql = 'insert into strategy_version(version_code, version_name, version_desc, git_branch, git_commit_id, feature_version, sample_version, action_version, ctime) values({version_code},\'{version_name}\',\'{version_desc}\', \'{git_branch}\', \'{git_commit_id}\', {feature_version}, {sample_version}, {action_version}, {ctime})'.format(version_code=versionCode, version_name=versionName, version_desc=versionDesc, git_branch=gitBranch, git_commit_id=gitCommitId, feature_version=featureVersion, sample_version=sampleVersion, action_version=actionVersion, ctime=int(time.time()))
            print sql
            ret = sqlExecutor.insert(sql)
        except Exception as e:
            raise Exception('addNewVersion error')

    #根据数据类型得到版本列表
    def getVersionList(self, offset, size):
        try:
            sqlExecutor = SqlExecutor.getInstance()
            sql = 'select * from strategy_version order by version_code desc limit {offset},{size}'.format(offset=offset, size=size)
            ret = sqlExecutor.select(sql)
            return ret
        except Exception as e:
            raise Exception('getVersionList error')

    def getVersionInfo(self, versionCode):
        try:
            sqlExecutor = SqlExecutor.getInstance()
            sql = 'select * from strategy_version where version_code={0}'.format(versionCode)
            ret = sqlExecutor.select(sql)
            if len(ret) > 0:
                return ret[0]
            else:
                return {} 
        except Exception as e:
            raise Exception('getVersionInfo error')



if __name__ == '__main__':
    try:
        strategyManager = StrategyManager()
        strategyManager.run()
    except:
        sys.exit('Error encountered.')
