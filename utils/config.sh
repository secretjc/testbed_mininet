#git clone git@github.com:secretjc/testbed_mininet.git
echo "git clone git@github.com:secretjc/testbed_mininet.git is done"
echo "basic config..."
#sudo passwd secretjc
echo -e "000000\n000000" | passwd secretjc
sudo scp testbed_mininet/other_files/sshd_config /etc/ssh/sshd_config
sudo service ssh restart
sudo scp testbed_mininet/other_files/sudoers /etc/sudoers

echo "cloning mininet..."
git clone git://github.com/mininet/mininet
cd mininet
git checkout -b mininet-2.3.0d6 2.3.0d6
rm ./examples/cluster.py
cd ..
scp testbed_mininet/other_files/cluster.py mininet/examples/
echo "installing mininet..."
mininet/util/install.sh -a

echo "cloning Tanner's ovs..."
cd ~
git clone --recurse-submodules git://github.com/tanner-andrulis/stochastic-ovs.git
sudo chmod -R 777 stochastic-ovs
cd stochastic-ovs
echo "installing Tanner's ovs..."
sudo ./quick-install

echo "installing yaml..."
cd ~/
sudo apt-get install -y python-yaml

ssh-keygen -t rsa -b 4096 -C "chuanjiang93@gmail.com"
cd ~/
echo "testbed config Done."

