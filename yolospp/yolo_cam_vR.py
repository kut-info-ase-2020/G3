import sys
import cv2
import numpy as np
import itertools
import math
import pyrealsense2
from human_distance import human_distance # 人との距離推定の実装
from print_distance import print_distance # 人との距離を画像上に表示する実装
from yolo import YOLO
from PIL import Image

def detect_img(yolo,RGB_image,depth_image):

            #人検出している
            #realsense_v2から処理済みの画像を取得
            #ret, frame = RGB_image
            #取得したフレームをout.jpgで保存
            cv2.imwrite("out.jpg", np.asarray(RGB_image)[..., ::-1])
            try:
               #out.jpgを参照する
                image = Image.open("out.jpg")
            except:
                print('Open Error! Try again!')
            else: 
               #フレームをyoloにかけ、識別済み画像と人の(y,x)のリストを取得
               r_image,list = yolo.detect_image(image)
               r_image.show()
               print(list)
                #opencvをクローズ
               #cv2.destroyAllWindows()
    
               #yolo.close_session()
               #cv2.destroyAllWindows()
               

               #距離推定プログラム
               # 参照するRGB画像と深度情報の指定
               import_npy = depth_image # 深度情報(npyファイル)
               image = RGB_image # RGB画像

               # 指定パスから読み込み
               #depth_image = np.load(import_npy)
               #image = cv2.imread(import_image)



               plot_list =list 
               # 保存した地点の情報の整理
               pr_x = [xy[0] for xy in plot_list]
               pr_y = [xy[1]-20 for xy in plot_list]
               for y in range(len(pr_y)):
                   if pr_y[y] < 0:
                       pr_y[y] = 0
               pr_depth = [depth_image[y][x] for x, y in zip(pr_x, pr_y)]

               # 距離推定
               comb, dis_list = human_distance(width = image.shape[1],pr_x = pr_x, pr_depth=pr_depth, isw=17, fcl=18)
               #comb, dis_list = human_distance(width = image.shape[1],pr_x = pr_x, pr_depth=pr_depth, agw=69.4)

               flag=0
               for dis in dis_list:
                 if dis < 2:
                   flag=1
                   break

               

                # 結果画像の作成
               result_image = print_distance(image=image, human_comb = comb, pr_x=pr_x, pr_y=pr_y, dis_list= dis_list)
                

                # 画像表示
               #result_image.imshow()
               #cv2.waitKey(0)

                # データをソケット経由で送信
               return len(list), dis_list, flag


