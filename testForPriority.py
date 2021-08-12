import sys
import math
from collections import defaultdict
#import copy
import time
import logging
from mininet.examples.cluster import ( MininetCluster, SwitchBinPlacer,
                                       RemoteLink, RemoteOVSSwitch )

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

import mininet.util


import mininet.node
import mininet.link
from mininet.net import Mininet
from mininet.topo import Topo
from multiprocessing import Process

"""
h1 --- s1 --- s2 --- h2
        |       |
        |       |
        h3      h4

"""
class MyTopo(Topo):
    "Simple topology example."

    def build( self ):
        "Create custom topo."

        # Add hosts and switches
        leftHost = self.addHost('h1')
        rightHost = self.addHost('h2')
        ldownHost = self.addHost('h3')
        rdownHost = self.addHost('h4')
        leftSwitch = self.addSwitch('s1')
        rightSwitch = self.addSwitch('s2')
        # print(leftHost)
        # print(type(leftHost))
        # Add links
        self.addLink( leftHost, leftSwitch,  )
        self.addLink( rightSwitch, rightHost )
        self.addLink( leftSwitch, ldownHost  )
        self.addLink( rightSwitch, rdownHost )
        self.addLink( leftSwitch, rightSwitch, bw = 1)
    
    def get_switches(self):
        return self.switches()

class RulesHandler(object):
    def __init__(self, topo, net):
        self.topo = topo
        self.ofctl_rules = defaultdict(list)
        self.vsctl_rules = defaultdict(list)
        self.generate_rules(net)
    def rules_for_pqueue(self, switch_name, switch_intf, switch_port):
        cmd = "set port"
        parameters = "{} qos=@newqos -- \
                    --id=@newqos create qos type=linux-htb \
                        max-rate=1000000000 \
                        queues:{}1=@hpriority \
                        queues:{}2=@lpriority -- \
                    --id=@hpriority create queue other-config:priority=10,max-rate=1000000000 -- \
                    --id=@lpriority create queue other-config:priority=20,max-rate=1000000000".format(switch_intf, str(switch_port), str(switch_port))
        self.vsctl_rules[switch_name].append((cmd, parameters))
        cmd = "add-flow"
        parameters = "in_port=1,actions=set_queue:{}1".format(str(switch_port))
        self.ofctl_rules[switch_name].append((cmd, parameters))
        cmd = "add-flow"
        parameters = "in_port=2,actions=set_queue:{}2".format(str(switch_port))
        self.ofctl_rules[switch_name].append((cmd, parameters))
    def rules_for_forward(self, switch_name, net):
        cmd = "add-flow"
        parameters = "in_port=1,actions=output:3"
        self.ofctl_rules[switch_name].append((cmd, parameters))
        cmd = "add-flow"
        parameters = "in_port=2,actions=output:3"
        self.ofctl_rules[switch_name].append((cmd, parameters))
        if switch_name == 's1':
            h1 = net.getNodeByName('h1')
            cmd = "add-flow"
            parameters = "in_port=3,ip,ip_dst={},actions=output:1".format(h1.IP())
            self.ofctl_rules[switch_name].append((cmd, parameters))
            h3 = net.getNodeByName('h3')
            cmd = "add-flow"
            parameters = "in_port=3,ip,ip_dst={},actions=output:2".format(h3.IP())
            self.ofctl_rules[switch_name].append((cmd, parameters))
        elif switch_name == 's2':
            h2 = net.getNodeByName('h2')
            cmd = "add-flow"
            parameters = "in_port=3,ip,ip_dst={},actions=output:1".format(h2.IP())
            self.ofctl_rules[switch_name].append((cmd, parameters))
            h4 = net.getNodeByName('h4')
            cmd = "add-flow"
            parameters = "in_port=3,ip,ip_dst={},actions=output:2".format(h4.IP())
            self.ofctl_rules[switch_name].append((cmd, parameters))
    def generate_rules(self, net):
        # topo.links: [('s2', 'h2', {'node1': 's2', 'node2': 'h2', 'port2': 0, 'port1': 2}), ('s1', 's2', {'node1': 's1', 'node2': 's2', 'port2': 1, 'port1': 2}), ('h1', 's1', {'node1': 'h1', 'node2': 's1', 'port2': 20, 'port1': 10}), ('s2', 'h4', {'node1': 's2', 'node2': 'h4', 'port2': 0, 'port1': 3}), ('s1', 'h3', {'node1': 's1', 'node2': 'h3', 'port2': 0, 'port1': 3})]
        for (node1, node2, info) in self.topo.links(withInfo = True):
            print(node1, node2, info)
            if node1[0] == 's' and node2[0] == 's':
                s1_name = node1
                s2_name = node2
                s1_port = info['port1']
                s2_port = info['port2']
                s1_intf = '{}-eth{}'.format(s1_name, info['port1'])
                s2_intf = '{}-eth{}'.format(s2_name, info['port2'])
                self.rules_for_pqueue(s1_name, s1_intf, s1_port)
                self.rules_for_pqueue(s2_name, s2_intf, s2_port)
                self.rules_for_forward(s1_name, net)
                self.rules_for_forward(s2_name, net)     

    def _implement_switch_rules(self, switch, cmd_list, rule_type):
        print(switch, cmd_list)
        if rule_type == 'ofctl':
            for cmd, parameters in cmd_list:
                switch.dpctl(cmd, parameters)
        elif rule_type == 'vsctl':
            for cmd, parameters in cmd_list:
                switch.vsctl(cmd, parameters)
    
    def implement_rules(self, net):
        print("Implementing vsctl rules")
        process_list = []
        for switch in self.vsctl_rules:
            p = Process(target=self._implement_switch_rules, args=(net.getNodeByName(switch), self.vsctl_rules[switch], 'vsctl'))
            process_list.append(p)
            p.start()
        for p in process_list:
            p.join()
        print("Implementing ofctl rules")
        process_list = []
        for switch in self.ofctl_rules:
            p = Process(target=self._implement_switch_rules, args=(net.getNodeByName(switch), self.ofctl_rules[switch], 'ofctl'))
            process_list.append(p)
            p.start()
        for p in process_list:
            p.join()

