# -*- coding: utf-8 -*-

TMP_DATA_PATH = '/home/users/lihuipeng/work/fangchan/data-mining/pingjiaxitong/evaluation-sys/data/data-tmp/'
WAREHOUSE_DATA_PATH = '/home/users/lihuipeng/work/fangchan/data-mining/pingjiaxitong/evaluation-sys/data/data-warehouse/'

#数据类型
FEATURE_TYPE = 1    #特征数据
ACTION_TYPE = 2     #用户行为数据
SAMPLE_TYPE = 3     #样本数据
DATA_TYPE = {
        'feature' : FEATURE_TYPE,
        'action' : ACTION_TYPE, 
        'sample' : SAMPLE_TYPE,
}


JOB_STATUS = {
        'UNSCHEDULED'   :   10,
        'SCHEDULED'     :   20,
        'PREPARING'     :   30,
        'PREPARED'      :   40,
        'COMPUTING'     :   50,
        'DONE'          :   100,
}
