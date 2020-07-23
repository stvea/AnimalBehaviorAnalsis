import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *


class OperateMenu:
    def __init__(self, name, parent):
        self.name = name
        self.qTreeWidgetItem = QTreeWidgetItem(parent)
        self.qTreeWidgetItem.setText(0, name)

    def getQTreeWidgetItem(self):
        return self.qTreeWidgetItem

    def getName(self):
        return self.qTreeWidgetItem.text(0)
