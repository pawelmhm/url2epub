import time

from twisted.trial import unittest
from twisted.python import log
from lxml import etree

from url2epub.epub_writer import PackageOpf

class TestPackage(unittest.TestCase):
    def setUp(self):
        self.pack = PackageOpf("title here", time.time(), "pawelmhm")
        self.item_data = {
            "href": "http://foo",
            "id": str(abs(hash("hello"))),
            "media-type": "text/plain"
        }

    def test_package_created(self):
        self.assertIsNotNone(self.pack)

    def test_item_added_to_manifest(self):
        self.pack.add_item_to_manifest(self.item_data)
        self.assertIn(self.item_data["id"], etree.tostring(self.pack.manifest))
        item_data2 = {
            "href": "/style/css/foo",
            "id": str(abs(hash("helloworld"))),
            "media_type": "text/css"
        }
        self.pack.add_item_to_manifest(item_data2)
        self.assertIn(item_data2["id"], etree.tostring(self.pack.manifest))
        self.assertIn(self.item_data["id"], etree.tostring(self.pack.manifest))

    def test_add_item_to_spine(self):
        self.pack.add_item_to_spine(self.item_data)
        item_in_spine = self.pack.spine.xpath("//*[@idref={}]".format(self.item_data["id"]))
        self.assertTrue(bool(item_in_spine))

