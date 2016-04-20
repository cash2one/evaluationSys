#!/usr/bin/python 
#-*-coding:utf-8 -*-

"""
File: preloadmodule.py 
import path
"""

import os
import sys

PROG_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.append('%s/pythonlib2' % (PROG_PATH))
