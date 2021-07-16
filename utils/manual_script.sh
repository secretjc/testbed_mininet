echo -e "111111\n111111\n" | sudo passwd secretjc
sudo scp testbed_mininet/other_files/sshd_config /etc/ssh/sshd_config
sudo service ssh restart
sudo scp testbed_mininet/other_files/sudoers /etc/sudoers

ssh-keygen -t rsa -b 4096 -C "chuanjiang93@gmail.com"
ssh-copy-id secretjc@ms0216.utah.cloudlab.us
ssh-copy-id secretjc@ms0226.utah.cloudlab.us
ssh-copy-id secretjc@ms0219.utah.cloudlab.us
ssh-copy-id secretjc@ms0209.utah.cloudlab.us
ssh-copy-id secretjc@ms0218.utah.cloudlab.us
ssh-copy-id secretjc@ms0238.utah.cloudlab.us
ssh-copy-id secretjc@ms0220.utah.cloudlab.us
ssh-copy-id secretjc@ms0233.utah.cloudlab.us
ssh-copy-id secretjc@ms0217.utah.cloudlab.us
