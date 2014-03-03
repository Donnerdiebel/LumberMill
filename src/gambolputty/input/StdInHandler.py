# -*- coding: utf-8 -*-
import sys
import socket
import Utils
import BaseThreadedModule
from Decorators import ModuleDocstringParser

@ModuleDocstringParser
class StdInHandler(BaseThreadedModule.BaseThreadedModule):
    """
    Reads data from stdin and sends it to its output queues.

    Configuration example:

    - StdInHandler:
        multiline:                     # <default: False; type: boolean; is: optional>
        stream_end_signal:             # <default: False; type: boolean||string; is: optional>
        receivers:
          - NextModule
    """

    module_type = "input"
    """Set module type"""
    can_run_parallel = False

    def configure(self, configuration):
        BaseThreadedModule.BaseThreadedModule.configure(self, configuration)
        self.multiline = self.getConfigurationValue('multiline')
        self.stream_end_signal = self.getConfigurationValue('stream_end_signal')

    def run(self, input=sys.stdin):
        if not self.receivers:
            self.logger.error("%sWill not start module %s since no receivers are set.%s" % (Utils.AnsiColors.FAIL, self.__class__.__name__, Utils.AnsiColors.ENDC))
            return
        hostname = socket.gethostname()
        multiline_data = ""
        while self.alive:
            data = input.readline()
            if data.__len__() > 0:
                if not self.multiline:
                    self.sendEvent(Utils.getDefaultEventDict({"received_from": 'stdin://%s' % hostname, "data": data}, caller_class_name=self.__class__.__name__))
                else:
                    if self.stream_end_signal and self.stream_end_signal == data:
                        self.sendEvent(Utils.getDefaultEventDict({"received_from": 'stdin://%s' % hostname, "data": multiline_data}, caller_class_name=self.__class__.__name__))
                        multiline_data = ""
                        continue
                    multiline_data += data
            else: # an empty line means stdin has been closed
                if multiline_data.__len__() > 0:
                    self.sendEvent(Utils.getDefaultEventDict({"received_from": 'stdin://%s' % hostname, "data": multiline_data}, caller_class_name=self.__class__.__name__))
                self.gp.shutDown()
                self.alive = False