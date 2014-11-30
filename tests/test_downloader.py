from twisted.trial import unittest
from twisted.internet.defer import inlineCallbacks, Deferred
from url2epub.core import WebpageGetter
from twisted.internet import reactor

from twisted.web.client import getPage
import twisted

class TestDownloader(unittest.TestCase):
    def setUp(self):
        pass

    def test_download_ok(self):
        pass
