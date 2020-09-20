import cv2
import numpy as np

#from human_distance import human_distance # 人との距離推定の実装(水平撮影範囲と焦点距離を指定)
from human_distance_v2 import human_distance # 人との距離推定の実装(水平画角を指定)
from ImagePointSelect import ImagePointSelect # 画像をクリックした地点を保存する実装
from print_distance import print_distance # 人との距離を画像上に表示する実装

'''
[画像と深度情報を指定し、クリックした箇所の距離を推定して表示]
'''

def main():
    # 参照するRGB画像と深度情報の指定
    import_npy = '../2020-9-1_16-12-5/2020-9-1_16-12-5_001017.npy' # 深度情報(npyファイル)
    import_image = '../2020-9-1_16-12-5/2020-9-1_16-12-5_1017.png' # RGB画像

    # 指定パスから読み込み
    depth_image = np.load(import_npy)
    image = cv2.imread(import_image)

    # 画像上でクリックした地点を保存する
    im = ImagePointSelect()
    '''color_listはクリックした地点をマークする色の指定(BGR)を行う → この数を増やせばクリックする個所を増やせる'''
    '''color_listを指定しなければ6地点保存できる（デフォルト）'''
    plot_list = im.image_point_select(image, color_list=((0,0,255),(0,255,0),(255,0,0)))

    # 保存した地点の情報の整理
    pr_x = [xy[0] for xy in plot_list]
    pr_y = [xy[1] for xy in plot_list]
    pr_depth = [depth_image[y][x] for x, y in zip(pr_x, pr_y)]

    # 距離推定
    #comb, dis_list = human_distance(width = image.shape[1],pr_x = pr_x, pr_depth=pr_depth, isw=17, fcl=18)
    comb, dis_list = human_distance(width = image.shape[1],pr_x = pr_x, pr_depth=pr_depth, agw=69.4)

    # 結果画像の作成
    result_image = print_distance(image=image, human_comb = comb, pr_x=pr_x, pr_y=pr_y, dis_list= dis_list)

    # 画像表示
    cv2.imshow("result", result_image)
    cv2.waitKey(0)

if __name__ == '__main__':
    main()
