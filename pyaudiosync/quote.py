import json
import ssl
import urllib.request

import errors

QUOTE_URL = "https://dummyjson.com/quotes/random"


def _ssl_context():
    # Android's Python has no system CA store, so use certifi's bundle
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def get_quote():
    try:
        req = urllib.request.Request(QUOTE_URL, headers={"User-Agent": "PyAudioSync"})
        with urllib.request.urlopen(req, timeout=5, context=_ssl_context()) as res:
            data = json.loads(res.read().decode("utf-8"))
        print(data)
    except Exception:
        errors.error("Could not receive quote (Are you connected to the internet?)")
        data = {
            "quote": "Could not receive quote (Are you connected to the internet?)",
            "author": "",
        }
    return data