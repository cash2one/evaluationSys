#-*-coding:utf-8 -*-
#!/usr/bin/python


"""
 * @file keyword_extract.py
 * @author rongyuecheng(com@baidu.com)
 * @date 2016/03/10 19:41:07
 * @brief 
 *  
"""
import sys
import string
import json
import re

reload(sys)
sys.setdefaultencoding('utf-8')


class LoupanLabel(object):
    
    loupanDict=[]
    estateNames=[]
    # def __init__(self,filePath):
    #     self.keywordDict=loadKeywords(filePath)

    def __init__(self,loupan_path):
        fileHandle=file(loupan_path,"r")
        logitem = fileHandle.readline().strip()
        index = 0
        while logitem:
            # print logitem
            infos = logitem.split(' ')
            city = infos[0]
            district = infos[1]
            estate = infos[2]
            price = infos[3]
            location = infos[4]
            ldict = {}
            ldict['city']=city
            ldict['district']=district
            ldict['estate']=estate
            ldict['price']=price
            ldict['location']=location
            self.loupanDict.append(ldict)

            self.estateNames.append(estate)

            logitem = fileHandle.readline().strip()
        fileHandle.close() 
        # print filePaths
    def getLoupanDict(self):
        return self.loupanDict
    """
    楼盘名称查询明细信息，返回json格式。注意转码
    """
    def getEstateInfo(self,estate_name,city,district):
        for estate in self.loupanDict:
            if city!='' and estate['city']!=city:
                continue
            if district!='' and estate['district']!=district:
                continue
            if estate['estate']==estate_name:
                # estaters = {}
                # estaters['city'] = estate['city'].encode('utf-8')
                # estaters['district'] = estate['district'].encode('utf-8')
                # estaters['estate'] = estate['estate'].encode('utf-8')
                # estaters['price'] = estate['price'].encode('utf-8')
                # estaters['location'] = estate['location'].encode('utf-8')
                return estate

    """
    根据楼盘词表，分词
    """
    def extractMMKeywordFromQuery(self,queryString):
        keywordList=[]
        queryLen=len(queryString)
        maxLen = 30
        i=0
        while i<queryLen:
            matched=0
            clen = maxLen
            if (queryLen-i)<maxLen:
                clen = (queryLen-i)
            for j in range(0,clen):
                subStr=queryString[i:(i+clen-j)]
                if subStr in self.estateNames:
                    keywordList.append(subStr)
                    i=i+(clen-j)
                    matched=1
                    # print 'matched '+subStr
                    break
                if matched==1:
                    break
            if matched==0:
                i=i+1

        if len(keywordList)<1:
            return ""
        
        keywordString=keywordList[0]
        for k in range(1,len(keywordList)):
            keywordString+="\t"+keywordList[k]
        return keywordString

    """
    根据query 提取兴趣楼盘，包含了最大匹配分词
    """
    def findQueryTargetEstates(self,query):
        keywordString = self.extractMMKeywordFromQuery(query)
        kws = keywordString.split('\t')
        estateinfos = []
        for kw in kws:
            estate = self.getEstateInfo(kw,'','')
            estateinfos.append(estate)

        return estateinfos
	

if __name__ == "__main__":
    estatepath = "estate_all"
    loupanLabel = LoupanLabel(estatepath)
    estateDict = loupanLabel.getLoupanDict()
    #estate = loupanLabel.getEstateInfo('赤山路干休所','天津','')
    # features = loupanLabel.extractMMKeywordFromQuery('赤山路干休所怎么样')
    estate = loupanLabel.findQueryTargetEstates('恒基旭辉城搜房网苏州')
    print json.dumps(estate, ensure_ascii=False).encode("utf-8")

    # print estateDict[0]['city']



