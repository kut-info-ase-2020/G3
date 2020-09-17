import sys
import cv2
import numpy as np
from yolo import YOLO
from PIL import Image

def detect_img(yolo):
    cap = cv2.VideoCapture(0)
    try:
        while (cap.isOpened()):
            ret, frame = cap.read()
            if ret == True:
               cv2.imwrite("out.jpg", np.asarray(frame)[..., ::-1])
            try:
                image = Image.open("out.jpg")
            except:
                print('Open Error! Try again!')
                continue
            else:
                r_image,list = yolo.detect_image(image)
                r_image.show()
                print(list)
    except KeyboardInterrupt:
        yolo.close_session()
        cap.release()
        cv2.destroyAllWindows()
    
    yolo.close_session()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
  detect_img(YOLO())
