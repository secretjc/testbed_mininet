git clone git://github.com/mininet/mininet
cd mininet
git checkout -b mininet-2.3.0d6 2.3.0d6
cd ..
mininet/util/install.sh -a

scp examples/cluster.py secretjc@ms0714.utah.cloudlab.us:/users/secretjc/mininet/examples/

sudo passwd secretjc

sudo vi /etc/ssh/sshd_config
sudo service ssh restart

sudo vi /etc/sudoers
#secretjc ALL=(ALL) NOPASSWD: ALL

ssh-keygen -t rsa -b 4096 -C "chuanjiang93@gmail.com"
ssh-copy-id secretjc@ms0738.utah.cloudlab.us
ssh-copy-id secretjc@ms0724.utah.cloudlab.us
ssh-copy-id secretjc@ms0721.utah.cloudlab.us
ssh-copy-id secretjc@ms0714.utah.cloudlab.us
ssh-copy-id secretjc@ms0712.utah.cloudlab.us
ssh-copy-id secretjc@ms0702.utah.cloudlab.us

sudo -E mn --topo tree,3,3 --cluster localhost,ms0244.utah.cloudlab.us,ms0230.utah.cloudlab.us
sudo mn -c

scp jiang486@ecegrid.ecn.purdue.edu:~/attdata/test_remote_switch_3.py ./

sh ovs-ofctl add-flow s0 table=0,ip,ip_dst=10.0.0.2,eth_type=0x800,actions=push_mpls:0x8847,set_field:1->mpls_label

sh ovs-ofctl add-flow s0 table=0,ip,ip_dst=10.0.0.3,eth_type=0x800,actions=group:0

# Yes! 
# From the linux shell prompt, use "sudo ovs-ofctl dump-flows s1". ovs-ofctl is your friend.
# From the Mininet CLI prompt, use "dpctl show" or "sh ovs-ofctl dump-flows s1".
# http://www.muzixing.com/pages/2015/02/22/fattree-topo-and-iperfmulti-function-in-mininet.html
# http://csie.nqu.edu.tw/smallko/sdn/iperf_mininet.htm


# script

# get root
sudo -s
cd /users/secretjc/

# Install Mininet
git clone git://github.com/mininet/mininet
cd mininet
git checkout -b mininet-2.3.0d6 2.3.0d6
cd ..
mininet/util/install.sh -a

# Download Tanner's ovs
git clone --recurse-submodules git://github.com/tanner-andrulis/stochastic-ovs.git
chmod -R 700 stochastic-ovs
cd stochastic-ovs

# Build ovs
git submodule init
git submodule update
cp ofproto-dpif-xlate.c ovs/ofproto/ofproto-dpif-xlate.c
cd ovs
./boot.sh
./configure
make

# Remove previous and install
apt-get remove openvswitch-common openvswitch-datapath-dkms openvswitch-controller openvswitch-pki openvswitch-switch
make install

# Replace previous version
config_file="/etc/depmod.d/openvswitch.conf"
for module in datapath/linux/*.ko; do
modname="$(basename ${module})"
echo "override ${modname%.ko} * extra" >> "$config_file"
echo "override ${modname%.ko} * weak-updates" >> "$config_file"
done
depmod -a

# Load kernel modules and show loaded version
/sbin/modprobe openvswitch
/sbin/lsmod | grep openvswitch

# Start daemon
export PATH=$PATH:/usr/local/share/openvswitch/scripts
ovs-ctl stop
ovs-ctl start
ovs-ctl status





sudo passwd secretjc

sudo vi /etc/ssh/sshd_config
sudo service ssh restart

ssh-keygen -t rsa -b 4096 -C "chuanjiang93@gmail.com"
ssh-copy-id secretjc@ms0327.utah.cloudlab.us
ssh-copy-id secretjc@ms0330.utah.cloudlab.us
ssh-copy-id secretjc@ms0344.utah.cloudlab.us

sudo vi /etc/sudoers
#secretjc ALL=(ALL) NOPASSWD: ALL

sudo apt update
sudo apt-get install git autoconf screen cmake build-essential sysstat python-matplotlib uuid-runtime python-pip

#mininet
git clone git://github.com/mininet/mininet
cd mininet
git checkout -b 2.2.2 2.2.2
cd .. && sudo mininet/util/install.sh -a

#metis
wget http://glaros.dtc.umn.edu/gkhome/fetch/sw/metis/metis-5.1.0.tar.gz
tar -xzf metis-5.1.0.tar.gz
rm metis-5.1.0.tar.gz
cd metis-5.1.0
make config
make
sudo make install
cd ..

sudo pip install Pyro4

cd ~ && git clone git://github.com/MaxiNet/MaxiNet.git
cd MaxiNet
git checkout v1.2
# change code 
vi MaxiNet/WorkerServer/server.py

sudo make install

sudo cp ~/MaxiNet/share/MaxiNet-cfg-sample ~/.MaxiNet.cfg


128.110.216.209
128.110.216.219
128.110.216.212
