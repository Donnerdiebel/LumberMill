import sys
import os
import io
import gzip
import time
import extendSysPath
import ModuleBaseTestCase
import mock
import tempfile
import Utils
import FileSink


class TestFileSink(ModuleBaseTestCase.ModuleBaseTestCase):

    def setUp(self):
        super(TestFileSink, self).setUp(FileSink.FileSink(gp=mock.Mock()))

    """
    - FileSink:
        file_name:                            # <type: string; is: required>
        format:                               # <default: '%(data)s'; type: string; is: optional>
        store_interval_in_secs:               # <default: 10; type: integer; is: optional>
        batch_size:                           # <default: 500; type: integer; is: optional>
        backlog_size:                         # <default: 5000; type: integer; is: optional>
        compress:                             # <default: None; type: None||string; values: [None,'gzip','snappy']; is: optional>
    """
    def getTempFileName(self):
        temp_file = tempfile.NamedTemporaryFile()
        temp_file_name = temp_file.name
        temp_file.close()
        return temp_file_name

    def deleteTempFile(self, temp_file_name):
        try:
            os.remove(temp_file_name)
        except:
            etype, evalue, etb = sys.exc_info()
            self.logger.error('Could no delete temporary file %s. Excpeption: %s, Error: %s.' % (temp_file_name, etype, evalue))
            sys.exit(255)

    def inflateGzipData(self, data):
        buffer = io.BytesIO(data)
        compressor = gzip.GzipFile(mode='rb', fileobj=buffer)
        try:
            inflated_data = compressor.read()
        except:
            inflated_data = None
        return inflated_data

    def test(self):
        temp_file_name = self.getTempFileName()
        self.test_object.configure({'file_name': temp_file_name,
                                    'store_interval_in_secs': 1})
        self.checkConfiguration()
        event = Utils.getDefaultEventDict({'data': 'One thing is for sure; a sheep is not a creature of the air.'})
        self.test_object.receiveEvent(event)
        self.test_object.shutDown()
        with open(temp_file_name) as temp_file:
            for line in temp_file:
                self.assertEquals(line.rstrip(), event['data'])
        self.deleteTempFile(temp_file_name)

    def testGzipCompression(self):
        temp_file_name = self.getTempFileName()
        self.test_object.configure({'file_name': temp_file_name,
                                    'store_interval_in_secs': 1,
                                    'compress': 'gzip'})
        self.checkConfiguration()
        event = Utils.getDefaultEventDict({'data': 'One thing is for sure; a sheep is not a creature of the air.'})
        self.test_object.receiveEvent(event)
        self.test_object.shutDown()
        with open("%s.gz" % temp_file_name) as temp_file:
            for line in temp_file:
                defalted_data = self.inflateGzipData(line)
                self.assertIsNotNone(defalted_data)
                self.assertEquals(defalted_data.rstrip(), event['data'])
        self.deleteTempFile("%s.gz" % temp_file_name)