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
import sys
import cv2

#HOST = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT")) if os.environ.get("PORT") is not None else 5900
QUALITY = 50
ROTATE = False
GRAYSCALE = False
RESIZE = False
OPTIMIZE = False
W = 640
H = 480
X = 0
Y = 0
CAM_NUM = 0

cap = cv2.VideoCapture(CAM_NUM)

# FPS related variables
SHOW_FPS_FLAG = True
counter = 0
prev_sec = 0
sec = 0
prev_fps = 0

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
        if SHOW_FPS_FLAG is True:
            # Write FPS in frame
            global prev_fps
            output_text = [
                    "FPS: {}".format(prev_fps)
            ]
            text_color = (0,255,0) #( B,G,R ) => Green
            for idx, text in enumerate(output_text):
                text_scale = 2
                xoffset = 20
                yoffset = (idx+1) * 50*text_scale
                font = cv2.FONT_HERSHEY_SIMPLEX
                thickness = 2
                cv2.putText(output, text, (xoffset, yoffset)
                        ,font ,text_scale ,text_color ,thickness ,cv2.LINE_AA)
        return output

    def do_GET(self):
        global counter
        global prev_sec
        global prev_fps
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
        elif self.path == '/frame.png':
            cv_img = self.getFrame()
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.end_headers()
            _, enimg = cv2.imencode('.png', cv_img)
            self.wfile.write(enimg)
        else:
            http.server.SimpleHTTPRequestHandler.do_GET(self)
        # Framerate
        import datetime
        sec=datetime.datetime.today().time().second
        if prev_sec == sec:
            counter+=1
        else:
            print("FPS: ", counter)
            prev_fps = counter
            counter = 1
        prev_sec=sec

if __name__ == '__main__':
    if "--no-fps" in sys.argv:
        SHOW_FPS_FLAG = False

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

