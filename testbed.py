"""
Start mininet testbed.
Run with Python2.7+
"""

import sys
import math
from collections import defaultdict
#import copy
import time
import logging
from mininet.examples.cluster import ( MininetCluster, SwitchBinPlacer,
                                       RemoteLink, RemoteOVSSwitch )
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink
import mininet.util
import mininet.node

from topology import Topology
#from graph import Graph
#from failure_detector import FailureDetector
from constants import *

class Testbed(object):
    """
    This class defines the testbed.
    """
    def __init__(self, configs):
        logging.info("======================")
        logging.info("Initializing topology.")

        self.topo = Topology(configs)
        servers = [ 'localhost', 'ms0721.utah.cloudlab.us', 'ms0712.utah.cloudlab.us' ]
        self.net = MininetCluster( topo=self.topo, 
                                   servers=servers, 
                                   switch=RemoteOVSSwitch, 
                                   link=RemoteLink,
                                   controller=None,
                                   cleanup=True,
                                   autoSetMacs=True,
                                   placement=SwitchBinPlacer )
        #self.net = Mininet(topo=self.topo, 
        #                   switch=mininet.node.OVSSwitch,
        #                   link=TCLink,
        #                   controller=None, 
        #                   cleanup=True,
        #                   autoSetMacs=True, 
        #                   listenPort=6631)
        self.topo.getNetInfo(self.net)
        try:
            #self.net.build()
            self.net.start()
            self.net.staticArp()
        except:
            logging.error("Error occured during mininet starting.")
            self.net.stop()
        self.configs = configs
        #self.failure_detector = FailureDetector(
        #    polling_interval=configs['main_config']['main']['failure_polling_interval'],
        #    intfs=self.topo.intfs.keys(),
        #    nbr_intf=self.topo.nbr_intf,
        #    callback_on_down=self.link_down_handler,
        #    callback_on_up=self.link_up_handler)
        self.num_flow_groups = defaultdict(int)
        #self.intfs_to_ip_sd_pairs = defaultdict(list)
        self.tunnel_first_hop = {}

        logging.info("Network Details.")
        logging.info("\tConnections:")
        mininet.util.dumpNetConnections(self.net)
        logging.info("\tSwitch Ports:")
        mininet.util.dumpPorts(self.net.switches)

    def _configure_initial_split(self):
        logging.info("\tConfiguring path weights...")
        initial_file = self.configs['topo_config']['topology']['initial_file']
        groups_info = {}
        with open(initial_file, 'r') as f:
            for line in f:
                if "s" in line:
                    continue
                tunnel_num, s, t, prio, weight = line.strip().split(' ')
                #if int(weight) == 0:
                #    continue
                port = self.tunnel_first_hop[tunnel_num]
                if (s, t, prio) not in groups_info:
                    if prio == 'h':
                        group_id = int(t) * 2 + 2
                    else:
                        group_id = int(t) * 2 + 1
                    groups_cmd = "group_id={},type=select,selection_method=hash,fields(ip_src,ip_dst,tcp_src,tcp_dst,udp_src,udp_dst)".format(group_id)
                    num_bucket = 0
                else:
                    groups_cmd, num_bucket = groups_info[(s, t, prio)]
                num_bucket += 1
                bucket_cmd = "bucket=bucket_id={},weight={},actions=push_mpls:0x8847,set_field:{}->mpls_label,output:{}".format(num_bucket, weight, tunnel_num, port)
                groups_cmd = groups_cmd + "," + bucket_cmd
                groups_info[(s, t, prio)] = (groups_cmd, num_bucket)
        for s, t, prio in groups_info:
            src_switch_name = 's_{}'.format(s)
            #dst_switch_name = 's_{}'.format(t)
            src_switch = self.topo.switch_set[src_switch_name]
            cmd = "-O {} add-group".format(OPENFLOW_PROTO)
            parameters, _ = groups_info[s, t, prio]
            parameters = "\"" + parameters + "\""
            logging.debug("dpctl cmd: ovs-ofctl %s %s %s"
                            % (cmd, src_switch_name, parameters))
            src_switch.dpctl(cmd, parameters)

            if prio == 'h':
                group_id = int(t) * 2 + 2
                dst_host_name = 'hh_{}'.format(t)
            else:
                group_id = int(t) * 2 + 1
                dst_host_name = 'hl_{}'.format(t)
            dst_host = self.topo.host_set[dst_host_name]
            cmd = "-O {} add-flow".format(OPENFLOW_PROTO)
            parameters = "table=0,ip,ip_dst={},eth_type=0x800,actions=group:{}".format(dst_host.IP(), group_id)
            logging.debug("dpctl cmd: ovs-ofctl %s %s %s"
                            % (cmd, src_switch_name, parameters))
            src_switch.dpctl(cmd, parameters)

    def _configure_tunnels(self):
        # table 1: forward to dst hosts
        for dst_switch_name in self.topo.switch_set:
            dst_switch = self.topo.switch_set[dst_switch_name]
            logging.info("checking s: {} {}".format(dst_switch_name, self.topo.hosts_to_switches[dst_switch_name]))
            for dst_host in self.topo.hosts_to_switches[dst_switch_name]:
                port = self.topo.switch_ports[dst_switch_name][dst_host.name]
                cmd = "-O {} add-flow".format(OPENFLOW_PROTO)
                parameters = \
                    "table=1,ip,ip_dst={},actions=output:{}".format(dst_host.IP(), port)
                logging.debug("dpctl cmd: ovs-ofctl %s %s %s"
                                  % (cmd, dst_switch_name, parameters))

                dst_switch.dpctl(cmd, parameters)
        tunnel_file = self.configs['topo_config']['topology']['tunnel_file']
        with open(tunnel_file, 'r') as f:
            for line in f:
                if "s" in line:
                    continue
                # record first hop for groups
                tunnel_num, s, t, edges = line.strip().split(' ')
                logging.info("\tConfiguring tunnel {}".format(tunnel_num))
                edge = edges.split(',')[0]
                src, dst = edge.split('-')
                src_switch_name = 's_{}'.format(src)
                dst_switch_name = 's_{}'.format(dst)
                port = self.topo.switch_ports[src_switch_name][dst_switch_name]
                self.tunnel_first_hop[tunnel_num] = port
                # set intermediate hops
                for edge in edges.split(',')[1:]:
                    src, dst = edge.split('-')
                    src_switch_name = 's_{}'.format(src)
                    dst_switch_name = 's_{}'.format(dst)
                    src_switch = self.topo.switch_set[src_switch_name]
                    port = self.topo.switch_ports[src_switch_name][dst_switch_name]
                    cmd = "-O {} add-flow".format(OPENFLOW_PROTO)

                    parameters = \
                        "table=0,mpls,mpls_label={},eth_type=0x8847,actions=output:{}".format(
                            tunnel_num, port)
                    logging.debug("dpctl cmd: ovs-ofctl %s %s %s"
                                  % (cmd, src_switch_name, parameters))
                    src_switch.dpctl(cmd, parameters)
                # last hop to strip label and go to table 1
                dst_switch_name = 's_{}'.format(t) 

                dst_switch = self.topo.switch_set[dst_switch_name]
                cmd = "-O {} add-flow".format(OPENFLOW_PROTO)

                parameters = \
                    "table=0,mpls,mpls_label={},eth_type=0x8847,actions=pop_mpls:0x800,goto_table:1".format(tunnel_num)
                logging.debug("dpctl cmd: ovs-ofctl %s %s %s"
                                  % (cmd, dst_switch_name, parameters))
                dst_switch.dpctl(cmd, parameters)

    def start(self):
        self._configure_tunnels()
        self._configure_initial_split()
        logging.info("Lanuching link failure detector.")
        #self.failure_detector.process.start()
        self.topo.testThroughput()
        
        cli = CLI(self.net)
        try:
            cli.run()
            self._start_simulation()
        except KeyboardInterrupt:
            logging.error("CLI interrupted by keyboard.")
            self._clean_up()
        except:
            logging.error("Unexpected exception catched.")
            self._clean_up()

    def _start_simulation(self):
        pass

    def _clean_up(self):
        logging.info("Cleaning up.")
        #self.failure_detector.process.terminate()
        self.net.stop()

if __name__ == '__main__':
    pass 
