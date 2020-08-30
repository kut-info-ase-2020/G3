#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    # 画像を表示する
    cv2.imshow('Image', frame)

    k = cv2.waitKey(1)
    if k == 27:
        break

# 終了処理
cap.release()
cv2.destroyAllWindows()