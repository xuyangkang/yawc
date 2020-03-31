#!/bin/sh
while :
do
    `which python3` main.py
    retVal=$?
    if [ $retVal -ne 0 ]; then
        break
    fi
done