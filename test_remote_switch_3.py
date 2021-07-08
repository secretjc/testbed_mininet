#!/usr/bin/env python

"clusterdemo.py: demo of Mininet Cluster Edition prototype"
import logging
from mininet.examples.cluster import ( MininetCluster, SwitchBinPlacer,
                                       RemoteLink, RemoteOVSSwitch )
# ^ Could also use: RemoteSSHLink, RemoteGRELink
from three_node_topo import ThreeNodesTopo
from mininet.log import setLogLevel
from mininet.examples.clustercli import ClusterCLI as CLI

def iperfPair( client, server, bw, num_session, port):
    server_file = "{}_to_{}_server.txt".format(client.name, server.name)
    server_cmd = "iperf -s -u -p {} -i 1 > {} &".format(port, server_file)
    print "server {} cmd: {}".format(server.name, server_cmd)
    server.cmd(server_cmd)
    client_file = "{}_to_{}_client.txt".format(client.name, server.name)
    client_cmd = "iperf -c {} -s -u -p {} -u -i 1 -b {}M -t 10 -l 1400 -P {} > {} &".format(server.IP(), port, bw, num_session, client_file)
    print "client {} cmd: {}".format(client.name, client_cmd)
    client.cmd(client_cmd)

def demo():
    "Simple Demo of Cluster Mode"
    servers = [ 'localhost', 'ms0330.utah.cloudlab.us', 'ms0344.utah.cloudlab.us' ]
    topo = ThreeNodesTopo()
    net = MininetCluster( topo=topo, 
                          servers=servers, 
                          switch=RemoteOVSSwitch, 
                          link=RemoteLink,
                          controller=None,
                          placement=SwitchBinPlacer )
    port = {}
    for link in net.links:
      intf = link.intf1.name
      p = intf.find("-eth")
      node1 = intf[:p]
      port1 = int(intf[p+4:])
      intf = link.intf2.name
      p = intf.find("-eth")
      node2 = intf[:p]
      port2 = int(intf[p+4:])
      logging.info("intf1 node:{}, port:{} ; intf2 node:{}, port:{}".format(node1, port1, node2, port2))
      port[node1, node2] = port1
      port[node2, node1] = port2
    hs = {}
    sw = {}
    for i in range(3):
      hs[i] = net.getNodeByName("h{}".format(i))
      sw[i] = net.getNodeByName("s{}".format(i))
    net.start()
    net.staticArp()
    # try dpctl rules
    cmd = "-O {} add-flow".format("OpenFlow13")
    # h0 -> s0 -> s1 - > h1
    parameters = "table=0,ip,ip_dst={},eth_type=0x800,actions=push_mpls:0x8847,set_field:0->mpls_label,output:{}".format(hs[1].IP(), port['s0','s1'])
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
    

    parameters = "table=1,ip,ip_dst={},eth_type=0x800,actions=output:{}".format(hs[1].IP(), port['s1', 'h1'])
    logging.info("dpctl cmd: ovs-ofctl %s %s %s"
                        % (cmd, sw[1].name, parameters))
    sw[1].dpctl(cmd, parameters)
    parameters = "table=0,mpls,mpls_label=0,eth_type=0x8847,actions=pop_mpls:0x800,goto_table:1"
    sw[1].dpctl(cmd, parameters)

    parameters = "table=0,ip,ip_dst={},eth_type=0x800,actions=output:{}".format(hs[2].IP(), port['s2', 'h2'])
    logging.info("dpctl cmd: ovs-ofctl %s %s %s"
                        % (cmd, sw[2].name, parameters))
    sw[2].dpctl(cmd, parameters)

    iperfPair(hs[0], hs[2], 20, 1, 5005)

    ###################
    CLI( net )
    net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    demo()
