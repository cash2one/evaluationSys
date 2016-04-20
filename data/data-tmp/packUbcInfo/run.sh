#!/bin/bash
START_DATE=`date -d "-3 day" "+%Y%m%d"`
END_DATE=`date -d "-2 day" "+%Y%m%d"`
echo $START_DATE
echo $END_DATE
EXPORT_DATA="output_data.$END_DATE"
#python export_data.py $START_DATE $END_DATE >$EXPORT_DATA
split -l 10000 $EXPORT_DATA  "pre_split_"
count=0
concurrentNumber=5
for file in `ls pre_split*`
do
    echo $count
    if [ $count -lt $concurrentNumber ]
    then
        cat $file | python on_filter_feature.py >"pure"$file  &
        echo "$file processing.... " 
        let count+=1
    elif [ $count -eq $concurrentNumber ]
    then
         wait
         echo "continue"
         count=0
    fi
done
wait
find . -name "pure*" | xargs cat  >>action.data
rm pre_split*
#rm $EXPORT_DATA
rm pure*
