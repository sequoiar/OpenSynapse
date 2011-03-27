#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenSynapse, Umut Aydin(MrGoodbyte), Copyright (c) 2011
    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
    sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
    FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
    WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from config import *

import random
import time
import ujson
import uuid

def protocolHandler(socket, address):
    handler = socket.makefile()

    while True:
        try:
            line = handler.readline()
            if not line:
                drop(handler)
                break # client disconnected

            # {"c":"cll", "p":{"n":"cache-get", "d":{"k":"my-key"}}}
            # {"c":"cll", "p":{"n":"cache-set", "d":{"k":"my-key", "v":"Hello World!"}}}
            request = ujson.decode(line) # ultrajson parser
            if request.has_key('c') and request.has_key('p'): # command, parameter
                # switch by command
                if   request.get('c') == 'reg': # registration
                    response = register(request.get('p'), handler)

                elif request.get('c') == 'cll': # task call
                    if request.has_key('b') and request.get('b'):
                        response = call(request.get('p'), None) # background
                    else:
                        response = call(request.get('p'), handler) # regular by default

                elif request.get('c') == 'rsp': # response
                    response = responseHandler(request.get('p'))

                else:
                    response = None
                # switch by command

                if response != None:
                    handler.write("%s\r\n" % response)
                    handler.flush()
            else:
                handler.write("%s\r\n" % '{"e":2,"r":""}') # missing parameters(c:command, p:parameters)
                handler.flush()
        except Exception as e:
            handler.write("%s\r\n" % '{"e":1,"r":""}') # global error
            handler.flush()

"""
@param  Object parameters: request
@param  handler: socket handler
This method handles task registration process and returns amount of tasks
"""
def register(parameters, handler):
    if parameters.has_key('n'):
        if parameters.has_key('k') and parameters.get('k'):
            byKey = True
        else:
            byKey = False

        if not TASKS.has_key(parameters.get('n')):
            TASKS[parameters.get('n')] = {
                'k': byKey,
                't': []
            }

        TASKS.get(parameters.get('n')).get('t').append(handler)
        return '{"e":0,"r":%s}' % len(TASKS.get(parameters.get('n')).get('t'))
    else:
        return '{"e":2,"r":""}' # missing parameter(n:name)

"""
@param  socket: connection handler
This method removes a task socket from lists(tasks / requests)
"""
def drop(socket):
    for task in TASKS:
        for handler in TASKS.get(task).get('t'):
            if socket in TASKS.get(task).get('t'):
                TASKS.get(task).get(t).remove(socket)

        if len(TASKS.get(task).get('t')) == 0:
            del TASKS[task]

    for req in REQUESTS:
        if socket == REQUESTS.get(req).get('s'):
            del REQUESTS[req]

"""
@param  Object parameters: request
This method handles task response and returns the data to client socket if requested
"""
def responseHandler(parameters):
    if parameters.has_key('uuid') and parameters.has_key('v'):
        if REQUESTS.has_key(parameters.get('uuid')):
            REQUESTS.get(parameters.get('uuid')).get('s').write("%s\r\n" % ('{"e":0,"r":%s}' % ujson.encode(parameters.get('v'))))
            REQUESTS.get(parameters.get('uuid')).get('s').flush()

            STATS['process'] += 1
            STATS['time'] = ((STATS['time'] * STATS['process']) + (int(time.time()) - REQUESTS.get(parameters.get('uuid')).get('t'))) / STATS['process']
            del REQUESTS[parameters.get('uuid')]

    return None

"""
@param  Object parameters: request
@param  Boolean background: background or regular call
@param  socket: connection handler
This method calls a task (local / remote)
"""
def call(parameters, socket):
    if parameters.has_key('n'):
        if parameters.has_key('d'):
            data = parameters.get('d')
        else:
            data = {}

        if data.has_key('k'):
            key = data.get('k')
        else:
            key = None

        if TASKS.has_key(parameters.get('n')): # local task
            handler = select(parameters.get('n'), key)
            if socket != None:
                id = str(uuid.uuid1())
                REQUESTS[id] = {
                    's': socket,
                    't': int(time.time())
                }
            else:
                id = None

            handler.write("%s\r\n" % ('{"n":"%s","uuid":"%s","p":%s}' % (parameters.get('n'), id, ujson.encode(data))))
            handler.flush()
            STATS['global'] += 1
            return None

        else:
            return '{"e":3,"r":""}' # there is no task
    else:
        return '{"e":2,"r":""}' # missing parameter(n:name)

"""
@param  String key: key parameter
This method converts given key to an integer value
"""
def calculate(key):
    val = 0
    for c in key:
        val += ord(c)

    return val

"""
@param  String name: task name
@param  String key: key parameter
This method returns a socket handler
"""
def select(name, key):
    if TASKS.get(name).get('k') and (key != None):
        val = calculate(key)
        return TASKS.get(name).get('t')[val % len(TASKS.get(name).get('t'))]
    else:
        return random.sample(TASKS.get(name).get('t'), 1)[0]







