#!/usr/bin/env python
from twisted.web import proxy, http
from twisted.internet import reactor
from urlparse import urlparse

files = dict()

class ProxyRequest(proxy.ProxyRequest):
    def process(self):
		_url = urlparse(self.path)
		url = _url.netloc+_url.path
		if url in files:
			self.write(open('files/'+files[url]).read())
			self.finish()
		else:
			proxy.ProxyRequest.process(self)

class LocalProxy(http.HTTPChannel):
    requestFactory = ProxyRequest

for row in open('files/references'):
	ref = row.split(' ')
	if ref:
		files[ref[0]] = ref[1].strip()

factory = http.HTTPFactory()
factory.protocol = LocalProxy
reactor.listenTCP(8080, factory)
reactor.run()
