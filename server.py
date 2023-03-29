#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Video streaming Server 1.0
(c) 2016 Jerzy Glowacki
(c) 2022 Yuya Hamamachi
Apache 2.0 License
"""

# For Socket server
import http.server
import socketserver
import socket
import os
import cv2

#HOST = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
HOST = "0.0.0.0"
PORT = 5900
QUALITY = 50
ROTATE = False
GRAYSCALE = False
RESIZE = True
OPTIMIZE = False
W = 640
H = 480
X = 0
Y = 0
CAM_NUM = 0
cap = cv2.VideoCapture(CAM_NUM)

class VNCServer(http.server.SimpleHTTPRequestHandler):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

    def getFrame(self):
        _, output = cap.read()
        if GRAYSCALE:
            output = cv2.cvtColor(output,cv2.COLOR_RGB2GRAY)
        if ROTATE:
            output = cv2.rotate(output, cv2.ROTATE_90_CLOCKWISE)
        if RESIZE:
            output = cv2.resize(output, dsize=(W,H) )
        return output

    def do_GET(self):
        self.path = self.path.split('?')[0]
        if self.path == '/frame.jpg':
            cv_img = self.getFrame()
            self.send_response(200)
            self.send_header('Content-Type', 'image/jpeg')
            self.end_headers()
            _, enimg = cv2.imencode('.jpg', cv_img, (cv2.IMWRITE_JPEG_QUALITY, QUALITY))
            self.wfile.write(enimg)
        elif self.path == '/frame.bmp':
            cv_img = self.getFrame()
            self.send_response(200)
            self.send_header('Content-Type', 'image/bmp')
            self.end_headers()
            _, enimg = cv2.imencode('.bmp', cv_img)
            self.wfile.write(enimg)
        else:
            http.server.SimpleHTTPRequestHandler.do_GET(self)

if __name__ == '__main__':
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer((HOST, PORT), VNCServer)
    httpd.allow_reuse_address = True
    print('Kindle VNC Server started at http://%s:%s' % (HOST, PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
       pass
    httpd.server_close()
    print('Server stopped')

