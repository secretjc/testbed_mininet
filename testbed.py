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

from rule_handler import Rule_handler
from topology import Topology
#from graph import Graph
#from failure_detector import FailureDetector
from constants import *

class Testbed(object):
    """
    This class defines the testbed.
    """
    def __init__(self, configs, is_cluster):
        logging.info("======================")
        logging.info("Initializing topology.")

        self.topo = Topology(configs)
        if is_cluster:
            servers = [ 'localhost', 
                    #'ms0301.utah.cloudlab.us',
                    #'ms0313.utah.cloudlab.us',
                    #'ms0338.utah.cloudlab.us',
                    'ms0301.utah.cloudlab.us',
                    'ms0325.utah.cloudlab.us' ]
            self.net = MininetCluster( topo=self.topo, 
                                   servers=servers, 
                                   switch=RemoteOVSSwitch, 
                                   link=RemoteLink,
                                   controller=None,
                                   cleanup=True,
                                   autoSetMacs=True,
                                   placement=SwitchBinPlacer )
        else:
            self.net = Mininet(topo=self.topo, 
                               switch=mininet.node.OVSSwitch,
                               link=TCLink,
                               controller=None, 
                               cleanup=True,
                               autoSetMacs=True, 
                               listenPort=6631)
        self.rule_handler = Rule_handler(self.topo)
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

        logging.info("Network Details.")
        logging.info("\tConnections:")
        mininet.util.dumpNetConnections(self.net)
        logging.info("\tSwitch Ports:")
        mininet.util.dumpPorts(self.net.switches)

    def start(self):
        self.rule_handler.configure_tunnels(self.configs['topo_config']['topology']['tunnel_file'], 'tunnel')
        self.rule_handler.configure_initial_split(self.configs['topo_config']['topology']['initial_file'], 'initial')
        self.rule_handler.implement_rules('tunnel')
        self.rule_handler.implement_rules('initial')
        #logging.info("Lanuching link failure detector.")
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
