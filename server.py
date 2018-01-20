#!/usr/bin/python

import trust
import users

from tornado import ioloop, web, template
from tornado.httpserver import HTTPServer

application = web.Application([
    (r"/users", users.List),
    (r"/users/([0-9]+)", users.Edit),
    (r"/(.*)", web.StaticFileHandler, {'path': 'static/'}),
], debug=True)

if __name__ == '__main__':
    http = HTTPServer(
            application,
            ssl_options = {
                'certfile': trust.cert_file,
                'keyfile': trust.key_priv
            }
    )
    http.listen(443)
    ioloop.IOLoop.current().start()
