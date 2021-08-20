#!/usr/bin/env bash
server0=ms0311.utah.cloudlab.us
username=li3566

serverfile=./utils/server.txt



declare -a serverList
serverList=(`cat "$serverfile"`)


scenario_num=($(python ./utils/read_scenario.py --scenario_file ./_data/scenario_ibm.tab| tr -d '[],'))
echo $scenario_num

ssh ${username}@${server0} "
cd ~/testbed_mininet
mkdir iperf_results
"


for i in "${scenario_num[@]}"
# for (( i=54; i<=138; i++ ))
do
    ssh -t ${username}@${server0} "
    cd ~/testbed_mininet
    mkdir iperf_results/ibm_scenario_${i}
    sudo python main.py --main_config ./_config/main.yaml --topo_config ./_config/scenario_${i}.yaml
    "
    wait
    ssh ${username}@${server0} "
    cd ~/testbed_mininet
    mv *.txt iperf_results/ibm_scenario_${i}
    "
    for ((x=1; x<${#serverList[@]}; x++));
    do
        echo "${serverList[x]}"
        scp ${username}@${serverList[x]}:~/*.txt ${username}@${server0}:~/testbed_mininet/iperf_results/ibm_scenario_${i}
        ssh ${username}@${serverList[x]} "
        rm ~/*.txt"
    done
    scp -r ${username}@${server0}:~/testbed_mininet/iperf_results/ibm_scenario_${i} . &
    for server in ${serverList[*]}
    do
        echo "$server"
        ssh ${username}@${server} "
        sudo mn -c" &
    done
    
done