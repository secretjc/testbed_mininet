#!/usr/bin/env bash

serverfile=server.txt
declare -a serverList
serverList=(`cat "$serverfile"`)
server0=${serverList[0]}
username=li3566

printf "\n\nSetting up Mininet cluster......\n\n"
printf "\n\nCloning repo from Github and installing Minime, OpenVSwitch etc..\n\n"
for server in ${serverList[*]}
    do
    echo "$server"
    ssh ${username}@${server} "
    git clone https://github.com/secretjc/testbed_mininet.git
    cd ~/testbed_mininet
    # sh utils/config.sh" &
done

wait

printf "\n\nChanging passwords and ssh configurations for each node......\n\n"
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

printf "\n\nGenerating a pair of shared ssh-key and populating it into each node......\n\n"
echo ${server0}
./auto_send_reply.exp ${username} ${server0} "${serverList[*]}"

printf "\n\nDone with setting up Mininet cluster.\n\n"
echo "Reday to start the experiment."