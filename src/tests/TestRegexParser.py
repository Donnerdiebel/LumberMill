import extendSysPath
import unittest
import ModuleBaseTestCase
import mock
import Queue
import Utils
import RegexParser

class TestRegexParser(ModuleBaseTestCase.ModuleBaseTestCase):

    raw_data= '192.168.2.20 - - [28/Jul/2006:10:27:10 -0300] "GET /cgi-bin/try/ HTTP/1.0" 200 3395'

    def setUp(self):
        super(TestRegexParser, self).setUp(RegexParser.RegexParser(gp=mock.Mock()))

    def testHandleEvent(self):
        self.test_object.configure({'source_field': 'event',
                                    'field_extraction_patterns': {'http_access_log': '(?P<remote_ip>\d+\.\d+\.\d+\.\d+)\s+(?P<identd>\w+|-)\s+(?P<user>\w+|-)\s+\[(?P<datetime>\d+\/\w+\/\d+:\d+:\d+:\d+\s.\d+)\]\s+\"(?P<url>.*)\"\s+(?P<http_status>\d+)\s+(?P<bytes_send>\d+)'}})
        result = self.conf_validator.validateModuleInstance(self.test_object)
        self.assertFalse(result)
        event = Utils.getDefaultEventDict({'event': self.raw_data})
        self.test_object.handleEvent(event)
        for event in self.receiver.getEvent():
            self.assert_('bytes_send' in event and event['bytes_send'] == '3395')

    def __testQueueCommunication(self):
        self.test_object.configure({'field_extraction_patterns': {'http_access_log': '(?P<remote_ip>\d+\.\d+\.\d+\.\d+)\s+(?P<identd>\w+|-)\s+(?P<user>\w+|-)\s+\[(?P<datetime>\d+\/\w+\/\d+:\d+:\d+:\d+\s.\d+)\]\s+\"(?P<url>.*)\"\s+(?P<http_status>\d+)\s+(?P<bytes_send>\d+)'}})
        result = self.conf_validator.validateModuleInstance(self.test_object)
        self.assertFalse(result)
        self.test_object.start()
        self.input_queue.put(Utils.getDefaultEventDict({}))
        queue_emtpy = False
        try:
            self.output_queue.get(timeout=1)
        except Queue.Empty:
            queue_emtpy = True
        self.assert_(queue_emtpy != True)

    def __testQueueCommunication(self):
        config = {'field_extraction_patterns': {'http_access_log': '(?P<remote_ip>\d+\.\d+\.\d+\.\d+)\s+(?P<identd>\w+|-)\s+(?P<user>\w+|-)\s+\[(?P<datetime>\d+\/\w+\/\d+:\d+:\d+:\d+\s.\d+)\]\s+\"(?P<url>.*)\"\s+(?P<http_status>\d+)\s+(?P<bytes_send>\d+)'}}
        super(TestRegexParser, self).testQueueCommunication(config)

    def __testOutputQueueFilterNoMatch(self):
        config = {'field_extraction_patterns': {'http_access_log': '(?P<remote_ip>\d+\.\d+\.\d+\.\d+)\s+(?P<identd>\w+|-)\s+(?P<user>\w+|-)\s+\[(?P<datetime>\d+\/\w+\/\d+:\d+:\d+:\d+\s.\d+)\]\s+\"(?P<url>.*)\"\s+(?P<http_status>\d+)\s+(?P<bytes_send>\d+)'}}
        super(TestRegexParser, self).testOutputQueueFilterNoMatch(config)

    def __testOutputQueueFilterMatch(self):
        config = {'field_extraction_patterns': {'http_access_log': '(?P<remote_ip>\d+\.\d+\.\d+\.\d+)\s+(?P<identd>\w+|-)\s+(?P<user>\w+|-)\s+\[(?P<datetime>\d+\/\w+\/\d+:\d+:\d+:\d+\s.\d+)\]\s+\"(?P<url>.*)\"\s+(?P<http_status>\d+)\s+(?P<bytes_send>\d+)'}}
        super(TestRegexParser, self).testOutputQueueFilterMatch(config)

    def __testWorksOnOriginal(self):
        config = {'field_extraction_patterns': {'http_access_log': '(?P<remote_ip>\d+\.\d+\.\d+\.\d+)\s+(?P<identd>\w+|-)\s+(?P<user>\w+|-)\s+\[(?P<datetime>\d+\/\w+\/\d+:\d+:\d+:\d+\s.\d+)\]\s+\"(?P<url>.*)\"\s+(?P<http_status>\d+)\s+(?P<bytes_send>\d+)'}}
        super(TestRegexParser, self).testWorksOnOriginal(config)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()