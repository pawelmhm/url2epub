from urlparse import urljoin, urlparse
import sys
from epub_writer import EpubWriter
from helpers import request_get
from optparse import OptionParser
from lxml import etree, html

from twisted.python import log

from twisted.internet import protocol, utils, reactor
from twisted.internet.defer import DeferredList, inlineCallbacks, Deferred


class WebpageGetter(object):
    def __init__(self, url):
        self.url = url

    def download(self, *args, **kwargs):
        req = request_get(self.url)
        req.addCallback(self.parse_stylesheets)
        req.addErrback(self.handle_error)
        return req

    def parse_stylesheets(self, response):
        response_html = html.fromstring(response)
        stylesheets = response_html.xpath("//link[@rel='stylesheet']/@href")
        dfd_list = []
        for sheet in stylesheets:
            sheet_url = urljoin(self.url, sheet)
            req = request_get(sheet_url)
            req.addErrback(self.handle_error)
            dfd_list.append(req)

        dfd_list = DeferredList(dfd_list)
        dfd_list.addCallback(self.stylesheets_done, response)
        return dfd_list

    def stylesheets_done(self, styles, response):
        styles = [stl[1] for stl in styles]
        styles = "\n".join(styles)
        title_xpath  = """
            //title//text()
                |
            //h1//text()
                |
            //h2//text()
        """
        sel = html.fromstring(response)
        title = sel.xpath(title_xpath)
        if title:
            title = title[0]
        else:
            title = urlparse(self.url).netloc
            title = title.replace("www.", "")
        title = "".join(title)
        html_dict = {
            "title": title,
            "response": response,
            "stylesheets": styles
        }

        writer = EpubWriter()
        writer.write_epub(html_dict)

    def handle_error(self, failure):
        log.err(failure)

class SerialDownloader(object):
    def __init__(self, urls):
        self.urls = urls

    def download_urls(self):
        dfd_list = []
        for url in self.urls:
            getter = WebpageGetter(url)
            dfd = getter.download()
            dfd_list.append(dfd)

        dfd_list = DeferredList(dfd_list)
        dfd_list.addCallback(self.write_epub)

    def write_epub(self, responses):
        pass


def main():
    usage = "usage url2epub url"
    parser = OptionParser(usage=usage)
    (options, args) = parser.parse_args()
    if not args:
        parser.error("url must be supplied")

    log.startLogging(sys.stdout)
    url = args[0]
    # serial = SerialDownloader(urls)
    # serial.download_urls()
    webpageGetter = WebpageGetter(url)
    webpageGetter.download()
    reactor.run()

if __name__ == "__main__":
    main()
