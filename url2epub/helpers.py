from treq import get
from twisted.python import log

def request_get(url, load_json=False):
    log.msg("sending request to url %s" % url)
    headers = {
            "user-agent": "Mozilla/5.0 (Linux; U; Android 2.2; en-us; SCH-I800 Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"}
    dfd = get(url, headers=headers)

    def done(response):
        if load_json:
            dfd = response.json()
        else:
            dfd = response.content()
        return dfd

    dfd.addCallback(done)
    return dfd
