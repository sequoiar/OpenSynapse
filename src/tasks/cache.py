#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Memory Cache Task Routine for OpenSynapse, Umut Aydin(MrGoodbyte), Copyright (c) 2011
    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
    sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
    FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
    WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from twisted.internet          import reactor
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic   import LineReceiver

import time
import ujson

SERVER = '127.0.0.1'
PORT   = 8688

class SampleWorker(LineReceiver):
    pattern = {'cache-get': 'get', 'cache-set': 'set'}
    byKey   = {'cache-get': True}
    expire  = 3600
    limit   = 500000
    db      = {}

    def connectionMade(self):
        if len(self.pattern):
            for job in self.pattern:
                if self.byKey.has_key(job) and self.byKey.get(job):
                    self.transport.write("%s\r\n" % ujson.encode({
                        'c': 'reg',
                        'p': {'n': job, 'k': True}
                    }));
                else:
                    self.transport.write("%s\r\n" % ujson.encode({
                        'c': 'reg',
                        'p': {'n': job, 'k': False}
                    }));

    def lineReceived(self, line):
        data = line.strip()
        if len(data) > 0:
            try:
                data = ujson.decode(data)
                if data.has_key('n') and self.pattern.has_key(data.get('n')):
                    response = getattr(self, self.pattern.get(data.get('n')))(data.get('uuid'), data.get('p'))
                    if response != None:
                        self.transport.write("%s\r\n" % ujson.encode(response))
            except:
                pass

    def get(self, id, data):
        if id != None:
            if data.has_key('k') and self.db.has_key(data.get('k')):
                if (int(time.time()) - self.db.get(data.get('k')).get('c')) < self.db.get(data.get('k')).get('e'):
                    return {
                        'c': 'rsp',
                        'p': {
                            'v': self.db.get(data.get('k')).get('v'),
                            'uuid': id
                        }
                    }
                else: # delete record if expired
                    del self.db[data.get('k')]

            return {
                'c': 'rsp',
                'p': {
                    'v': None,
                    'uuid': id
                }
            }

        return None

    def set(self, id, data):
        if len(self.db) < self.limit:
            if data.has_key('k') and data.has_key('v'):
                if data.has_key('e'):
                    expire = data.get('e')
                else:
                    expire = self.expire

                self.db[data.get('k')] = {
                    'c': int(time.time()),
                    'e': expire,
                    'v': data.get('v')
                }

        return None

class SampleWorkerFactory(ClientFactory):
    protocol = SampleWorker

    def clientConnectionFailed(self, connector, reason):
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        reactor.stop()

try:
    factory = SampleWorkerFactory()
    reactor.connectTCP(SERVER, PORT, factory)
    reactor.run()
except:
    pass