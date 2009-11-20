#!/bin/bash
DIR=`date +%F`

if [-d $DIR ]; then
    rm -rf $DIR
else
    mkdir $DIR
fi

cd $DIR
VAL=1
#echo $PWD
for i in {1..3}
do
echo "iter: $i"
    ../ServerSide/server_manager.py $i &
#exec 2>/dev/null
#exec 1>/dev/null
done
