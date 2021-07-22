echo -e "111111\n111111\n" | sudo passwd secretjc
sudo scp testbed_mininet/other_files/sshd_config /etc/ssh/sshd_config
sudo service ssh restart
sudo scp testbed_mininet/other_files/sudoers /etc/sudoers

ssh-keygen -t rsa -b 4096 -C "chuanjiang93@gmail.com"
ssh-copy-id secretjc@ms0234.utah.cloudlab.us
ssh-copy-id secretjc@ms0216.utah.cloudlab.us
ssh-copy-id secretjc@ms0226.utah.cloudlab.us
ssh-copy-id secretjc@ms0235.utah.cloudlab.us
ssh-copy-id secretjc@ms0202.utah.cloudlab.us
ssh-copy-id secretjc@ms0242.utah.cloudlab.us
