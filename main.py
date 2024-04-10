# 股票 代码,1s更新一次 最新股价和百分比涨跌幅
import ctypes
import psutil
import requests
import json
import time
import os

# demo
"""
url https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&invt=2&fields=f2,f3,f12,f14,f9&secids=0.000661,1.603259,0.300142,0.300122,0.002007,0.300601,1.600201,0.300529,0.300676,1.600867,&_=1599742806408
response :
{
    "rc": 0,
    "rt": 11,
    "svr": 182482658,
    "lt": 1,
    "full": 1,
    "dlmkts": "",
    "data": {
        "total": 10,
        "diff": [
            {
                "f2": 120,
                "f3": 0.51,
                "f9": 10.71,
                "f12": "000661",
                "f14": "长春高新"
            },
            {
                "f2": 45.89,
                "f3": -0.48,
                "f9": 14.01,
                "f12": "603259",
                "f14": "药明康德"
            },
            {
                "f2": 15.17,
                "f3": 1.07,
                "f9": 58.14,
                "f12": "300142",
                "f14": "沃森生物"
            },
            {
                "f2": 44.47,
                "f3": 0.91,
                "f9": 12.26,
                "f12": "300122",
                "f14": "智飞生物"
            },
            {
                "f2": 18.93,
                "f3": 0.96,
                "f9": 23.37,
                "f12": "002007",
                "f14": "华兰生物"
            },
            {
                "f2": 21.65,
                "f3": 0.93,
                "f9": 26.02,
                "f12": "300601",
                "f14": "康泰生物"
            },
            {
                "f2": 9.5,
                "f3": 0.42,
                "f9": 27.69,
                "f12": "600201",
                "f14": "生物股份"
            },
            {
                "f2": 22.44,
                "f3": 1.54,
                "f9": 32.08,
                "f12": "300529",
                "f14": "健帆生物"
            },
            {
                "f2": 39.94,
                "f3": 1.89,
                "f9": 181.25,
                "f12": "300676",
                "f14": "华大基因"
            },
            {
                "f2": 10.21,
                "f3": 0,
                "f9": 17.43,
                "f12": "600867",
                "f14": "通化东宝"
            }
        ]
    }
}
"""
import dataclasses


@dataclasses.dataclass
class retStockInfo:
    stock_name: str
    stock_price: float
    stock_percent: float


# 根据 上述 代码, 从东方财富网获取 股票 名称 和 最新股价 和 涨跌幅
def get_stock_price(stock_code_list):
    ret = list[retStockInfo]
    ret = []
    stock_code_list_str = ",".join(stock_code_list)
    url = "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&invt=2&fields=f2,f3,f12,f14,f9&secids=" + stock_code_list_str + "&_=" + str(int(time.time()))
    response = requests.get(url)
    # print(url)
    data = json.loads(response.text)
    for item in data["data"]["diff"]:
        stock_name = item["f14"]
        stock_price = item["f2"]
        stock_percent = item["f3"]
        ret.append(retStockInfo(stock_name, stock_price, stock_percent))
    return ret


from PySide2 import QtCore, QtWidgets, QtGui

# 新建一个窗口,无边框,半透明,置顶,显示股票信息 窗口大小等于 16号 字体大小 宽度20个字符 高度 1.5个字符
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *


@dataclasses.dataclass
class stockConfig:
    stock_code: str
    # 买入价: float# 用英语
    buy_price: float
    # 买入数量: int
    buy_count: int
    def to_json(self):
        return json.dumps(self.__dict__)


@dataclasses.dataclass
class stockConfigList:
    data = list[stockConfig]
    def to_json(self):
        ret = "["
        for item in self.data:
            ret += item.to_json()
            if(item != self.data[-1]):
                ret += ","
        ret+="]"
        return ret
    def savejson(self):
        with open("stock.json", "w") as f:
            ret = self.to_json()
            f.write(ret)

    def loadjson(self):
        self.data = []
        try:
            with open("stock.json", "r") as f:
                obj = json.loads(f.read())
                for item in obj:
                    self.data.append(stockConfig(item["stock_code"], item["buy_price"], item["buy_count"]))
        except:
            self.data.append(stockConfig("0.002167", 0, 0))
            self.savejson()


