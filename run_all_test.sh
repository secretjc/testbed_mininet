#!/usr/bin/env bash
server0=ms0939.utah.cloudlab.us
username=li3566

serverfile=./utils/server.txt



declare -a serverList
serverList=(`cat "$serverfile"`)



for server in ${serverList[*]}
do
    echo "$server"
    ssh ${username}@${server} "
    sudo mn -c"
done
