# -*- coding: utf-8 -*-
"""test data by lihuipeng"""
from argparse import ArgumentParser
import logging
import logging.config
import os
import sys
import time
import datetime
import commands
import json

reload(sys)
sys.setdefaultencoding('utf8')



if __name__ == '__main__':
    try:
        user = {
                "intentionpurchase":25,
                "strategyversion": "v1.0.1",
                "datatime":"20160314",
                "intentioncity":[
                    {
                    "city":"nanjing",
                    }
                ],
                "intentionbuilding":["b1", "b2"],
                "cuid":"11111111",
        }

        print json.dumps(user)
        user["cuid"] = "22222222"
        print json.dumps(user)
        user["cuid"] = "33333333"
        print json.dumps(user)
    except:
        sys.exit('Error encountered.')
