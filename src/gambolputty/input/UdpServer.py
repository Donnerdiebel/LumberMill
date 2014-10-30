# -*- coding: utf-8 -*-
import logging
import threading
import SocketServer
import socket
import ssl
import sys
import Queue
import Utils
import BaseModule
from Decorators import ModuleDocstringParser


class ThreadPoolMixIn(SocketServer.ThreadingMixIn):
    """
    Use a thread pool instead of a new thread on every request.

    Using a threadpool prevents the spawning of a new thread for each incoming
    request. This should increase performance a bit.

    See: http://code.activestate.com/recipes/574454/
    """
    numThreads = 15
    allow_reuse_address = True  # seems to fix socket.error on server restart
    alive = True

    def serve_forever(self):
        """
        Handle one request at a time until doomsday.
        """
        # Set up the threadpool.
        self.requests = Queue.Queue(self.numThreads)

        for x in range(self.numThreads):
            t = threading.Thread(target=self.process_request_thread)
            t.setDaemon(1)
            t.start()

        # server main loop
        while self.alive:
            self.handle_request()
        self.server_close()


    def process_request_thread(self):
        """
        obtain request from queue instead of directly from server socket
        """
        while True:
            SocketServer.ThreadingMixIn.process_request_thread(self, *self.requests.get())


    def handle_request(self):
        """
        simply collect requests and put them on the queue for the workers.
        """
        try:
            request, client_address = self.get_request()
        except:
            etype, evalue, etb = sys.exc_info()
            print "Exception: %s, Error: %s." % (etype, evalue)
            return
        #if self.verify_request(request, client_address):
        self.requests.put((request, client_address))


class ThreadedUdpRequestHandler(SocketServer.BaseRequestHandler):

    def __init__(self, udp_server_instance, *args, **keys):
        self.udp_server_instance = udp_server_instance
        self.logger = logging.getLogger(self.__class__.__name__)
        SocketServer.BaseRequestHandler.__init__(self, *args, **keys)

    def handle(self):
        try:
            data = self.request[0].strip()
            if data == "":
                return
            host = self.client_address[0]
            port = self.client_address[1]
            event = Utils.getDefaultEventDict({"data": data}, received_from="%s:%s" % (host, port),caller_class_name='UdpServer')
            self.udp_server_instance.sendEvent(event)
        except socket.error, e:
           self.logger.warning("%sError occurred while reading from socket. Error: %s%s" % (Utils.AnsiColors.WARNING, e, Utils.AnsiColors.ENDC))
        except socket.timeout, e:
            self.logger.warning("%sTimeout occurred while reading from socket. Error: %s%s" % (Utils.AnsiColors.WARNING, e, Utils.AnsiColors.ENDC))

class ThreadedUdpServer(ThreadPoolMixIn, SocketServer.UDPServer):

    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True, timeout=None, tls=False, key=False, cert=False, ssl_ver = ssl.PROTOCOL_SSLv23):
        SocketServer.UDPServer.__init__(self, server_address, RequestHandlerClass)
        self.socket.settimeout(timeout)
        self.use_tls = tls
        self.timeout = timeout
        if tls:
            self.socket = ssl.wrap_socket(self.socket,
                                          server_side=True,
                                          keyfile=key,
                                          certfile=cert,
                                          cert_reqs=ssl.CERT_NONE,
                                          ssl_version=ssl_ver,
                                          do_handshake_on_connect=False,
                                          suppress_ragged_eofs=True)

    def get_request(self):
        (socket, addr) = SocketServer.UDPServer.get_request(self)
        if self.use_tls:
            socket.settimeout(self.timeout)
            socket.do_handshake()
        return (socket, addr)

class UdpRequestHandlerFactory:
    def produce(self, tcp_server_instance):
        def createHandler(*args, **keys):
            return ThreadedUdpRequestHandler(tcp_server_instance, *args, **keys)
        return createHandler

@ModuleDocstringParser
class UdpServer(BaseModule.BaseModule):
    """
    Reads data from udp socket and sends it to its output queues.

    Configuration template:

    - TcpServerThreaded:
        interface:                       # <default: ''; type: string; is: optional>
        port:                            # <default: 5151; type: integer; is: optional>
        timeout:                         # <default: None; type: None||integer; is: optional>
        tls:                             # <default: False; type: boolean; is: optional>
        key:                             # <default: False; type: boolean||string; is: required if tls is True else optional>
        cert:                            # <default: False; type: boolean||string; is: required if tls is True else optional>
        receivers:
          - NextModule
    """

    module_type = "input"
    """Set module type"""

    def configure(self, configuration):
        # Call parent configure method
        BaseModule.BaseModule.configure(self, configuration)
        self.server = False

    def run(self):
        if not self.receivers:
            self.logger.error("%sShutting down module %s since no receivers are set.%s" % (Utils.AnsiColors.FAIL, self.__class__.__name__, Utils.AnsiColors.ENDC))
            return
        handler_factory = UdpRequestHandlerFactory()
        try:
            self.server = ThreadedUdpServer((self.getConfigurationValue("interface"),
                                             self.getConfigurationValue("port")),
                                             handler_factory.produce(self),
                                             timeout=self.getConfigurationValue("timeout"),
                                             tls=self.getConfigurationValue("tls"),
                                             key=self.getConfigurationValue("key"),
                                             cert=self.getConfigurationValue("cert"))
        except:
            etype, evalue, etb = sys.exc_info()
            self.logger.error("%sCould not listen on %s:%s. Exception: %s, Error: %s%s" % (Utils.AnsiColors.FAIL, self.getConfigurationValue("interface"),
                                                                                            self.getConfigurationValue("port"), etype, evalue, Utils.AnsiColors.ENDC))
            self.gp.shutDown()
            return
        # Start a thread with the server -- that thread will then start one
        # more threads for each request.
        server_thread = threading.Thread(target=self.server.serve_forever)
        # Exit the server thread when the main thread terminates.
        server_thread.daemon = True
        server_thread.start()

    def shutDown(self):
        try:
            self.server.alive = False
        except AttributeError:
            pass