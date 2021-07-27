echo -e "111111\n111111\n" | sudo passwd secretjc
sudo scp testbed_mininet/other_files/sshd_config /etc/ssh/sshd_config
sudo service ssh restart
sudo scp testbed_mininet/other_files/sudoers /etc/sudoers

ssh-keygen -t rsa -b 4096 -C "chuanjiang93@gmail.com"
ssh-copy-id secretjc@ms0204.utah.cloudlab.us
ssh-copy-id secretjc@ms0232.utah.cloudlab.us
ssh-copy-id secretjc@ms0203.utah.cloudlab.us
ssh-copy-id secretjc@ms0238.utah.cloudlab.us
ssh-copy-id secretjc@ms0222.utah.cloudlab.us

ssh-copy-id secretjc@ms0241.utah.cloudlab.us
