import zipfile
import os
from lxml import etree, html
import hashlib
from datetime import datetime
from twisted.internet import reactor
from twisted.python import log
from ebooklib import epub

from templates import (container, package_root, mimetype,
                       nav, package_manifest, package_spine)


class EpubWriter(object):
    def write_epub(self, doc):
        """html_docs - list of dictionaries with following keys:
        title, responses (html), stylesheets
        """
        book = epub.EpubBook()
        # TODO
        book.add_author('Author Authorowski')
        sel = html.document_fromstring(doc.get("response"))
        content = doc.get('response')

        # TODO lxml.htmlcleaner
        for elem in sel.iter():
            if elem.tag == 'script':
                elem.getparent().remove(elem)

        # TODO
        doc_ascii = content.encode('ascii','ignore')
        hash_id = hashlib.sha224(doc_ascii).hexdigest()
        book.set_identifier(hash_id)
        title = doc.get("title")
        book.set_language('en')
        book.set_title(title)
        # TODO
        c1 = epub.EpubHtml(title='Intro', file_name='chap_01.xhtml', lang='en')
        c1.content = doc.get('response')
        book.add_item(c1)
        book.toc = (epub.Link('chap_01.xhtml', 'Introduction', 'intro'),
             (epub.Section('Simple book'),
             (c1, ))
            )
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        # TODO?
        style = 'BODY {color: white;}'
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
        book.add_item(nav_css)
        book.spine = ['nav', c1]
        # TODO
        epub.write_epub('test.epub', book, {})
        reactor.stop()
