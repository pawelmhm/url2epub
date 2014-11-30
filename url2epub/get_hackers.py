import sys
from treq import get
from twisted.internet import reactor
from twisted.internet.defer import DeferredList, inlineCallbacks, Deferred
from twisted.internet.protocol import ProcessProtocol
from twisted.python import log
from twisted.internet import protocol, utils, reactor
import json

from epub_writer import EpubWriter
from helpers import request_get

class NewsGetter(object):
    def main(self):
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        dfd = request_get(url, load_json=True)
        dfd.addCallback(self.parse_stories)
        dfd.addErrback(self.log_error)
        return dfd

    def parse_stories(self, stories):
        log.msg("parsing stories")
        url = 'https://hacker-news.firebaseio.com/v0/item/{0}.json'
        req_list = []

        for id_ in stories[:30]:
            req = request_get(url.format(id_), load_json=True)
            req.addCallback(self.follow_link)
            req_list.append(req)

        dfd_list = DeferredList(req_list)
        dfd_list.addCallback(self.return_all)
        return dfd_list

    def follow_link(self, response):
        url = response.get("url")
        url = str(url)
        dfd = request_get(url)
        dfd.addCallback(self.add_metadata, response)
        return dfd

    def add_metadata(self, response, api_response):
        html_docs = {
            # "id": api_response.get("id"),
            "title": api_response.get("title"),
            # "score": api_response.get("score"),
            "response": response,
            "stylesheets": []
        }
        return html_docs

    def return_all(self, responses):
        htmls = [tup[1] for tup in responses]
        writer = EpubWriter()
        writer.write_epub(htmls)
        reactor.stop()

    def log_error(self, exception):
        log.err(exception)

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    api = NewsGetter()
    api.main()
    reactor.run()