class newLabel(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(newLabel, self).__init__(parent)
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(0, 0, 20 * 9, 1.5 * 9)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label.setStyleSheet("background-color:rgba(255,255,255,0.1); color: rgba(196, 183, 215,0.8);")

    def setText(self, text):
        self.label.setText(text)

def formatStr(str):
    ret =""
    # 1.0 -> 01.00 保留2位小数,且整数部分2位 前补0
    ret = "{:0>5.2f}".format(str)
    # 替换ret 字符串前的所有0 为 空格
    # 替换ret 字符串尾部的所有0 为 空格,中间的不替换,小数点前的0不替换
    num整数部分=ret.split(".")[0]
    num小数部分=ret.split(".")[1]
    for i in range(2):
        if num整数部分[i] == "0":
            num整数部分 = " " + num整数部分[1:]
        else:
            break

    ret = num整数部分 + "." + num小数部分
    return ret

class StockWindow(QtWidgets.QWidget):
    def __init__(self):
        self.tipstr1=""
        super(StockWindow, self).__init__()
        self.labels = list[newLabel]
        self.stock_config = stockConfigList()
        self.stock_config.loadjson()
        self.initLabelAddr(len(self.stock_config.data))
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # 使用 QTimer 定时器,每隔1s更新一次股票信息
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_stock_info)
        self.tray_icon = QSystemTrayIcon(self)
        self.setWindowIcon(QIcon("logo.ico"))
        self.tray_icon.setIcon(QIcon("logo.ico"))
        self.windowLastHeight = 0
        # 串口悬停显示
        
        tray_menu = QMenu(self)

        # Create actions for tray menu
        show_action = QAction("显示", self)
        quit_action = QAction("关闭", self)

        # Add actions to tray menu
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)

        # Set tray menu for system tray icon
        self.tray_icon.setContextMenu(tray_menu)

        # Connect actions to functions
        show_action.triggered.connect(self.showNormal)
        quit_action.triggered.connect(self.quit_app)
        self.tray_icon.show()

    def initLabelAddr(self, len):
        self.labels=[]
        for i in range(len):
            label = newLabel(self)
            label.setGeometry(0, 1.5 * 9 * i, 20 * 9, 1.5 * 9)
            self.labels.append(label)
        self.resize(20 * 9, 1.5 * 9 * len)

    def quit_app(self):
        QApplication.quit()


    def update_stock_info(self):
        # 非开市时间,不更新
        now = time.localtime()
        if now.tm_hour < 9 or now.tm_hour > 15:
            return
        # 中午休市
        if now.tm_hour == 11 and now.tm_min > 30:
            return
        reqCodeList = list[str]
        reqCodeList = []
        for stock in self.stock_config.data:
            reqCodeList.append(stock.stock_code)
        ret: list[retStockInfo]
        ret = get_stock_price(reqCodeList)

        self.update_stock(ret)
        profit = self.盈亏计算(ret)
        self.tipstr1 += f"盈亏: {profit:.2f}"
        self.tipstr1=self.tipstr1.replace("\t", " ")
        self.tray_icon.setToolTip(self.tipstr1)
        # print(self.tipstr1)

    def 盈亏计算(self,ret: list[retStockInfo])->int:
        rett = 0
        for i in range(len(ret)):
            stock = self.stock_config.data[i]
            buy_price = stock.buy_price
            buy_count = stock.buy_count
            stock_price = ret[i].stock_price
            stock_percent = ret[i].stock_percent
            if buy_price == 0 or buy_count == 0:
                continue
            buy_total = buy_price * buy_count
            now_total = stock_price * buy_count
            profit = now_total - buy_total
            profit_percent = profit / buy_total * 100
            rett+=profit
        # 印花税 0.1% 计算
        rett = rett * 0.999
        # 每个股票的佣金 万5, 最低 5源, 卖出计算1次
        # for i in range(len(ret)):
        #     持仓2 = ret[i].stock_price * self.stock_config.data[i].buy_count
        #     佣金2 = max(5, 持仓2 * 0.0005)
        #     rett -= 佣金2


        return rett
    

    def update_stock(self, ret: list[retStockInfo]):
        self.tipstr1 = ""
        for i in range(len(ret)):
            stock_name = ret[i].stock_name
            stock_price = ret[i].stock_price
            stock_percent = ret[i].stock_percent
            self.labels[i].setText(stock_name + "\t" + str(stock_price) + "\t" + str(stock_percent) + "%")
            self.tipstr1+=stock_name + "\t" + formatStr(stock_percent) + "%\t" + formatStr(stock_price) + "\n"


    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    # 双击关闭窗口
    def mouseDoubleClickEvent(self, event):
        self.close()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage("Demo", "应用已最小化到托盘", QSystemTrayIcon.Information, 2000)


def checkrunning():
    try:
        with open("app.pid") as f:
            pid = int(f.read())
        if psutil.pid_exists(pid):
            print("Already running!")
            return True
        else:
            with open("app.pid", "w") as f:
                f.write(str(os.getpid()))
            return False
    except:
        with open("app.pid", "w") as f:
            f.write(str(os.getpid()))

        return False


if __name__ == "__main__":
    #   放到 托盘区运行,
    if checkrunning() == False:
        import sys

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("CompanyName.ProductName.jiucai")
        from PySide2.QtGui import QIcon, QPainter, QImage, QBrush, QColor, QFont

        app = QtWidgets.QApplication(sys.argv)
        app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
        stock_window = StockWindow()
        stock_window.show()
        stock_window.timer.start(1000)
        stock_window.setWindowIcon(QIcon("logo.ico"))
        stock_window.tray_icon.activated.connect(stock_window.showNormal)
        sys.exit(app.exec_())
