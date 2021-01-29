#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import irange, dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import RemoteController

import argparse
import sys
import time


class ClosTopo(Topo):

    def __init__(self, fanout, cores, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        core_switches = []
        aggregation_switches = []
        edge_switches = []
        hosts = []

        aggregations_num = fanout*cores
        edges_num = fanout*aggregation_switches
        hosts_num = fanout*edge_switches

        counter=1
        for i in range(cores):
            switch=self.addSwitch('c'+str(counter))
            core_switches.append(switch)
            counter=counter+1

        for i in range(aggregations_num):
            switch=self.addSwitch('a'+str(counter))
            for j in range(cores):
                self.addLink(switch,core_switches[j])
            aggregation_switches.append(switch)
            counter=counter+1
        pass
        for i in range(edges_num):
            switch=self.addSwitch('e'+str(counter))
            for j in range(aggregations_num):
                self.addLink(switch,aggregation_switches[j])
            edge_switches.append(switch)
            counter=counter+1
        pass
        host_counter=1
        for i in range(edges_num):
            for j in range(2):
                host=self.addHost('h'+str(host_counter))
                self.addLink(host,edge_switches[j])
                host_counter=host_counter+1
            hosts.append(host)
        pass


def setup_clos_topo(fanout=2, cores=1):
    "Create and test a simple clos network"
    assert (fanout > 0)
    assert (cores > 0)
    topo = ClosTopo(fanout, cores)
    net = Mininet(topo=topo, controller=lambda name: RemoteController('c0', "127.0.0.1"), autoSetMacs=True, link=TCLink)
    net.start()
    time.sleep(20)  # wait 20 sec for routing to converge
    net.pingAll()  # test all to all ping and learn the ARP info over this process
    CLI(net)  # invoke the mininet CLI to test your own commands
    net.stop()  # stop the emulation (in practice Ctrl-C from the CLI
    # and then sudo mn -c will be performed by programmer)


def main(argv):
    parser = argparse.ArgumentParser(description="Parse input information for mininet Clos network")
    parser.add_argument('--num_of_core_switches', '-c', dest='cores', type=int, help='number of core switches')
    parser.add_argument('--fanout', '-f', dest='fanout', type=int, help='network fanout')
    args = parser.parse_args(argv)
    setLogLevel('info')
    setup_clos_topo(args.fanout, args.cores)


if __name__ == '__main__':
    main(sys.argv[1:])
