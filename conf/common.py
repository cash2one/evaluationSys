# -*- coding: utf-8 -*-
from db import MYSQL

SRC_DATA_HOST = 'lihuipeng@cp01-rdqa04-dev121.cp01.baidu.com'
SRC_DATA_PATH = '/home/users/lihuipeng/work/fangchan/data-mining/pingjiaxitong/evaluation-sys/data/data-src/'

DEST_DATA_HOST = 'lihuipeng@cp01-rdqa04-dev121.cp01.baidu.com'
DEST_DATA_PATH = '/home/users/lihuipeng/work/fangchan/data-mining/pingjiaxitong/evaluation-sys/data/data-dest/'

#数据类型
FEATURE_TYPE = 1    #特征数据
ACTION_TYPE = 2     #用户行为数据
SAMPLE_TYPE = 3     #样本数据
DATA_TYPE = {
        'feature' : FEATURE_TYPE,
        'action' : ACTION_TYPE, 
        'sample' : SAMPLE_TYPE,
}


CFG = {
    'src_data_host' : SRC_DATA_HOST,
    'src_data_path' : SRC_DATA_PATH,
    'dest_data_host' : DEST_DATA_HOST,
    'dest_data_path' : DEST_DATA_PATH,
    'db' : MYSQL,
}

