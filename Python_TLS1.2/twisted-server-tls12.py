#!/usr/bin/env python

"""Asynchronous server using Twisted with GNUTLS"""

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.error import CannotListenError, ConnectionDone
from twisted.internet import reactor

from gnutls.constants import *
from gnutls.crypto import *
from gnutls.errors import *
from gnutls.interfaces.twisted import X509Credentials

from gnutls.library.constants import GNUTLS_CIPHER_AES_256_CBC


class EchoProtocol(LineOnlyReceiver):

    def connectionMade(self):
        session = self.session
        session.handshake()
        print '\nNew connection from:', self.transport.socket.getpeername()
        print 'Protocol:     ', session.protocol
        print 'KX algorithm: ', session.kx_algorithm
        print 'Cipher:       ', session.cipher
        print 'MAC algorithm:', session.mac_algorithm
        print 'Compression:  ', session.compression

    def lineReceived(self, line):
        if line == 'quit':
            self.transport.loseConnection()
            return
        self.sendLine('hello')

    def connectionLost(self, reason):
        if reason.type != ConnectionDone:
            print "Connection was lost:", str(reason.value)

class EchoFactory(Factory):
    protocol = EchoProtocol

certs_path = 'certs'

cert = X509Certificate(open(certs_path + '/valid.crt').read())
key = X509PrivateKey(open(certs_path + '/valid.key').read())
cred = X509Credentials(cert, key)

cred.session_params.protocols = (PROTO_TLS1_2, )
cred.session_params.ciphers = (GNUTLS_CIPHER_AES_256_CBC,)
cred.session_params.compressions = (COMP_DEFLATE, COMP_NULL)

reactor.listenTLS(10000, EchoFactory(), cred)
reactor.run()

