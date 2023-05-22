#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Video streaming Server 1.0
(c) 2016 Jerzy Glowacki
(c) 2022 Yuya Hamamachi
Apache 2.0 License
"""

import server # server.py

# For Socket server
import http.server
import socketserver

import os

#HOST = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT")) if os.environ.get("PORT") is not None else 5900

class testVNCServer(server.VNCServer):
    testFlag = True

if __name__ == '__main__':
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer((HOST, PORT), testVNCServer)
    httpd.allow_reuse_address = True
    print('Server started at http://%s:%s' % (HOST, PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
       pass
    httpd.server_close()
    print('Server stopped')

