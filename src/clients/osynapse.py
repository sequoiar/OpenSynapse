#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenSynapse Python Client, Umut Aydin(MrGoodbyte), Copyright (c) 2011
    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
    sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
    FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
    WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import socket
import ujson

class OpenSynapse():
    hostname = None
    port = None
    s = None

    def __init__(self, hostname, port):
        self.port = port
        self.hostname = hostname
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        if self.isConnected():
            return True

        try:
            self.s.connect((self.hostname, self.port))
            return True
        except:
            return False

    def close(self):
        try:
            self.s.close()
        except:
            pass

    def send(self, task, parameters):
        if not self.isConnected():
            if not self.connect():
                return False

        try:
            self.s.send("%s\r\n" % ujson.encode({
                'c': 'cll',
                'p': {
                    'n': task,
                    'd': parameters
                }
            }))
            #self.s.makefile.readline()
            return True
        except:
            return False

    def isConnected(self):
        try:
            self.s.getpeername()
            return True
        except:
            return False

if __name__ == "__main__":
    osynapse = OpenSynapse('127.0.0.1', 8688)
    osynapse.connect()
    osynapse.send('cache-set', {'k': 'test', 'v': 'Hello World!'})
    print osynapse.send('cache-get', {'k': 'test'})





