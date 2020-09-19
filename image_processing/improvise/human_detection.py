import cv2
import numpy as np
import time
import itertools
import math
import socket
import json

BACK_TH = 10 # 背景差分後の画像を二値化するための閾値
AREA_TH = 2000 # 検出した候補領域のうち、小さな領域を取り除くための閾値
RECT_TH = 100 # 検出した矩形領域をオーバーラップする領域の閾値
CAMERA_ANGLE = 70 # カメラの画角の設定
CAMERA_DIS = 3 # カメラから人までの距離

'''
[参考]
バウンティングボックスのオーバーラップ関連
https://stackoverrun.com/ja/q/12688561

'''


class Conect():
    def __init__(self):
       self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       self.s.connect(('192.168.0.8', 50007))

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


def main():
    c = Conect()

    # 動画の読み込み
    cap = cv2.VideoCapture(0)

    # 動画情報の読み込み(動画を作成する際のパラメータ)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # 作成する動画の設定
    #fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    #video = cv2.VideoWriter('./overlap_union.mp4', fourcc, fps, (width, height))

    # 最初のフレームの処理
    end_flag, frame = cap.read()

    #　背景差分法(CNT)のインスタンスを作成
    bg = cv2.bgsegm.createBackgroundSubtractorCNT()

    try:　
        # フレームの読み込みと背景差分法の適用
        while(end_flag):
            start = time.time()

            # 人検出
            box_list, human_image = human_detection(bg, frame, AREA_TH)

            # 人距離推定
            comb, dis_list, distance_image = human_distance(box_list, CAMERA_ANGLE, CAMERA_DIS, frame.shape[1], human_image)

            flag=True
            for dis in dis_list:
                if dis > 2:
                    flag=False
                    break

            # データをソケット経由で送信
            #send_data(c, len(box_list), dis_list, flag)

            # 次のフレームの準備
            end_flag, frame = cap.read()

            end = time.time() - start
            #print ("image_time:{0}".format(end) + "[sec]")

            # 検出した結果をウィンドウに表示
            cv2.imshow('human_view', human_image)
            cv2.imshow('human_distance', distance_image)


            # 動画処理中の中断処理
            k = cv2.waitKey(1)
            if k == 27: # ESCキー
                break

            # 動画への書き込み
            #video.write(img)

        # 動画を解放
        #video.release()

    # 'Ctrl+C' が押されたとき、ソケットをクローズ
    except KeyboardInterrupt:
            c.close()


    # 終了処理
    cv2.destroyAllWindows()
    cap.release()

# 人検出
def human_detection(bg, frame, area_th):
    # グレースケールに変換
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 背景差分法(CNT)
    sub = bg.apply(gray)

    # 輪郭抽出
    labels, contours, hierarchy = cv2.findContours(sub, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    box_list = []
    # 検出した領域を矩形描画するための処理
    for i in range(0, len(contours)):
        if len(contours[i]) > 0:

            # 抽出エリアの内、小さなエリアは取り除く
            if cv2.contourArea(contours[i]) < area_th:
                continue

            rect = contours[i]
            x, y, w, h = cv2.boundingRect(rect) # 外接矩形領域を算出
            #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 0), 10) # 矩形領域を描画
            box_list.append((x,y,w,h))

    box_list = combine_boxes(box_list)

    result_frame = frame.copy()
    for box in box_list:
        x, y, w, h = box
        cv2.rectangle(result_frame, (x, y), (x + w, y + h), (0, 0, 255), 10) # 矩形領域を描画

    return box_list, result_frame


# 2個のバウンティングボックスの和集合を求める
def union(a,b):
     x = min(a[0], b[0])
     y = min(a[1], b[1])
     w = max(a[0]+a[2], b[0]+b[2]) - x
     h = max(a[1]+a[3], b[1]+b[3]) - y
     return (x, y, w, h)

# 2個のバウンティングボックスの積集合を求める
def intersection(a,b):
     x = max(a[0], b[0])
     y = max(a[1], b[1])
     w = min(a[0]+a[2], b[0]+b[2]) - x
     h = min(a[1]+a[3], b[1]+b[3]) - y
     # ボックス同士がRECT_THの範囲以内にいないなら何も返さない
     if w< -1 * RECT_TH or h< -1 * RECT_TH : return () # or (0,0,0,0) ?
     # ボックスが重なっている、ボックス同士がRECT_THの範囲以内にいる場合、積集合の値を返す
     return (x, y, w, h)

# 近くにあるバウンティングボックスの統合
def combine_boxes(boxes):
    noIntersectLoop = False
    noIntersectMain = False
    posIndex = 0 # バウンティングボックスの添字

    while noIntersectMain == False:
        noIntersectMain = True
        posIndex = 0

        # ボックスの数だけ処理を実行
        while posIndex < len(boxes):
            noIntersectLoop = False
            while noIntersectLoop == False and len(boxes) > 1:
                a = boxes[posIndex] # 1個目のボックス
                listBoxes = np.delete(boxes, posIndex, 0)
                index = 0

                # 1個のボックスを固定して、それに対して他のボックスが統合するか判定
                for b in listBoxes:
                    # 各ボックス同士が重なっている、もしくは近い位置にいる場合に実行
                    if intersection(a, b):
                        newBox = union(a,b) # 和集合を求める
                        listBoxes[index] = newBox # 新しいボックスの作成
                        boxes = listBoxes # ボックス情報の上書き
                        noIntersectLoop = False
                        noIntersectMain = False
                        index = index + 1
                        break
                    noIntersectLoop = True
                    index = index + 1
            posIndex = posIndex + 1
    return boxes

# 距離推定
def human_distance(box_list, camera_angle, camera_dis, image_width, image):
    point = []
    for box in box_list:
        x = box[0] + box[2]//2
        y = box[1]
        point.append([x,y])

    comb = itertools.permutations(list(range(len(point))), 2)
    result_image = image.copy()
    dis_list = []
    for c1, c2 in comb:
        a = point[c1]
        b = point[c2]

        view_area = math.tan(math.radians(camera_angle/2)) * camera_dis * 2
        dis = abs(float(a[0]) - float(b[1])) * (float(view_area) / float(image_width))
        dis_list.append(dis)

        xtp = abs(a[0]-b[0]) // 2 + min(a[0], b[0])
        ytp = abs(a[1]-b[1]) // 2 + min(a[1], b[1])
        result_image = cv2.line(result_image, (a[0], a[1]), (b[0], b[1]), (0, 0, 255), thickness=1, lineType=cv2.LINE_4)
        cv2.putText(result_image, '{:.2f} m'.format(dis), (xtp, ytp+30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), thickness=1)

    return comb, dis_list, result_image

# データ送信（ソケット通信）
def send_data(c, human_num, dis_list, dis_flag):
    #データ送信
    data = {
            "id":3,
            "num":len(box_list), #入室人数
            "metre":dis_list, #各人物の距離推定
            "metre_NG": flag #距離推定の結果２m以内の有無
    }
    try:
        c.setsenddata(data)
        send_status = c.getrecvdata()
    except send_status == 'ok':
        c.close()


if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time() - start
    print ("all_time:{0}".format(end) + "[sec]")
