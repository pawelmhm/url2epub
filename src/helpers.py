from treq import get

from twisted.python import log

def request_get(url, load_json=False):
    log.msg("sending request to url %s" % url)
    dfd = get(url)

    def done(response):
        if load_json:
            dfd = response.json()
        else:
            dfd = response.content()
        return dfd

    dfd.addCallback(done)
    return dfd
