#!/usr/bin/python 
#-*-coding:utf-8 -*-

import os
import sys
import json
import re
import datetime
from keyword_extract import keywordExtractor
from loupanLabel import LoupanLabel
reload(sys)
sys.setdefaultencoding('utf-8')

city_estate_dict={}
district_estate_dict={}
for line in open('estate_all'):
    line = line.strip()
    arr=line.split(" ")
    estate_dict={}
    estate_dict["city"]=arr[0]
    estate_dict["district"]=arr[1]
    estate_dict["estate"]=arr[2]
    estate_dict["price"]=arr[3]
    estate_dict["location"]=arr[4]
    if city_estate_dict.has_key(arr[0]):
       city_estate_dict[arr[0]].append(estate_dict)
    else:
       list_dict=[]
       list_dict.append(estate_dict)
       city_estate_dict[arr[0]]=list_dict
    if district_estate_dict.has_key(arr[1]):
       district_estate_dict[arr[1]].append(estate_dict)
    else:
       d_list_dict=[]
       d_list_dict.append(estate_dict)
       district_estate_dict[arr[1]]=d_list_dict
    

def get_estate_city_from_title(title):
    for city in  city_estate_dict.keys():
        if city in title:
           for city_estate in  city_estate_dict[city]:
               if city_estate["estate"] in title:
                  return city_estate
    for district in district_estate_dict.keys():
        if district in title:
            for district_estate in district_estate_dict[district]:
                if district_estate["estate"] in title:
                   return district_estate
              
    
stat_dict={}
default_str={"pv":0,"uv":0,"click":0,"xf_click":0,"esf_click":0,"other_click":0}
#city_dict={u"北京" :"beijing",u"大连":"dalian",u"海南":"hainan",u"杭州":"hangzhou",u"济南":"jinan",u"南京":"nanjing",u"青岛":"qingdao",u"上海":"shanghai",u"沈阳":"shenyang",u"苏州":"suzhou",u"郑州":"zhengzhou"}
#estate_dict={}
#for city,citycode in city_dict.items():
#   fang_dict={}
#   for str_line in open("loupan/"+citycode+".txt"):
#     str_line=str_line.strip()
#     str_line=str_line.encode("utf-8")
#     arr=str_line.split('\t')
#     fang_dict[arr[0]]=1
#   estate_dict[city]=fang_dict

for str_line in open('feature.txt'):
    str_line=str_line.encode("utf-8")
    str_line=str_line.strip()
    fea_arr=str_line.split('\t')
    if len(fea_arr)==2:
       feakey=re.sub('\\t',"\t ",fea_arr[0])
       stat_dict[fea_arr[0]]=json.loads(fea_arr[1])

kwFiles = {'common':'words/fang-keywords-all.txt','area_name':'words/area_name.txt','head_esate':'words/head_esate.txt','general_query':'words/general_query.txt'}
keyExtr=keywordExtractor(kwFiles) 

#label_tool=LoupanLabel('estate_all')

for line in sys.stdin:
       line=line.strip()
       _json=json.loads(line)
       if  _json.has_key("wisequery:querystring")!=True:
          continue
       query_json=_json["wisequery:querystring"]
       new_filter_querylist_dict={}
       query_dict={}
       for item in query_json:
           querystring=item["querystring"]
           clicknumber=len(item["click"])
           if clicknumber>0:
              for title_item in item["click"]:
                  if title_item.has_key("title"):
                     if (u"租" not in title_item["title"]):
                         _datetime=item["datetime"]
                         stamp=datetime.datetime.strptime(_datetime,"%Y%m%d")
                         #start_time=datetime.datetime.strptime("20160301","%Y%m%d")
                         #end_time=datetime.datetime.strptime("20160418","%Y%m%d")
                         #if stamp <start_time or stamp >end_time:
                         #   continue
                         #for city ,fang in estate_dict.items():
                         #   if (city in title_item["title"]):
                         #      for estate_name in fang.keys():
                         #estatelist=label_tool.findQueryTargetEstates(title_item["title"].encode('utf-8'))
                         estate_dict=get_estate_city_from_title(title_item["title"].encode('utf-8'))
                         if estate_dict!=None:
                                 #estate_dict=estatelist[0]
                                 estate_name=estate_dict["estate"]
                                 #if estate_name in title_item["title"] :
                                 if new_filter_querylist_dict.has_key(estate_name)!=True:
                                        interest_estate={}
                                        interest_estate["city"]=estate_dict["city"]
                                        interest_estate["estate"]=estate_dict["estate"]
                                        interest_estate["price"]=estate_dict["price"]
                                        interest_estate["district"]=estate_dict["district"]
                                        interest_estate["location"]=estate_dict["location"]
                                        interest_estate["estate_click"]=1
                                        item["target"]=estate_name
                                        new_filter_querylist_dict[estate_name]=interest_estate
                                 else:
                                        interest_estate=new_filter_querylist_dict[estate_name]
                                        interest_estate["estate_click"]=interest_estate["estate_click"]+1
                                        new_filter_querylist_dict[estate_name]=interest_estate
                         info={} 
                         info["clicknumber"]=clicknumber
                         info["datetime"]=_datetime
                         key_word = keyExtr.extractKeywordFromQuery(querystring.encode("utf-8"))
                         if key_word!="" and stat_dict.has_key(key_word):
                            info["statistics"]=stat_dict[key_word]
                         else:
                            info["statistics"]=[] 
                         if query_dict.has_key(querystring):
                            query_dict[querystring].append(info)
                         else:
                            arr=[]
                            arr.append(info)
                         query_dict[querystring]=arr
       del _json["wisequery:querystring"]
       if len(new_filter_querylist_dict)>0:
          query_arr=[]
          for k,v in query_dict.items():
              dict_q={}
              dict_q["querystring"]=k
              dict_q["personinfo"]=v
              k_word = keyExtr.extractKeywordFromQuery(k.encode("utf-8"))
              k_word=re.sub("\t"," ",k_word)
              dict_q["feature_word"]=k_word
              query_arr.append(dict_q)
          
          _json["interest_target"]=new_filter_querylist_dict.values()
          _json["wisequery"]=query_arr
          print json.dumps(_json, ensure_ascii=False).encode("utf-8")
