echo -e "111111\n111111\n" | sudo passwd secretjc
sudo scp testbed_mininet/other_files/sshd_config /etc/ssh/sshd_config
sudo service ssh restart
sudo scp testbed_mininet/other_files/sudoers /etc/sudoers

ssh-keygen -t rsa -b 4096 -C "chuanjiang93@gmail.com"
ssh-copy-id secretjc@ms0333.utah.cloudlab.us
ssh-copy-id secretjc@ms0301.utah.cloudlab.us
ssh-copy-id secretjc@ms0325.utah.cloudlab.us
ssh-copy-id secretjc@ms0338.utah.cloudlab.us
ssh-copy-id secretjc@ms0310.utah.cloudlab.us
ssh-copy-id secretjc@ms0305.utah.cloudlab.us
ssh-copy-id secretjc@ms0338.utah.cloudlab.us
ssh-copy-id secretjc@ms0310.utah.cloudlab.us
ssh-copy-id secretjc@ms0305.utah.cloudlab.us
