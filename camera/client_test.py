#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2

 #mjpg-streamerを動作させているPC・ポートを入力
URL = "http://192.168.10.110:8080/?action=stream"
s_video = cv2.VideoCapture(URL)

while True:
    ret, img = s_video.read()
    cv2.imshow("WebCamera form Raspberry pi",img)
    key = cv2.waitKey(1)
    if k == 27: #Esc入力時は終了
        break