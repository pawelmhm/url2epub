import zipfile
import os
from lxml import etree, html
import hashlib
from datetime import datetime
from twisted.internet import reactor
from twisted.python import log

from templates import (container, package_root, mimetype,
                       nav, package_manifest, package_spine)


class PackageOpf(object):
    def __init__(self, title, date, creator):
        self.manifest = etree.fromstring(package_manifest)
        self.spine = etree.fromstring(package_spine)
        self.root = etree.fromstring(package_root.format(title=title,
                                             date=date,
                                             creator=creator))

    def add_item_to_package(self, item_data):
        """Adds item to manifest and spine, perhaps
        better naming is needed.
        """
        self.add_item_to_spine(item_data)
        self.add_item_to_manifest(item_data)

    def add_item_to_spine(self, item_data):
        itemref = etree.Element('itemref')
        itemref.set('idref', item_data["id"])
        self.spine.append(itemref)

    def add_item_to_manifest(self, item_data):
        item = etree.Element('item')
        for attr in item_data:
            if isinstance(item_data[attr], basestring):
                item.set(attr, item_data[attr])
        self.manifest.append(item)

    def generate_package(self):
        self.root.append(self.manifest)
        self.root.append(self.spine)
        return etree.tostring(self.root)


class EpubWriter(object):
    def prepare_navs(self, html_docs):
        navs = etree.fromstring(nav)
        for doc in html_docs:
            for elem in navs.iter():
                if elem.attrib.get("id") == "content_list":
                    li = etree.Element('li')
                    a = etree.Element('a')
                    a.text = doc["title"]
                    a.set("href", doc["attrs"]["href"])
                    li.append(a)
                    elem.append(li)

        return etree.tostring(navs, pretty_print=True)

    def prepare_package(self, html_docs):
        date = datetime.now().isoformat()
        title = "Hacker News at {}".format(date)
        creator = " ".join(os.uname()[:2])
        pack = PackageOpf(title, date, creator)

        for doc in html_docs:
            pack.add_item_to_package(doc["attrs"])
            for style in doc["stylesheets"]:
                pack.add_item_to_manifest(style["attrs"])
        return pack.generate_package()

    def prepare_titles(self, html_docs):
        """
        :return dict with hash of contents as key,
        """
        _html_docs = []
        for doc in html_docs:
            sel = html.document_fromstring(doc.get("response"))
            for elem in sel.iter():
                if elem.tag == 'script':
                    elem.getparent().remove(elem)

            doc_content = "".join(sel.xpath(".//text()"))
            doc_ascii = doc_content.encode('ascii','ignore')
            id_ = hashlib.sha224(doc_ascii).hexdigest()
            css_id = hashlib.sha224(doc_ascii + "css").hexdigest()
            title = doc.get("title")
            head = sel.xpath("//head")[0]
            elem = etree.Element('link')
            elem.set("rel", "stylesheet")
            elem.set("href", 'css/{}'.format(css_id))
            elem.set("type", "text/css")
            head.append(elem)
            response = etree.tostring(sel)
            _html_docs.append({
                "title": title,
                "response": response,
                "stylesheets": [{
                    "attrs": {
                        "id": "id-" + css_id,
                        "media-type": "text/css",
                        "href": "css/" + css_id,
                        "rel": "stylesheet"
                    },
                    "content": doc.get("stylesheets"),
                }],
                "attrs": {
                    "id": "id-" + id_,
                    "href": id_,
                    "media-type": "application/xhtml+xml"
                }
            })

        return _html_docs

    def css_id(self, id_):
        css_id = "css" + id_
        id_ = hashlib.sha224(css_id).hexdigest()
        return id_

    def write_epub(self, html_docs):
        """html_docs - list of dictionaries with following keys:
        title, responses (html), stylesheets
        """
        html_docs = self.prepare_titles(html_docs)
        package_opf = self.prepare_package(html_docs)
        nav = self.prepare_navs(html_docs)
        self._write_epub(package_opf, nav, html_docs)

    def _write_epub(self, package, nav, html_docs):
        with zipfile.ZipFile('example/example.epub','w') as f:
            f.writestr('mimetype', mimetype)
            f.writestr('EPUB/package.opf', package.strip())
            f.writestr('META-INF/container.xml', container.strip())
            f.writestr('EPUB/navs.xhtml', nav)
            for doc in html_docs:
                f.writestr('EPUB/{0}'.format(doc["attrs"]["href"]), doc["response"])
                for style in doc["stylesheets"]:
                    f.writestr('EPUB/{}'.format(style["attrs"]["href"]),
                                style["content"])
        reactor.stop()
