#!/usr/bin/env bash

server0=ms0626.utah.cloudlab.us
username=li3566

serverfile=server.txt

ssh ${username}@${server0} "
    geni-get manifest > manifest.txt"
scp ${username}@${server0}:~/manifest.txt ./
grep -i "hostname=" manifest.txt | sed -e 's/.*hostname="\(.*\)" p.*/\1/g' > $serverfile
rm manifest.txt

declare -a serverList
serverList=(`cat "$serverfile"`)

printf "**********************Adding to known_hosts......\n\n"
for ((x=1; x<${#serverList[@]}; x++));
do
    echo "${serverList[x]}"
    ./auto_addto_known.exp $username ${serverList[x]}
done

printf "**********************Setting up Mininet cluster......\n\n"
printf "**********************Cloning repo from Github and installing Minime, OpenVSwitch etc..\n\n"
for server in ${serverList[*]}
    do
    echo "$server"
    ssh ${username}@${server} "
    git clone https://github.com/secretjc/testbed_mininet.git
    cd ~/testbed_mininet
    sh utils/config.sh" &
done

wait

printf "**********************Changing passwords and ssh configurations for each node......\n\n"
for server in ${serverList[*]}
    do
    echo "$server"
    ssh -t ${username}@${server} "
    sudo passwd $username <<EOF
111111
111111
EOF
    sudo scp testbed_mininet/other_files/sshd_config /etc/ssh/sshd_config
    sudo service ssh restart
    sudo scp testbed_mininet/other_files/sudoers /etc/sudoers"
done

printf "**********************Generating a pair of shared ssh-key and populating it into each node......\n\n"
echo ${server0}
./auto_send_reply.exp ${username} ${server0} "${serverList[*]}"

printf "**********************Done with setting up Mininet cluster.\n\n"
printf "**********************Generating _config/main.yaml.\n\n"
python add_hname_to_config.py --main_config ../_config/main.yaml --server_file ./server.txt
printf "**********************Generating _config/scenario_{#}.yaml.\n\n"
python create_scenario.py ----scenario_file ../_data/scenario_example.tab --scenario_template ../_config/scenario_template.yaml
printf "**********************Copying _config _data to node 0.\n\n"
scp -r ../_config ${username}@${host_0}:~/testbed_mininet/
scp -r ../_data ${username}@${host_0}:~/testbed_mininet/
echo "**********************Ready to start the experiment."
echo 'ssh to node 0 and run testbed_mininet/run_all.sh'
