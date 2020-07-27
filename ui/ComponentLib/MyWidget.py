from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout


class MyWidget:
    def set2FullVBoxLayout(self, widgets):
        vbl = QVBoxLayout()
        vbl.setContentsMargins(0, 0, 0, 0)
        for widget in widgets:
            vbl.addWidget(widget)
        return vbl

    def set2FullHBoxLayout(self, widgets):
        hbl = QHBoxLayout()
        hbl.setContentsMargins(0, 0, 0, 0)
        for widget in widgets:
            hbl.addWidget(widget)
        return hbl
