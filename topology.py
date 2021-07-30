"""
Build topology.
Run with Python2.7+
"""
from collections import defaultdict
import logging

import mininet.node
import mininet.link
from mininet.net import Mininet
from mininet.topo import Topo

from constants import *

class Topology( Topo ):
    """
    This class is used to initialize the topology in Mininet.
    """

    def build( self, configs ):
        # Numbering:  h0,h1,h2, s0,s1,s2
        self.scale = 1
        self.base_bw = 500
        self.pkt_size = 1000
        self.kbit_per_pkt = self.pkt_size * 8 / 1000.0
        self.configs = configs
        self.failed_links = self._get_failed_links()
        self.host_set = {}
        self.switch_set = {}
        self.graph = defaultdict(set)
        self.switch_ports = {}
        self.hosts_to_switches = {}
        #self.intfs = {}
        #self.nbr_intf = {}
        self.build_topo()
        self.hostNum = len(self.host_set)
        self.switchNum = len(self.switch_set)

    def build_topo(self):
        """
        Add hosts, switches, links when parsing the file.
        """
        topo_file = self.configs['topo_config']['topology']['cap_file']
        with open(topo_file, 'r') as f:
            for line in f:
                if line[0] == 'i':
                    continue

                src, dst, cap, lt = line.strip().split()

                if src in self.graph[dst]:
                    continue

                cap = float(cap)
                self.graph[src].add(dst)
                self.graph[dst].add(src)
                for node in [src, dst]:
                    if "s_{}".format(node) in self.switch_set:
                        continue

                    # Add switches
                    switch_name = 's_{}'.format(node)
                    s = self.addSwitch(switch_name)
                    self.switch_set[switch_name] = s

                    # Add 1 host
                    host_name = 'h_{}'.format(node)
                    h = self.addHost(host_name)
                    self.host_set[host_name] = h
                    self.hosts_to_switches[switch_name] = host_name

                    # Connect the host and switch.
                    # Caveat: Setting port number as 0 causes problems
                    # in mininet.
                    linkopts = dict(bw=self.base_bw * self.scale)
                    l = self.addLink(h, s, port1=1, port2=1, **linkopts)
                    self.switch_ports[switch_name] = {host_name: 1}
                    #self.intfs[l.intf2] = (s, h)

                # Add links between src and dst switches.
                src_switch = 's_{}'.format(src)
                dst_switch = 's_{}'.format(dst)
                linkopts = dict(bw=cap * self.scale)
                p1 = len(self.switch_ports[src_switch]) + 1
                p2 = len(self.switch_ports[dst_switch]) + 1
                l = self.addLink(self.switch_set[src_switch],
                                self.switch_set[dst_switch],
                                port1=p1, port2=p2,
                                **linkopts)
                self.switch_ports[src_switch][dst_switch] = p1
                #self.intfs[l.intf1] = \
                #    (self.switch_set[src_switch], self.switch_set[dst_switch])
                #self.nbr_intf[l.intf1] = l.intf2
                self.switch_ports[dst_switch][src_switch] = p2
                #self.intfs[l.intf2] = \
                #    (self.switch_set[dst_switch], self.switch_set[src_switch])
                #self.nbr_intf[l.intf2] = l.intf1

        logging.debug("Switches: %s" % self.switch_set)
        logging.debug("Hosts: %s" % self.host_set)
        logging.debug("Switch ports: %s" % self.switch_ports)
        #logging.debug("Switch interfaces: %s" % [(intf.name, link[0].name,
        #    link[1].name) for intf, link in self.intfs.iteritems()])
        logging.debug("Network graph: %s" % self.graph)

    def getNetInfo(self, net):
        for switch_name in self.switch_set:
            self.switch_set[switch_name] = net.getNodeByName(switch_name)
        for host_name in self.host_set:
            self.host_set[host_name] = net.getNodeByName(host_name)
        for switch_name in self.hosts_to_switches:
            host_name = self.hosts_to_switches[switch_name]
            self.hosts_to_switches[switch_name] = [self.host_set[host_name]]
    
    def _get_failed_links(self):
        str_failed_links = self.configs['topo_config']['topology']['failed_links']
        if "no" in str_failed_links:
            return []
        else:
            link_name_list = str_failed_links.strip().split(',')
            link_list = []
            for link in link_name_list:
                u, v = link.split('-')
                u = "s_{}".format(u)
                v = "s_{}".format(v)
                if u < v:
                    link_list.append((u,v))
            return link_list
        
    def fail_links(self, net):
        if len(self.failed_links) == 0:
            logging.info("No link to fail.")
        for s1, s2 in self.failed_links:
            logging.info("Failing link: {}-{}".format(s1, s2))
            net.configLinkStatus(s1, s2, 'down')

    def iperfPair(self, client, server, bw, num_session, port):
        server_file = "{}_to_{}_server.txt".format(client.name, server.name)
        server_cmd = "iperf -s -u -p {} -f b -i 1 > {} &".format(port, server_file)
        logging.info("server {} cmd: {}".format(server.name, server_cmd))
        server.cmd(server_cmd)
        client_file = "{}_to_{}_client.txt".format(client.name, server.name)
        client_cmd = "iperf -c {} -s -u -p {} -u -i 1 -b {}K -t 30 -l {} -f b -P {} > {} &".format(server.IP(), port, bw, self.pkt_size, num_session, client_file)
        logging.info("client {} cmd: {}".format(client.name, client_cmd))
        client.cmd(client_cmd)

    def testThroughput(self):
        port = 5000
        bw_ = self.configs['topo_config']['demand']['bw']
        demand_file = self.configs['topo_config']['demand']['demand_file']
        sd_pair = []
        with open(demand_file, 'r') as f:
            for line in f:
                if 's' in line:
                    continue
                src, dst, dm = line.strip().split()
                if int(dm) * self.scale / self.kbit_per_pkt < 2:
                    dm = 2 * self.kbit_per_pkt / self.scale
                session = 1 #int(float(dm) / bw)
                sd_pair.append((self.host_set[src],
                                self.host_set[dst],
                                session,
                                int(dm) * self.scale))
        #sd_pair = [(self.host_set['hh_0'], self.host_set['hh_2'], 20),
        #           (self.host_set['hl_0'], self.host_set['hl_2'], 50),
        #           (self.host_set['hh_0'], self.host_set['hh_1'], 20),
        #           (self.host_set['hh_1'], self.host_set['hh_0'], 50)]
        for server, client, num_session, bw in sd_pair:
            self.iperfPair(server, client, bw, num_session, port)
            port += 1
