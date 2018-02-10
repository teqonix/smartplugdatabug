#!/bin/bash

pythonscriptfile=testWemoClass.py
checkModifyFile=lastKnownActivity.log
numMinutes=$1

if [ -z "$numMinutes" ]
then
    echo "Please pass in a number of minutes allowed for the wemo app to be idle.  Exiting.."
    exit
fi

if [ $(($numMinutes)) -gt 0 ]
then
    echo "Is wemo app running? "
    ps_run_count=`ps -ef | grep $pythonscriptfile | grep -v grep | wc -l`

    echo $ps_run_count

    if [ $ps_run_count -gt 0 ]
    then
        echo "Wemo app is running - checking for activity in last X mins: " $numMinutes
        lastUpdatedInXMins=`find $checkModifyFile -mmin -$numMinutes | wc -l`
        if [ $((lastUpdatedInXMins)) -eq 0 ]
        then
            echo "Wemo Fetch App has hung!  Killing.."
            pidToKill=`pgrep -f $pythonscriptfile`
            kill $pidToKill
        fi
        if [ $((lastUpdatedInXMins)) -gt 0 ]
        then
            echo "Wemo app is responsive!  Exiting.."
            exit
        fi
    fi

    #If the app isn't running, start it in the background
    if [ $ps_run_count -eq 0 ]
    then
        python $pythonscriptfile > ./wemoCronJob.log 2>&1 &
        echo "Wemo app started!"
    fi

fi
