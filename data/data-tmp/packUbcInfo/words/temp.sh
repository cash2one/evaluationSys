#!/bin/bash

line ='北京市'
if [ ^'市' $line ]
then
    echo $line

#for line in `cat ./cp_head.txt`;
#do
#    if [ ${#line} -gt 2 ]
#    then
#        echo $line
##    then
##        echo $line
##    if expr index "$string" $line <3
##        then
##            echo $line
##    fi
###    if length($line)==1
###    then
###        echo $line
#    fi
#done
