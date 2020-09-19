import pyrealsense2 as rs
import numpy as np
import cv2
import math
import datetime
import os

'''
[参考]
https://qiita.com/gatideatui/items/7e76d85149b9b95f3888
https://qiita.com/idev_jp/items/3eba792279d836646664
'''
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
def record_realsence(export_dir):

    time_str = get_time()

    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    video = cv2.VideoWriter(export_dir + '/'+ time_str + '.mp4', fourcc, 30, (640, 480))

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

    try:
        i = 0　# 深度情報のファイル数を初期化
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

            # 深度情報を疑似カラー画像に変換
            depth_image = np.asanyarray(depth_frame.get_data()) # 深度情報を読み込み
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.0255),
                                cv2.COLORMAP_JET) # 深度情報を疑似カラー画像に変換

            # 表示表示
            images = np.hstack((RGB_image, depth_colormap))
            cv2.imshow('RealSense', images) # 画像表示

            # 動画への書き込み・深度情報の保存
            video.write(RGB_image)
            np.save(export_path + '/'+ export_file + '_{:0>6}'.format(i) , depth_image)

            i = i+1 # 深度情報のファイル数を更新

            if cv2.waitKey(1) & 0xff == 27: # ESCで終了
                cv2.destroyAllWindows()
                break

        # 動画を出力
        video.release()

    finally:
        # ストリーミング停止
        pipeline.stop()

# 現在時刻を取得する
def get_time():
    # 現在時刻の取得
    dt_now = datetime.datetime.now()
    year = dt_now.year
    month = dt_now.month
    day = dt_now.day
    hour = dt_now.hour
    minute = dt_now.minute
    second = dt_now.second

    time_str = '{0}-{1}-{2}_{3}-{4}-{5}'.format(year, month, day, hour, minute,second)
    return time_str

if __name__ == '__main__':
    export_dir = '' # 出力先ディレクトリを指定
    record_realsence(export_dir)