class TestBed(object):
    def __init__(self):
        self.topo = MyTopo()
        self.net = Mininet(
            topo = self.topo,
            switch=mininet.node.OVSSwitch,
            link=TCLink,
            controller=None,
            cleanup=True,
            autoSetMacs=True, 
            listenPort=6631
        )
        self.net.start()
        self.net.staticArp()
        self.rules_handler = RulesHandler(self.topo, self.net)
        self.pkt_size = 1000
        mininet.util.dumpNetConnections(self.net)
    def iperfPair(self, client, server, bw, num_session, port):
        server_file = "{}_to_{}_server.txt".format(client.name, server.name)
        server_cmd = "iperf -s -u -p {} -f b -i 1 > {} &".format(port, server_file)
        logging.info("server {} cmd: {}".format(server.name, server_cmd))
        server.cmd(server_cmd)
        client_file = "{}_to_{}_client.txt".format(client.name, server.name)
        client_cmd = "iperf -c {} -s -u -p {} -u -i 1 -b {}K -t 15 -l {} -f b -P {} > {} &".format(server.IP(), port, bw, self.pkt_size, num_session, client_file)
        logging.info("client {} cmd: {}".format(client.name, client_cmd))
        client.cmd(client_cmd)
    def testThrpt(self):
        h1 = self.net.getNodeByName('h1')
        h2 = self.net.getNodeByName('h2')
        h3 = self.net.getNodeByName('h3')
        h4 = self.net.getNodeByName('h4')
        self.iperfPair(client = h1, server = h2, bw = 2000, num_session = 1, port = 5000)
        self.iperfPair(client = h3, server = h4, bw = 400, num_session = 1, port = 5001)
        

    def start(self):
        h1 = self.net.getNodeByName('h1')
        h2 = self.net.getNodeByName('h2')
        h3 = self.net.getNodeByName('h3')
        h4 = self.net.getNodeByName('h4')
        self.rules_handler.implement_rules(self.net)
        time.sleep(5)
        self.testThrpt()
        time.sleep(30)
        # self.net.ping(hosts=[h1, h2])
        # self.net.ping(hosts=[h3, h4])
        # self.net.ping(hosts=[h1, h3])
        # cli = CLI(self.net)
        # cli.run()
        # self.testThrpt()
        print("Done.")
        
        


# topo = MyTopo()
# net = Mininet(topo = topo)
# print(topo.get_switches())
# print(topo.addHost('h3'))
# print(topo.switches())
# print(topo.port('h1', 's1'))
# print(topo.port('h2', 's4'))
# print(topo.port('s3', 's4'))
# print(topo.addLink('h2', 'h3'))
# print(topo.port('h2', 'h3'))
# print(topo.links(withInfo = True))
# print(topo.iterLinks(withKeys = True, withInfo = True))
# host_node = net.getNodeByName('h1')
# print(host_node.intfList())
# print(host_node.intfNames())

test_bed = TestBed()
time.sleep(5)
test_bed.start()