from PyQt5.QtWidgets import *

from Entity.OperateMenu import OperateMenu
from ui.ComponentLib.MyWidget import MyWidget

class Menu(MyWidget):
    def __init__(self):
        super(Menu, self)
        self.GroupBox = QGroupBox("实验步骤")
        self.experimentExploer = QTreeWidget()
        self.experimentExploer.setColumnCount(1)
        self.experimentExploer.setHeaderHidden(True)
        operateMenus = [['视频操作', '查看视频信息'], ['检测设置', '标注区域', '视频范围'], ['结果分析', '结果预览', '数据导出', '数据预览']]
        for menusIndex in range(len(operateMenus)):
            for menuIndex in range(len(operateMenus[menusIndex])):
                if menuIndex == 0:
                    operateMenus[menusIndex][menuIndex] = OperateMenu(operateMenus[menusIndex][menuIndex],
                                                                      self.experimentExploer)
                else:
                    operateMenus[menusIndex][menuIndex] = OperateMenu(operateMenus[menusIndex][menuIndex],
                                                                      operateMenus[menusIndex][0].getQTreeWidgetItem())
        self.experimentExploer.expandAll()
        self.GroupBox.setLayout(self.set2FullVBoxLayout([self.experimentExploer]))

    def setUnable(self):
        self.GroupBox.setEnabled(False)