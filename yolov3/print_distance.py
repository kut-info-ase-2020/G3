import numpy as np
import cv2

'''
pr_x = List of x-coordinates of person
pr_y = List of y-coordinates of person
pr_dis = List of distace of two people
human_comb = Combination of people who measure distance.
example: A, B, C combination is [[0,1],[0,2],[1,2]]
'''

def print_distance(image, human_comb, pr_x, pr_y, dis_list):
    result_image = image.copy()

    # 各人の距離を表示
    for (a, b), dis in zip(human_comb, dis_list):
        # 2人の座標情報の読み込み
        Ax = int(pr_x[a])
        Bx = int(pr_x[b])
        Ay = int(pr_y[a])
        By = int(pr_y[b])

        # 距離を表示する座標を2人の距離の中心に指定
        xtp = abs(Ax-Bx) // 2 + min(Ax, Bx)
        ytp = abs(Ay-By) // 2 + min(Ay, By)

        # 画像内に距離の表示と線を引く
        result_image = cv2.line(result_image, (Ax, Ay), (Bx, By), (0, 0, 255),
                            thickness=1, lineType=cv2.LINE_4) # 2人の座標間に線を引く
        cv2.putText(result_image, '{:2f} m'.format(dis), (xtp, ytp+30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), thickness=1) # 2人の座標間に距離を表示

    return result_image