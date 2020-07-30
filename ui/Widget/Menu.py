from PyQt5.QtWidgets import *

from Entity.OperateMenu import OperateMenu
from SystemInfo import SystemInfo
from ui.ComponentLib.MyWidget import MyWidget

class Menu(MyWidget):
    def __init__(self):
        super(Menu, self)
        self.GroupBox = QGroupBox("实验步骤")
        self.experimentExploer = QTreeWidget()
        self.experimentExploer.setColumnCount(1)
        self.experimentExploer.setHeaderHidden(True)
        for menusIndex in range(len(SystemInfo.operate_menus)):
            for menuIndex in range(len(SystemInfo.operate_menus[menusIndex])):
                if menuIndex == 0:
                    SystemInfo.operate_menus[menusIndex][menuIndex] = OperateMenu(SystemInfo.operate_menus[menusIndex][menuIndex],
                                                                      self.experimentExploer)
                else:
                    SystemInfo.operate_menus[menusIndex][menuIndex] = OperateMenu(SystemInfo.operate_menus[menusIndex][menuIndex],
                                                                      SystemInfo.operate_menus[menusIndex][0].getQTreeWidgetItem())
        self.experimentExploer.expandAll()
        self.GroupBox.setLayout(self.set2FullVBoxLayout([self.experimentExploer]))
        self.experimentExploer.clicked.connect(self.switchSet)

    def switchSet(self, index):
        item = self.experimentExploer.currentItem()
        SystemInfo.main_view.setWidget.stopPaint()
        if item.text(0) == "查看视频信息":
            SystemInfo.main_view.setWidget.stackWidget.setCurrentWidget(SystemInfo.main_view.setWidget.videoInfo)
            SystemInfo.main_view.setWidget.GroupBox.setTitle("查看视频信息")
        elif item.text(0) == "视频范围":
            SystemInfo.main_view.setWidget.stackWidget.setCurrentWidget(SystemInfo.main_view.setWidget.detectSet)
            SystemInfo.main_view.setWidget.GroupBox.setTitle("视频范围")
        elif item.text(0) == "标注区域":
            SystemInfo.main_view.setWidget.startPaint()
        elif item.text(0) == SystemInfo.operate_menus[1][3].getName():
            SystemInfo.main_view.setWidget.startScalePaint()