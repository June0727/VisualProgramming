import sys, os
from PIL import Image
import numpy as np

import matplotlib.pyplot as plt 
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.image import imread

from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                               QWidget, QFileDialog, QListWidget, QHBoxLayout
                               ,QListWidgetItem, QMessageBox, QStatusBar)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt

class ImageViewr(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.axis('off')
        
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.item_click)
        
        lm = QHBoxLayout()
        widget = QWidget()
        widget.setLayout(lm)
        self.setCentralWidget(widget)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        left_lm = QVBoxLayout()
        left_lm.addWidget(self.file_list)
        
        lm.addLayout(left_lm)
        lm.addWidget(self.canvas)
        
        self.dragging = False
        self.rect = None
        self.start_Point = (0,0)
        self.image = None
        
        self.file_list.addItem("Set Directory")
        
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        
    def set_dir(self):
        dir = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir:
            self.file_list.clear()
            self.file_list.addItem('Set Directory')
            for file_name in os.listdir(dir):
                if file_name.lower().endswith(('.png', '.jpg')):
                    item = QListWidgetItem(file_name)
                    item.setData(Qt.UserRole, os.path.join(dir, file_name))
                    
                    icon = self.create_icon(os.path.join(dir, file_name))
                    item.setIcon(icon)
                    
                    self.file_list.addItem(item)
                    
    def create_icon(self, file_path):
        image = Image.open(file_path)
        image.thumbnail((64,64))
        image.save("icon.png")
        return QIcon(QPixmap("icon.png"))
    
    def item_click(self, item):
        if item.text() == "Set Directory":
            self.set_dir()
        else:
            file_path = item.data(Qt.UserRole)
            self.status_bar.showMessage(file_path)
            self.load_image(file_path)
            
    def load_image(self, file_name):
        self.image = imread(file_name)
        self.ax.clear()
        self.ax.imshow(self.image)
        self.ax.axis('on')
        self.canvas.draw()
        
    def on_click(self, event):
        if self.image is None:
            return
        if event.button == 3:
            self.on_right_click(event)
        else:
            if event.inaxes != self.ax:
                return
            self.dragging = True
            self.start_point = (event.xdata, event.ydata)
            self.rect = self.ax.add_patch(
                plt.Rectangle(self.start_point, 0, 0, fill=False, color='red')
            )
            self.canvas.draw()
            
    def on_right_click(self, event):
        if self.image is None:
            return
        if event.dblclick:
            self.ax.add_patch(
                plt.Circle(
                    (event.xdata, event.ydata),
                    10,
                    color='blue', fill=True)
            )
            self.canvas.draw()
            
    def on_drag(self, event):
        if self.image is None:
            return        
        if not self.dragging or not event.inaxes:
            return
        if event.dblclick:
            return
        x0, y0 = self.start_point
        x1, y1 = event.xdata, event.ydata
        self.rect.set_width(x1 - x0)
        self.rect.set_height(y1 - y0)
        self.rect.set_xy((min(x0, x1), min(y0, y1)))
        self.canvas.draw()\
            
    def on_release(self, event):
        if self.image is None:
            return
        if event.button == 3:
            return
        if self.dragging:
            self.dragging = False
            response = QMessageBox.question(self,
                                            "Confirm",
                                            "Keep the rectangle?",
                                            QMessageBox.Yes | QMessageBox.No)
            if response == QMessageBox.No:
                self.rect.remove()
            self.canvas.draw()
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = ImageViewr()
    mw.show()
    sys.exit(app.exec())