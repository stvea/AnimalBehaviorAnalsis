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

    def setUnable(self):
        self.GroupBox.setEnabled(False)