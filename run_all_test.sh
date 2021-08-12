#!/usr/bin/env bash
server0=ms0322.utah.cloudlab.us
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


# mininet test command
ovs-vsctl set port s1-eth2 qos=@newqos -- \
  --id=@newqos create qos type=linux-htb \
      other-config:max-rate=1000000 \
      queues:1=@hpriority \
      queues:2=@lpriority -- \
  --id=@hpriority create queue other-config:max-rate=200000 -- \
  --id=@lpriority create queue other-config:max-rate=100000


ovs-ofctl add-flow s1 in_port=1,actions=set_queue:1,normal

ovs-vsctl set port s1-eth2 qos=@newqos -- \
  --id=@newqos create qos type=linux-htb \
      queues:1=@hpriority \
      queues:2=@lpriority -- \
  --id=@hpriority create queue other-config:priority=10 -- \
  --id=@lpriority create queue other-config:priority=20

ovs-vsctl list queue

ovs-vsctl -- --all destroy QoS -- --all destroy Queue