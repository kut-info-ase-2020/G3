import cv2

# マウスイベントを管理するクラス
class MouseParam:

    # コンストラクタ
    def __init__(self, input_img_name):
        self.mouseEvent = {"x":None, "y":None, "event":None, "flags":None} # マウスイベント用のパラメータの初期化
        cv2.setMouseCallback(input_img_name, self.__CallBackFunc, None) # マウスイベント時の設定
        # マウスイベント時に__CallBackFuncに5つの引数(event,x,y,flagparam)が渡される


    # コールバック関数
    def __CallBackFunc(self, eventType, x, y, flags, userdata):
        self.mouseEvent["x"] = x
        self.mouseEvent["y"] = y
        self.mouseEvent["event"] = eventType
        self.mouseEvent["flags"] = flags

    # マウスイベント用のパラメータを返すための関数
    def getData(self):
        return self.mouseEvent

    # マウスのイベントの種類を返す関数
    def getEvent(self):
        return self.mouseEvent["event"]

    #マウスフラグを返す関数
    def getFlags(self):
        return self.mouseEvent["flags"]

    #xの座標を返す関数
    def getX(self):
        return self.mouseEvent["x"]

    #yの座標を返す関数
    def getY(self):
        return self.mouseEvent["y"]

    # x座標とy座標を返す関数
    def getPos(self):
        return (self.mouseEvent["x"], self.mouseEvent["y"])