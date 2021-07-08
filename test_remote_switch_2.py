#!/usr/bin/env python

import logging
from three_node_topo import ThreeNodesTopo
from mininet.log import setLogLevel
from mininet.node import OVSSwitch
from MaxiNet.Frontend import maxinet

def staticArp(hosts):
  for src in hosts:
    for dst in hosts:
      if src != dst:
        hosts[src].setARP( ip=hosts[dst].IP(), mac=hosts[dst].MAC() )

def demo():
    "Simple Demo of Maxinet"
    topo = ThreeNodesTopo()
    cluster = maxinet.Cluster()
    exp = maxinet.Experiment(cluster, topo, switch=OVSSwitch)
    exp.setup()

    hs = {}
    sw = {}
    for i in range(3):
      hs[i] = exp.get_node("h{}".format(i))
      sw[i] = exp.get_node("s{}".format(i))

    staticArp(hs)
    
    port = topo.port

    # try dpctl rules
    cmd = "-O {} add-flow".format("OpenFlow13")
    # h0 -> s0 -> s1 - > h1
    parameters = "table=0,ip,ip_dst={},eth_type=0x800,actions=output:{}".format(hs[1].IP(), port['s0','s1'])
    logging.info("dpctl cmd: ovs-ofctl %s %s %s"
                        % (cmd, sw[0].name, parameters))
    sw[0].dpctl(cmd, parameters)

    parameters = "table=0,ip,ip_dst={},eth_type=0x800,actions=output:{}".format(hs[0].IP(), port['s1','s0'])
    logging.info("dpctl cmd: ovs-ofctl %s %s %s"
                        % (cmd, sw[1].name, parameters))
    sw[1].dpctl(cmd, parameters)
    # h0 -> s0 -> s2 - > h2
    parameters = "table=0,ip,ip_dst={},eth_type=0x800,actions=output:{}".format(hs[2].IP(), port['s0','s2'])
    logging.info("dpctl cmd: ovs-ofctl %s %s %s"
                        % (cmd, sw[0].name, parameters))
    sw[0].dpctl(cmd, parameters)

    parameters = "table=0,ip,ip_dst={},eth_type=0x800,actions=output:{}".format(hs[0].IP(), port['s2', 's0'])
    logging.info("dpctl cmd: ovs-ofctl %s %s %s"
                        % (cmd, sw[2].name, parameters))
    sw[2].dpctl(cmd, parameters)

    # s0 -> h0, s1 -> h1, s2 -> h2
    parameters = "table=0,ip,ip_dst={},eth_type=0x800,actions=output:{}".format(hs[0].IP(), port['s0', 'h0'])
    logging.info("dpctl cmd: ovs-ofctl %s %s %s"
                        % (cmd, sw[0].name, parameters))
    sw[0].dpctl(cmd, parameters)

    parameters = "table=0,ip,ip_dst={},eth_type=0x800,actions=output:{}".format(hs[1].IP(), port['s1', 'h1'])
    logging.info("dpctl cmd: ovs-ofctl %s %s %s"
                        % (cmd, sw[1].name, parameters))
    sw[1].dpctl(cmd, parameters)

    parameters = "table=0,ip,ip_dst={},eth_type=0x800,actions=output:{}".format(hs[2].IP(), port['s2', 'h2'])
    logging.info("dpctl cmd: ovs-ofctl %s %s %s"
                        % (cmd, sw[2].name, parameters))
    sw[2].dpctl(cmd, parameters)

    print "sleep for 5 seconds"
    time.sleep(5)
    print exp.get_node("h0").cmd("ping -c 5 10.0.0.1")
    print exp.get_node("h0").cmd("ping -c 5 10.0.0.2")

    print "sleep for 10 seconds"
    time.sleep(10)

    exp.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    demo()
