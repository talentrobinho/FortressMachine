#!/bin/bash

pidfile=$(awk -F ' = ' '$1~/pid_file/{print $2}' ../bsshd.cfg | awk -F '"' '{print $2}')

function start()
{
    ./main.py
}

function stop()
{
    if [ ! -s $pidfile ]
    then
        echo "$pidfile is not exist"
    fi
    kill `cat $pidfile`
    rm -f $pidfile
}

function restart()
{
    stop
    start
}

if [ $# -ne 1 ]
then
    exit 1
fi

op=$(echo "$1" | tr [A-Z] [a-z])
if [ "$op" == "start" ]
then
    start
fi
if [ "$op" == "stop" ]
then
    stop
fi
if [ "$op" == "restart" ]
then
    restart
fi
