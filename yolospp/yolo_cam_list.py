import sys
import cv2
import numpy as np
from yolo_list import YOLO
from PIL import Image

def detect_img(yolo):
    #内部カメラ起動
    cap = cv2.VideoCapture(0)
    try:
        while (cap.isOpened()):
            #カメラからフレーム取得
            ret, frame = cap.read()
            if ret == True:
               #取得したフレームをout.jpgで保存
               cv2.imwrite("out.jpg", np.asarray(frame)[..., ::-1])
            try:
               #out.jpgを参照する
                image = Image.open("out.jpg")
            except:
                print('Open Error! Try again!')
                continue
            else:
                #フレームをyoloにかけ、人の(y,x)のリストを取得
                list = yolo.detect_image(image)
                print(list)
                
    except KeyboardInterrupt:
        #yoloをクローズ
        yolo.close_session()
        #キャプチャをクローズ
        cap.release()
        #opencvをクローズ
        cv2.destroyAllWindows()
    
    yolo.close_session()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
  detect_img(YOLO())
