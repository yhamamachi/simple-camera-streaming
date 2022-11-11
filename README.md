Video Straming Server & Client
=======================

Simple server and client using plain old HTML. However, it does not use the RFB protocol, but a series of JPEG frames.

## Requirements

 - Python 3
 - python-opencv

## Usage

Run `python3 ./server.py` and connect to `http://[local_address]:5900` using your web browser. For configuration options look at the top of the `server.py` file.

## Screenshot

![Preview of Kindle VNC Client](http://i.imgur.com/pKdzviw.jpg)

## Author

Original Developed by Jerzy Głowacki under Apache 2.0 License

Modified for video streaming and supporting python3 by Yuya Hamamachi

