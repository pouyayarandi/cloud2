#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import irange,dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import RemoteController
from itertools import product

import argparse
import sys
import time


class ClosTopo(Topo):

    def __init__(self, fanout, cores, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        
        "Set up Core and Aggregate level, Connection Core - Aggregation level"
        
        count = cores
        lower, upper = 1, count
        cores = [ self.addSwitch('c%s' % s) for s in irange(lower, upper) ]
        
        count *= fanout
        lower, upper = upper + 1, upper + count
        aggregates = [ self.addSwitch('a%s' % s) for s in irange(lower, upper) ]
        
        for core, aggregate in product(cores, aggregates):
            self.addLink(core, aggregate)

        "Set up Edge level, Connection Aggregation - Edge level "
        
        count *= fanout
        lower, upper = upper + 1, upper + count
        edges = [ self.addSwitch('e%s' % s) for s in irange(lower, upper) ]
        
        for aggregate, edge in product(aggregates, edges):
            self.addLink(aggregate, edge)
        
        "Set up Host level, Connection Edge - Host level "
        
        lower, upper = 1, count * fanout
        hosts = [ self.addHost('h%s' % h) for h in irange(lower, upper) ]
        
        for i in range(upper):
            self.addLink(hosts[i], edges[i / fanout])
	

def setup_clos_topo(fanout=2, cores=1):
    "Create and test a simple clos network"
    assert(fanout>0)
    assert(cores>0)
    topo = ClosTopo(fanout, cores)
    net = Mininet(topo=topo, controller=lambda name: RemoteController('c0', "127.0.0.1"), autoSetMacs=True, link=TCLink)
    net.start()
    time.sleep(20) #wait 20 sec for routing to converge
    net.pingAll()  #test all to all ping and learn the ARP info over this process
    CLI(net)       #invoke the mininet CLI to test your own commands
    net.stop()     #stop the emulation (in practice Ctrl-C from the CLI 
                   #and then sudo mn -c will be performed by programmer)

    
def main(argv):
    parser = argparse.ArgumentParser(description="Parse input information for mininet Clos network")
    parser.add_argument('--num_of_core_switches', '-c', dest='cores', type=int, help='number of core switches')
    parser.add_argument('--fanout', '-f', dest='fanout', type=int, help='network fanout')
    args = parser.parse_args(argv)
    setLogLevel('info')
    setup_clos_topo(args.fanout, args.cores)


if __name__ == '__main__':
    main(sys.argv[1:])
