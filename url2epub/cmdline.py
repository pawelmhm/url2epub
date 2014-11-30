import sys
from optparse import OptionParser
from twisted.python import log
from twisted.internet import reactor

from core import WebpageGetter

def execute():
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

