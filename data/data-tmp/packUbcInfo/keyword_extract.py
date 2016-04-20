#-*-coding:utf-8 -*-
#!/usr/bin/python


"""
 * @file keyword_extract.py
 * @author rongyuecheng(com@baidu.com)
 * @date 2016/03/10 19:41:07
 * @brief 
 *  
"""

import string
def loadKeywords(keywordFilePath):
    keywordDict=set()
    fileHandle=file(keywordFilePath,"r")
    keyword = fileHandle.readline().strip()
    while keyword:
	keywordDict.add(keyword)
	keyword = fileHandle.readline().strip()
    fileHandle.close()
    return keywordDict

def loadKeywordFiles(keywordFilePaths):
    keywordDict={}
    for kwKey in keywordFilePaths:
        kwfpath = keywordFilePaths[kwKey]
        kwSubDict = set()
        keywordDict[kwKey] = kwSubDict
        fileHandle=file(kwfpath,"r")
        keyword = fileHandle.readline().strip()
        while keyword:
            kwSubDict.add(keyword)
            keyword = fileHandle.readline().strip()
        fileHandle.close()
    return keywordDict
def loadKeywords(keywordFilePath):
    keywordDict=set()
    fileHandle=file(keywordFilePath,"r")
    keyword = fileHandle.readline().strip()
    while keyword:
	keywordDict.add(keyword)
	keyword = fileHandle.readline().strip()
    fileHandle.close() 
    return keywordDict

class keywordExtractor(object):
    
    keywordDict=set()
    # def __init__(self,filePath):
    #     self.keywordDict=loadKeywords(filePath)

    def __init__(self,filePaths):
        self.keywordDict=loadKeywordFiles(filePaths)
        # print filePaths
	
    def extractKeywordFromQuery(self,queryString):
        keywordList=[]
        queryLen=len(queryString)
        # print queryLen
        i=0
        while i<queryLen:
            for j in range(i+1,queryLen):
                subStr=queryString[i:j+1]
                for kwkey in self.keywordDict:
                    if subStr in self.keywordDict[kwkey]:
                        keywordList.append(subStr)
                        i=j
                        break
	    i=i+1

        if len(keywordList)<1:
            return ""
        
        keywordString=keywordList[0]
	for k in range(1,len(keywordList)):
            keywordString+="\\t"+keywordList[k]
        return keywordString

if __name__ == "__main__":
    kwFiles = {'common':'words/fang-keywords-all.txt','area_name':'words/area_name.txt','head_esate':'words/head_esate.txt','general_query':'words/general_query.txt'}
    extractor = keywordExtractor(kwFiles)
    testStr1="建宁在线房价"
    testStr2="长阳半岛房贷"
    #testStr3="公司的公积金怎么交的"
    # print testStr1
    extStr1=extractor.extractKeywordFromQuery(testStr1)
    print extStr1

    # extractor=keywordExtractor("fang-keywords-all.txt")
    # testStr1="万科房价"
    # testStr2="长阳半岛房贷"
    # testStr3="公司的公积金怎么交的"
