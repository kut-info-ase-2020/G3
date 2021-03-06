import pyrealsense2 as rs
import numpy as np
import cv2
import math
import datetime
import socket
import json
import os
from yolo import YOLO
import yolo_cam_vR as vR
'''
[深度カメラの表示用プログラム・本番用]
rgbカメラと深度カメラの画角合わせ・深度カメラ画像へのフィルタがかかっている
本番では、このプログラムで取得している画像や情報等を用いること
[参考]
https://qiita.com/gatideatui/items/7e76d85149b9b95f3888
https://qiita.com/idev_jp/items/3eba792279d836646664
'''

#ソケット通信の始まり
class Connect():
    def __init__(self):
       self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       self.s.connect(('192.168.0.35', 50007))

    def setsenddata(self, data):
        strdata = json.dumps(data)
        bindata = strdata.encode()
        # サーバにメッセージを送る
        self.s.sendall(bindata)

    def getrecvdata(self):
        # ネットワークのバッファサイズは1024。サーバからの文字列を取得する
        data = self.s.recv(1024)
        return data

    def close(self):
        self.s.close()

# カメラの設定を指定するクラス
class AppState:
    def __init__(self, *args, **kwargs):
        self.WIN_NAME = 'RealSense'
        self.pitch, self.yaw = math.radians(-10), math.radians(-15)
        self.translation = np.array([0, 0, -1], dtype=np.float32)
        self.distance = 2
        self.prev_mouse = 0, 0
        self.mouse_btns = [False, False, False]
        self.paused = False
        self.decimate = 1
        self.scale = True
        self.color = True

    def reset(self):
        self.pitch, self.yaw, self.distance = 0, 0, 2
        self.translation[:] = 0, 0, -1

    @property
    def rotation(self):
        Rx, _ = cv2.Rodrigues((self.pitch, 0, 0))
        Ry, _ = cv2.Rodrigues((0, self.yaw, 0))
        return np.dot(Ry, Rx).astype(np.float32)

    @property
    def pivot(self):
        return self.translation + np.array((0, 0, self.distance), dtype=np.float32)

# depthカメラのフィルタ周りの設定
state = AppState()
decimate = rs.decimation_filter()
decimate.set_option(rs.option.filter_magnitude, 1 ** state.decimate)
depth_to_disparity = rs.disparity_transform(True)
disparity_to_depth = rs.disparity_transform(False)
spatial = rs.spatial_filter()
spatial.set_option(rs.option.filter_smooth_alpha, 0.6)
spatial.set_option(rs.option.filter_smooth_delta, 8)
temporal = rs.temporal_filter()
temporal.set_option(rs.option.filter_smooth_alpha, 0.5)
temporal.set_option(rs.option.filter_smooth_delta, 20)
hole_filling = rs.hole_filling_filter()


# 深度画像とRGB画像を録画
def realsence():
    # rgb画像の画角を取得
    align = rs.align(rs.stream.color)

    # 設定の反映
    config = rs.config()

    # RGB画像と深度情報の解像度・fpsの指定
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

    # ストリーミング開始
    pipeline = rs.pipeline()
    profile = pipeline.start(config)

    intr = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
    print(intr.width, intr.height, intr.fx, intr.fy, intr.ppx, intr.ppy)

    c=Connect()

    try:
        while True:
            # フレーム待ち
            frames = pipeline.wait_for_frames()
            aligned_frames = align.process(frames)

            # RGB画像
            RGB_frame = aligned_frames.get_color_frame()
            RGB_image = np.asanyarray(RGB_frame.get_data())

            # 深度情報
            depth_frame = aligned_frames.get_depth_frame()

            # 深度情報に対するフィルタ処理
            depth_frame = decimate.process(depth_frame)
            depth_frame = depth_to_disparity.process(depth_frame)
            depth_frame = spatial.process(depth_frame)
            depth_frame = temporal.process(depth_frame)
            depth_frame = disparity_to_depth.process(depth_frame)
            depth_frame = hole_filling.process(depth_frame)

            # 深度情報の整形
            depth_image = np.asanyarray(depth_frame.get_data()) # 深度情報を読み込み
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.0255),
                                cv2.COLORMAP_JET) # 深度情報を疑似カラー画像に変換
            
            human_num,dis_list,dis_flag= vR.detect_img(YOLO(),RGB_image,depth_image)
            send_data(c,human_num,dis_list,dis_flag)
            # 表示表示
            #images = np.hstack((RGB_image, depth_colormap))
            #cv2.imshow('RealSense', images) # 画像表示

            if cv2.waitKey(1) & 0xff == 27: # ESCで終了
                cv2.destroyAllWindows()
                break

    finally:
        # ストリーミング停止
        pipeline.stop()
        c.close()

# データ送信（ソケット通信）
def send_data(c, human_num, dis_list, dis_flag):
    #データ送信
    data = {
            "id":3,
            "num":human_num, #入室人数
            "metre":dis_list, #各人物の距離推定
            "metre_NG": dis_flag #距離推定の結果２m以内の有無
    }
    print(data)
    c.setsenddata(data)
    send_status = c.getrecvdata()


if __name__ == '__main__':
    realsence()