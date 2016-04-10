from __future__ import print_function
import requests
from requests.auth import HTTPBasicAuth
import posixpath
from StringIO import StringIO
import json
import time


class ClientBase(object):
    def __init__(self, repo, username, password):
        self.username = username
        self.password = password
        self.repo = repo
        if not self.repo.startswith("/"):
            self.repo = "/" + self.repo

    log_requests = True

    def _with_retries(self, fn, *arg, **kw):
        for retry in range(3):
            try:
                ret = fn(*arg, **kw)
            except IOError as err:
                self._output(
                    "Got error %s, sleeping for 5 then "
                    "retrying for %d" % (err, retry))
                time.sleep(5)
            else:
                if ret.status_code >= 300:
                    raise Exception("did not get 200 status: %s" % ret.text)
                else:
                    return json.loads(ret.text)

    def _get(self, path, headers=None):
        url = self._url(path)
        if self.log_requests:
            self._output("GET %s" % url)
        return self._with_retries(
            requests.get,
            url, headers=headers,
            auth=HTTPBasicAuth(self.username, self.password)
        )

    def _put(self, path, data=None, headers=None):
        url = self._url(path)
        if self.log_requests:
            self._output("PUT %s" % url)
        return self._with_retries(
            requests.put,
            url, data=data,
            headers=headers,
            auth=HTTPBasicAuth(self.username, self.password)
        )

    def _post(self, path, data=None, headers=None, as_json=False):
        url = self._url(path)
        if self.log_requests:
            self._output("POST %s" % url)
        return self._with_retries(
            requests.post,
            url, data=json.dumps(data) if as_json else data,
            headers=headers,
            auth=HTTPBasicAuth(self.username, self.password)
        )

    def _patch(self, path, data=None, headers=None, as_json=False):
        url = self._url(path)
        if self.log_requests:
            self._output("PATCH %s" % url)
        return self._with_retries(
            requests.patch,
            url, data=json.dumps(data) if as_json else data,
            headers=headers,
            auth=HTTPBasicAuth(self.username, self.password)
        )

    def _url(self, path):
        if not path.startswith("/"):
            raise ValueError("relative urls aren't supported...")

        dirname, file_ = posixpath.split(path)
        self.relative_to = dirname

        if path.startswith("/"):
            path = path[1:]
        return posixpath.join(self.base_url, path)

    def _output(self, msg):
        if isinstance(msg, unicode):
            msg = msg.encode('ascii', errors='ignore')
        print(msg)

    def _paged_iterator(self, uri):
        start = 0
        while True:
            to_get = uri + "?start=%d&limit=50" % start
            response = self._get(to_get)
            struct = json.loads(response.text)
            yield struct

            start += 50

