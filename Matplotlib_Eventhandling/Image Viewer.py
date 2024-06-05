import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListWidget,
    QListWidgetItem, 
    QHBoxLayout, QVBoxLayout, QWidget, QFileDialog, QMenuBar, 
    QStatusBar, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.image as mpimg


class ImageCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setStyleSheet("background-color: #2f2f2f;")
        self.ax.axis('off')  # Hide the axis
        self.fig.subplots_adjust(
            left=0, right=1,
            top=1, bottom=0
        )

    def display_image(self, image_path):
        self.ax.clear()
        img = mpimg.imread(image_path)
        self.ax.imshow(img)
        self.ax.axis('off')  # Hide the axis
        self.fig.subplots_adjust(
            left=0, right=1,
            top=1, bottom=0
        )
        self.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PNG Viewer")

        # Main layout setup
        main_layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        right_layout = QVBoxLayout()
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        # QListWidget setup
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        main_layout.addWidget(self.list_widget)
        
        # Matplotlib FigureCanvas setup
        self.canvas = ImageCanvas(self)
        
        # NavigationToolbar setup
        self.nav_toolbar = NavigationToolbar(self.canvas, self)
        
        right_layout.addWidget(self.nav_toolbar)
        right_layout.addWidget(self.canvas)
        
        main_layout.addWidget(right_widget)

        # StatusBar setup
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Menubar setup
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        menubar.setNativeMenuBar(False)

        # Directory selection action
        open_action = QAction("Open Directory", self)
        open_action.triggered.connect(self.open_directory)
        file_menu.addAction(open_action)
        
        self.dragging = False
        self.rect = None
        self.start_point = (0, 0)
        self.click_count = 0  
        
        # Connect mouse events
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        
        self.show()

    def open_directory(self):
        # Open directory dialog
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.list_widget.clear()
            # List PNG and JPG files in the directory
            image_files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            for image_file in image_files:
                item = QListWidgetItem(image_file)
                item.setData(Qt.UserRole, os.path.join(directory, image_file))
                self.list_widget.addItem(item)
    
    def on_item_clicked(self, item):
        # Display selected image
        file_path = item.data(Qt.UserRole)
        self.canvas.display_image(file_path)
        self.status_bar.showMessage(file_path)
        
    def on_click(self, event):
        if event.button == 3:  # Right-click
            self.on_right_click(event)
        else:
            self.dragging = True
            self.start_point = (event.xdata, event.ydata)
            self.rect = self.ax.add_patch(
                plt.Rectangle(
                    self.start_point, 
                    0, 0, 
                    fill=False, color='red'
                )
            )
            self.canvas.draw()
            
    def on_right_click(self, event):
        # Handle right-click event
        self.ax.add_patch(
            plt.Circle(
                (event.xdata, event.ydata), 
                10, 
                color='blue', fill=True
            )
        )
        self.canvas.draw()
            
    def on_drag(self, event):
        # Handle drag event
        if not self.dragging or event.inaxes != self.canvas.ax:
            return
        x0, y0 = self.start_point
        x1, y1 = event.xdata, event.ydata
        self.rect.set_width(x1 - x0)
        self.rect.set_height(y1 - y0)
        self.rect.set_xy((min(x0, x1), min(y0, y1)))
        self.canvas.draw()
        
    def on_release(self, event):
        # Handle mouse button release event
        if event.button == 3:  # Ignore right-click
            return
        if self.dragging:
            self.dragging = False
            response = QMessageBox.question(self, 
                                            "Confirm", 
                                            "Keep the rectangle?", 
                                            QMessageBox.Yes | QMessageBox.No)
            if response == QMessageBox.No:
                self.rect.remove()  # Remove rectangle if 'No' is selected
            self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
