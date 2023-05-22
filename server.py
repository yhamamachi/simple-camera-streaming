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
import datetime
import numpy as np

#HOST = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT")) if os.environ.get("PORT") is not None else 5900
QUALITY = 50
ROTATE = False
GRAYSCALE = False
RESIZE = False
OPTIMIZE = False
W = int(os.environ.get("CAM_W")) if os.environ.get("CAM_W") is not None else 640
H = int(os.environ.get("CAM_H")) if os.environ.get("CAM_H") is not None else 480
X = 0
Y = 0
CAM_NUM = int(os.environ.get("CAM_NUM")) if os.environ.get("CAM_NUM") is not None else 0
cap = cv2.VideoCapture(CAM_NUM)

# FPS related variables
SHOW_FPS_FLAG = True
counter = 0
sec = 0
prev_sec = 0
prev_fps = 0
g_frame_counter = 0

class VNCServer(http.server.SimpleHTTPRequestHandler):
    testFlag = False
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)

    def generateDummyFrame(self):
        global g_frame_counter
        image = np.zeros((H,W,3), np.uint8)
        g_frame_counter += 1
        output_text = [
                "Hello world",
                "  Python OpenCV",
                "CurrentTime:",
                "  {}".format(datetime.datetime.now()),
                "FrameCount:",
                "  {}".format(g_frame_counter),
        ]
        text_color = (0,255,0) #( B,G,R ) => Green
        for idx, text in enumerate(output_text):
            text_scale = 1
            xoffset = 20
            yoffset = (idx+3) * 50*text_scale
            font = cv2.FONT_HERSHEY_SIMPLEX
            thickness = 2
            cv2.putText(image, text, (xoffset, yoffset) ,font ,text_scale ,text_color ,thickness ,cv2.LINE_AA)
        return image

    def getFrame(self):
        if self.testFlag is False:
            _, output = cap.read()
        else: # is True
            output = self.generateDummyFrame()
        output = self.procFrame(output)
        return output

    def procFrame(self, cv_img):
        global SHOW_FPS_FLAG
        self.proc_fps()

        output = cv_img
        if GRAYSCALE:
            output = cv2.cvtColor(output,cv2.COLOR_RGB2GRAY)
        if ROTATE:
            output = cv2.rotate(output, cv2.ROTATE_90_CLOCKWISE)
        if RESIZE:
            output = cv2.resize(output, dsize=(W,H) )
        if SHOW_FPS_FLAG is True:
            output = self.writeFPSinFrame(output)
        return output

    def writeFPSinFrame(self, cv_img):
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
            cv2.putText(cv_img, text, (xoffset, yoffset)
                    ,font ,text_scale ,text_color ,thickness ,cv2.LINE_AA)
        return cv_img

    def proc_fps(self):
        global sec
        global prev_sec
        global counter
        global prev_fps
        sec=datetime.datetime.today().time().second
        if prev_sec == sec:
            counter+=1
        else:
            print("FPS: ", counter)
            prev_fps = counter
            counter = 1
        prev_sec=sec

    def do_GET(self):
        self.path = self.path.split('?')[0]
        basename = self.path.split('.')[0]
        if basename == "/frame":
            ext = self.path.split('.')[1]
            cv_img = self.getFrame()
            self.send_response(200)
            self.send_header('Content-Type', 'image/'+ext)
            self.end_headers()
            #_enimg = ""
            if ext == "jpeg":
                _, enimg = cv2.imencode('.'+ext, cv_img, (cv2.IMWRITE_JPEG_QUALITY, QUALITY))
            else:
                _, enimg = cv2.imencode('.'+ext, cv_img)
            self.wfile.write(enimg)
        elif self.path == "/stream.bmp":
            ext = self.path.split('.')[1]
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            while True:
                cv_img = self.getFrame()
                _, enimg = cv2.imencode('.'+ext, cv_img)

                self.wfile.write(b'--frame\r\n')
                self.send_header('Content-Type', 'image/'+ext)
                self.send_header('Content-Length', len(enimg))
                self.end_headers()
                self.wfile.write(enimg)
                self.wfile.write(b'\r\n')
        else:
            http.server.SimpleHTTPRequestHandler.do_GET(self)

    def log_message(self, format, *args):
        print(args)
        pass

if __name__ == '__main__':
    if "--no-fps" in sys.argv:
        SHOW_FPS_FLAG = False

    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer((HOST, PORT), VNCServer)
    httpd.allow_reuse_address = True
    print('Server started at http://%s:%s' % (HOST, PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
       pass
    httpd.server_close()
    print('Server stopped')

