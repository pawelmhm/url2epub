import sys
from treq import get
from twisted.internet import reactor
from twisted.internet.defer import DeferredList, inlineCallbacks, Deferred
from twisted.internet.protocol import ProcessProtocol
from twisted.python import log
import json

class EpubConvert(ProcessProtocol):
    data = ""

    def __init__(self, input_html):
        self.html = input_html

    def connectionMade(self):
        self.transport.writeToChild(0, self.html)
        self.transport.closeChildFD(0)

    def outReceived(self, data):
        log.msg("receiving data")
        self.data += data

    def errReceived(self, data):
        log.msg("error received %s" % data)
        self.data += data

    def processEnded(self, reason):
        if reason.value.exitCode == 1:
            reason.trap()
        else:
            self.deferred.callback(self.data)

class NewsGetter(object):
    def main(self):
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        dfd = self.request_get(url)
        dfd.addCallback(self.parse_stories)
        dfd.addErrback(self.log_error)
        return dfd

    @inlineCallbacks
    def parse_stories(self, stories):
        log.msg("parsing stories")
        url = 'https://hacker-news.firebaseio.com/v0/item/{0}.json'
        req_list = []

        for id_ in stories[:5]:
            req = self.request_get(url.format(id_))
            req.addCallback(self.follow_link)
            req_list.append(req)
            yield req
            break

        dfd_list = DeferredList(req_list)
        dfd_list.addCallback(self.return_all)
        yield dfd_list

    @inlineCallbacks
    def follow_link(self, response):
        url = response.get("url")
        url = str(url)
        dfd = self.request_get(url)
        dfd.addCallback(self.save_response)
        yield dfd

    def save_response(self, response):
        dfd = response.content()
        dfd.addCallback(self.print_html)
        return dfd

    def return_all(self, responses):
        pass

    def done(self, response):
        dfd = response.content()
        dfd.addCallback(self.print_response)
        dfd.addErrback(self.return_html, response)
        return dfd

    def print_response(self, response):
        return json.loads(response)

    @inlineCallbacks
    def print_html(self, response):
        epub_convert = EpubConvert(response)
        epub_convert.deferred = Deferred()
        epub_convert.deferred.addBoth(self.finish_all)
        # log.msg("first x chars of response %s" % response[:100])
        reactor.spawnProcess(epub_convert, 'pandoc',
                             ['pandoc', '-f','html', '-o','some_file.epub'])
        yield epub_convert.deferred

    def finish_all(self, data):
        log.msg("ending_process")
        with open('local.epub','w') as f:
            f.write(data)
        reactor.stop()

    def return_html(self, exception, response):
        return response

    def request_get(self, url):
        log.msg("sending request to url %s" % url)
        dfd = get(url)
        dfd.addCallback(self.done)
        return dfd

    def log_error(self, exception):
        log.err(exception)

if __name__ == "__main__":

    log.startLogging(sys.stdout)
    api = NewsGetter()
    api.main()
    reactor.run()
