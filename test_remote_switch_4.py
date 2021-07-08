#!/usr/bin/env python

"clusterdemo.py: demo of Mininet Cluster Edition prototype"
import logging
from mininet.examples.cluster import ( MininetCluster, SwitchBinPlacer,
                                       RemoteLink, RemoteOVSSwitch )
# ^ Could also use: RemoteSSHLink, RemoteGRELink
from three_node_topo import ThreeNodesTopo
from mininet.log import setLogLevel
from mininet.examples.clustercli import ClusterCLI as CLI

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
    cmd_group = "-O {} add-group".format("OpenFlow13")
    # h0 -> s0 -> 2 choices

    parameters = "group_id=0,type=select,selection_method=hash,fields(ip_src,ip_dst,tcp_src,tcp_dst,udp_src,udp_dst),"
    parameters += "bucket=bucket_id=0,weight=50,actions=push_mpls:0x8847,set_field:{}->mpls_label,output:{},".format(3, port['s0', 's1'])
    parameters += "bucket=bucket_id=1,weight=50,actions=push_mpls:0x8847,set_field:{}->mpls_label,output:{},".format(2, port['s0', 's2'])
    sw[0].dpctl(cmd_group, "\"" + parameters + "\"")

    parameters = "table=0,ip,ip_dst={},eth_type=0x800,actions=group:0".format(hs[2].IP())
    logging.info("dpctl cmd: ovs-ofctl %s %s %s"
                        % (cmd, sw[0].name, parameters))
    sw[0].dpctl(cmd, parameters)


    # s0 -> h0
    parameters = "table=0,ip,ip_dst={},eth_type=0x800,actions=output:{}".format(hs[0].IP(), port['s0','h0'])
    sw[0].dpctl(cmd, parameters)

    # h2 -> s2 --> s0 -> h0
    parameters = "table=0,ip,ip_dst={},eth_type=0x800,actions=output:{}".format(hs[0].IP(), port['s2', 's0'])
    logging.info("dpctl cmd: ovs-ofctl %s %s %s"
                        % (cmd, sw[2].name, parameters))
    sw[2].dpctl(cmd, parameters)

    parameters = "table=0,mpls,mpls_label=3,eth_type=0x8847,actions=output:{}".format(port['s1','s2'])
    sw[1].dpctl(cmd, parameters)

    parameters = "table=0,mpls,mpls_label=3,eth_type=0x8847,actions=pop_mpls:0x800,goto_table:1"
    sw[2].dpctl(cmd, parameters)
    parameters = "table=0,mpls,mpls_label=2,eth_type=0x8847,actions=pop_mpls:0x800,goto_table:1"
    sw[2].dpctl(cmd, parameters)
    parameters = "table=1,ip,ip_dst={},eth_type=0x800,actions=output:{}".format(hs[2].IP(), port['s2', 'h2'])
    logging.info("dpctl cmd: ovs-ofctl %s %s %s"
                        % (cmd, sw[2].name, parameters))
    sw[2].dpctl(cmd, parameters)

    ###################
    CLI( net )
    net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    demo()