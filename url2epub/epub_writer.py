import zipfile
import os
from lxml import etree, html
import hashlib
from datetime import datetime
from twisted.internet import reactor

from templates import container, package_opf, mimetype, nav

class EpubWriter(object):
    def prepare_navs(self, html_docs):
        navs = etree.fromstring(nav)
        for doc in html_docs:
            for elem in navs.iter():
                if elem.attrib.get("id") == "content_list":
                    li = etree.Element('li')
                    a = etree.Element('a')
                    a.text = html_docs[doc][0]
                    a.set("href", doc)
                    li.append(a)
                    elem.append(li)

        return etree.tostring(navs, pretty_print=True)

    def prepare_package(self, html_docs):
        date = datetime.now().isoformat()
        title = "Hacker News at {}".format(date)
        creator = " ".join(os.uname()[:2])
        package = package_opf.format(title=title, date=date, creator=creator)
        pack = etree.fromstring(package)
        for doc in html_docs:
            # write each one to xml
            id_id = "id-id{0}".format(doc)
            for elem in pack.iter():
                if elem.tag == "{http://www.idpf.org/2007/opf}manifest":
                    item = etree.Element('item')
                    item.set("href", doc)
                    item.set("id", id_id)
                    item.set("media-type", "application/xhtml+xml")
                    elem.append(item)
                    item = etree.Element('item')
                    item.set('media-type', 'text/css')
                    item.set("id", "id-{}".format(self.css_id(doc)))
                    item.set("href", 'css/{}'.format(self.css_id(doc)))
                    elem.append(item)
                elif elem.tag == "{http://www.idpf.org/2007/opf}spine":
                    itemref = etree.Element('itemref')
                    itemref.set('idref', id_id)
                    elem.append(itemref)
        pack = etree.tostring(pack)
        return pack

    def prepare_titles(self, html_docs):
        """
        :return dict with hash of contents as key,
        """
        _html_docs = {}
        for doc in html_docs:
            sel = html.document_fromstring(doc.get("response"))
            for elem in sel.iter():
                if elem.tag == 'script':
                    elem.getparent().remove(elem)

            doc_content = "".join(sel.xpath(".//text()"))
            doc_ascii = doc_content.encode('ascii','ignore')
            id_ = hashlib.sha224(doc_ascii).hexdigest()
            title = doc.get("title")
            head = sel.xpath("//head")[0]
            elem = etree.Element('link')
            elem.set("rel", "stylesheet")
            elem.set("href", 'css/{}'.format(self.css_id(id_)))
            elem.set("type", "text/css")
            head.append(elem)
            response = etree.tostring(sel)
            _html_docs[id_] = (title, response, doc.get("stylesheets"))

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
        nav = self.prepare_navs(html_docs)
        package_opf = self.prepare_package(html_docs)
        with zipfile.ZipFile('example/example.epub','w') as f:
            f.writestr('mimetype', mimetype)
            f.writestr('EPUB/package.opf', package_opf.strip())
            f.writestr('META-INF/container.xml', container.strip())
            f.writestr('EPUB/navs.xhtml', nav)
            for doc in html_docs:
                f.writestr('EPUB/{0}'.format(doc), html_docs[doc][1])
                f.writestr('EPUB/css/{}'.format(self.css_id(doc)), html_docs[doc][2])
        reactor.stop()


if __name__ == "__main__":
    wr = EpubWriter()
    wr.write_epub((html1, html2))
