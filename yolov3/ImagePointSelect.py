import cv2
import numpy as np
import time
from MouseParam import MouseParam # ディレクトリ内モジュール(マウスイベント用)


class ImagePointSelect:
    # カラーセットのデフォルト
    __c_list = ((0,0,255),(0,255,0),(255,0,0),(255,255,0),(255,0,255),(0,255,255)) # 赤・緑・青・シアン・マゼンタ・黄

    # マウスで指定座標を選ぶ
    @classmethod
    def image_point_select(cls, import_image, *, color_list=__c_list , point_size = 1):
        print("------------------------ point select start ------------------------------")
        disp_image = np.copy(import_image)
        plot_list = []

        # 画像の表示設定
        WINDOWS_NAME = 'inpupt point' # windowに表示される名
        cv2.imshow(WINDOWS_NAME, disp_image) # 画像の表示

        # マウスイベントやカラー指定のために必要な変数
        Enter = 13 # Enterキーコード
        mouseData = MouseParam(WINDOWS_NAME) # コールバックの設定

        # マウスイベントとキー入力待ち
        while 1:
            key = cv2.waitKey(20)

            #左クリックがあったら座標を保存
            if mouseData.getEvent() == cv2.EVENT_LBUTTONDOWN:
                get_x = mouseData.getX()
                get_y = mouseData.getY()

                # 同じ座標を保存しないための処理
                if [get_x, get_y] in plot_list:
                    continue

                # カラーセットの数以上座標を保存しないための処理
                elif len(plot_list) >= len(color_list):
                    print('input point up to ' + str(len(color_list)))
                    time.sleep(0.3)
                    continue

                else :
                    # 座標の保存
                    print('save point : {0}'.format([get_x, get_y]))
                    plot_list.append([get_x, get_y])

                    # 画像の座標表示
                    disp_image = cls.__plot_image(disp_image, get_x, get_y, list(color_list[len(plot_list)-1]), point_size) # 画像に座標をプロット
                    cv2.imshow(WINDOWS_NAME, disp_image) # 画像の表示
                    time.sleep(0.3)

            # Enterキーが押されたとき
            elif key == Enter:
                cv2.destroyWindow(WINDOWS_NAME) # 画像を閉じる

                # 指定座標が何もない場合に実行
                if not plot_list:
                    print('click point not found.\nProgram finish.')
                    break

                # 指定座標の標準出力
                print('plot_list = {0}'.format(plot_list))

                break

        print("------------------------ point select finish ------------------------------")
        return plot_list

    @staticmethod
    def __plot_image(import_image, plot_x, plot_y, color_bgr, karnel_size):
        point_image = np.copy(import_image)
        n = karnel_size//2

        point_image[plot_y-n:plot_y+(n+1), plot_x-n:plot_x+(n+1), 0] = color_bgr[0]
        point_image[plot_y-n:plot_y+(n+1), plot_x-n:plot_x+(n+1), 1] = color_bgr[1]
        point_image[plot_y-n:plot_y+(n+1), plot_x-n:plot_x+(n+1), 2] = color_bgr[2]

        return point_image