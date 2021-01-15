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


class BCubeTopo(Topo):

    def __init__(self, n, k, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        
        serverCount, switchCountPerLevel = n ** (k + 1), n ** k
        
        "Setup hosts"
        lower, upper = 0, serverCount - 1
        hosts = [ self.addHost('h%s' % h) for h in irange(lower, upper) ]

        "Setup switches"
        switches = []
        for level in range(k + 1):
            lower = serverCount + (level * switchCountPerLevel)
	    upper = lower + switchCountPerLevel - 1
	    switches += [ self.addSwitch('s%s' % s) for s in irange(lower, upper) ]
            
        "Connect each host to the desired switches"
        for i in range(serverCount):
            for level in range(k + 1):
                shift, length = n ** level, n ** (level + 1)
                lower = level * switchCountPerLevel
                connect = lower + (((i / length) * shift) + (i % shift))
                
                self.addLink(hosts[i], switches[connect])
	

def setup_bcube_topo(n=4, k=1):
    "Create and test a simple BCube network"
    assert(n>0)
    assert(k>=0)
    topo = BCubeTopo(n, k)
    net = Mininet(topo=topo, controller=lambda name: RemoteController('c0', "127.0.0.1"), autoSetMacs=True, link=TCLink)
    net.start()
    time.sleep(20) #wait 20 sec for routing to converge
    net.pingAll()  #test all to all ping and learn the ARP info over this process
    CLI(net)       #invoke the mininet CLI to test your own commands
    net.stop()     #stop the emulation (in practice Ctrl-C from the CLI 
                   #and then sudo mn -c will be performed by programmer)

    
def main(argv):
    parser = argparse.ArgumentParser(description="Parse input information for mininet BCube network")
    parser.add_argument('--n-factor', '-n', dest='n', type=int, help='value of n factor')
    parser.add_argument('--k-factor', '-k', dest='k', type=int, help='value of k factor')
    args = parser.parse_args(argv)
    setLogLevel('info')
    setup_bcube_topo(args.n, args.k)


if __name__ == '__main__':
    main(sys.argv[1:])
