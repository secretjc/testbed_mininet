import logging
from constants import *
from collections import defaultdict

class Rule_handler(object):
    """
    This class defines the rule handler.
    """
    def __init__(self, topo):
      self.topo = topo
      self.tunnel_first_hop = {}
      self.rules = {}

    def _implement_switch_rules(self, switch, cmd_list):
        for cmd, parameters in cmd_list:
            switch.dpctl(cmd, parameters)

    def implement_rules(self, rule_name):
        logging.info("\tImplementing rules: {} ...".format(rule_name))
        #TODO: make it multiprocessing
        rules_set = self.rules[rule_name]
        for switch in rules_set:
            self._implement_switch_rules(switch, rules_set[switch])

    def configure_tunnels(self, tunnel_file, rule_name):
        logging.info("\tConfiguring tunnels...")
        rules_set = defaultdict(list)
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
                rules_set[dst_switch].append((cmd, parameters))
                #dst_switch.dpctl(cmd, parameters)
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
                    rules_set[src_switch].append((cmd, parameters))
                    #src_switch.dpctl(cmd, parameters)
                # last hop to strip label and go to table 1
                dst_switch_name = 's_{}'.format(t) 

                dst_switch = self.topo.switch_set[dst_switch_name]
                cmd = "-O {} add-flow".format(OPENFLOW_PROTO)

                parameters = \
                    "table=0,mpls,mpls_label={},eth_type=0x8847,actions=pop_mpls:0x800,goto_table:1".format(tunnel_num)
                logging.debug("dpctl cmd: ovs-ofctl %s %s %s"
                                  % (cmd, dst_switch_name, parameters))
                rules_set[dst_switch].append((cmd, parameters))
                #dst_switch.dpctl(cmd, parameters)
        self.rules[rule_name] = rules_set

    def configure_initial_split(self, initial_file, rule_name):
        rules_set = defaultdict(list)
        logging.info("\tConfiguring path weights...")
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
            rules_set[src_switch].append((cmd, parameters))
            #src_switch.dpctl(cmd, parameters)

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
            rules_set[src_switch].append((cmd, parameters))
            #src_switch.dpctl(cmd, parameters)
        self.rules[rule_name] = rules_set
