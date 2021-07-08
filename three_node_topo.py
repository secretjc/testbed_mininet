from mininet.topo import Topo

# The build() method is expected to do this:
# pylint: disable=arguments-differ

class ThreeNodesTopo( Topo ):
    "Topology for a 3-node network."

    def build( self ):
        # Numbering:  h0,h1,h2, s0,s1,s2
        self.hostNum = 3
        self.switchNum = 3
        switchs = []
        hosts = []
        for i in range(3):
          sw_node = self.addSwitch( 's%s' % i )
          switchs.append(sw_node)
          hs_node = self.addHost( 'h%s' % i )
          hosts.append(hs_node)
          self.addLink( hs_node, sw_node, bw=50, delay="0.1ms" )
        self.addLink( switchs[0], switchs[1], bw=10, delay="0.1ms" )
        self.addLink( switchs[1], switchs[2], bw=10, delay="0.1ms" )
        self.addLink( switchs[0], switchs[2], bw=10, delay="5ms" )
