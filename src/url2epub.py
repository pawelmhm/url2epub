import sys
from epub_writer import EpubWriter
from helpers import request_get
from optparse import OptionParser
from lxml import etree, html

from twisted.python import log

from twisted.internet import protocol, utils, reactor
from twisted.internet.defer import DeferredList, inlineCallbacks, Deferred


class EpubSpider(object):
    def __init__(self, url):
        self.url = url

    def download(self, *args, **kwargs):
        req = request_get(self.url)
        req.addCallback(self.parse_stylesheets)
        return req

    def parse_stylesheets(self, response):
        response_html = html.fromstring(response)
        stylesheets = response_html.xpath("//link[@rel='stylesheet']/@href")
        dfd_list = []
        for sheet in stylesheets:
            req = request_get(sheet)
            dfd_list.append(req)

        dfd_list = DeferredList(dfd_list)
        dfd_list.addCallback(self.stylesheets_done, response)
        return dfd_list

    def stylesheets_done(self, styles, response):
        styles = [stl[1] for stl in styles]
        styles = "\n".join(styles)
        # TODO add stylesheet to HEAD here
        htmls = [{
            "title": "foo bar",
            "response": response,
            "stylesheets": styles
        }
        ]
        writer = EpubWriter()
        writer.write_epub(htmls)


def main():
    usage = "usage url2epub url"
    parser = OptionParser(usage=usage)
    (options, args) = parser.parse_args()
    if not args:
        parser.error("url must be supplied")

    # log.startLogging(sys.stdout)
    url = args[0]
    spider = EpubSpider(url)
    spider.download()
    reactor.run()

if __name__ == "__main__":
    main()
