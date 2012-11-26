#!/usr/bin/env python

"""Asynchronous client using Twisted with GNUTLS"""

from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet import reactor

from gnutls.constants import *
from gnutls.crypto import *
from gnutls.errors import *
from gnutls.interfaces.twisted import X509Credentials

from gnutls.library.constants import GNUTLS_CIPHER_AES_256_CBC


class EchoProtocol(LineOnlyReceiver):

    def connectionMade(self):
        self.sendLine('echo')

    def lineReceived(self, line):
        print 'received: ', line
        self.transport.loseConnection()

    def connectionLost(self, reason):
        reactor.stop()

class EchoFactory(ClientFactory):
    protocol = EchoProtocol

    def clientConnectionFailed(self, connector, err):
        print err.value
        reactor.stop()

cred = X509Credentials()

cred.session_params.protocols = (PROTO_TLS1_2,)
cred.session_params.ciphers = (GNUTLS_CIPHER_AES_256_CBC,)
cred.session_params.compressions = (COMP_DEFLATE, COMP_NULL)

reactor.connectTLS('localhost', 10000, EchoFactory(), cred)
reactor.run()

