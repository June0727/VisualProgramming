import sys
import os
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.image import imread

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout,
    QWidget, QFileDialog, QListWidget, QHBoxLayout, QListWidgetItem, QMessageBox, QStatusBar
)
from PySide6.QtCore import Qt

class InteractivePlot(QMainWindow):
    def __init__(self):
        super().__init__()

        # 창의 기본 설정: 그래프 영역, 캔버스, 그리기 도구 및 버튼 초기화
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.axis('off')  # 축을 초기에 비활성화하여 이미지만 표시

        # 파일 목록을 표시할 QListWidget 설정
        self.file_list_widget = QListWidget()
        self.file_list_widget.itemClicked.connect(self.on_item_click)

        # 메인 위젯 및 레이아웃 설정
        layout = QHBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # 스테이터스 바 설정
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 왼쪽 레이아웃: 파일 목록
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.file_list_widget)

        # 레이아웃에 위젯 추가
        layout.addLayout(left_layout)
        layout.addWidget(self.canvas)

        # 마우스 드래그 상태 및 사각형 선택을 위한 변수 초기화
        self.dragging = False
        self.rect = None
        self.start_point = (0, 0)
        self.image = None

        # "Set Directory" 항목 추가
        self.file_list_widget.addItem("Set Directory")

        # 마우스 클릭 및 더블클릭 이벤트 연결
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_drag)
        self.canvas.mpl_connect('button_release_event', self.on_release)

    def set_directory(self):
        # 사용자가 선택한 디렉토리의 이미지 파일 목록을 QListWidget에 표시
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.file_list_widget.clear()
            self.file_list_widget.addItem("Set Directory")
            for file_name in os.listdir(directory):
                if file_name.lower().endswith(('.png', '.jpg')):
                    item = QListWidgetItem(file_name)
                    item.setData(Qt.UserRole, os.path.join(directory, file_name))
                    self.file_list_widget.addItem(item)

    def on_item_click(self, item):
        # 사용자가 "Set Directory" 항목을 클릭하면 디렉토리를 설정
        if item.text() == "Set Directory":
            self.set_directory()
        else:
            file_path = item.data(Qt.UserRole)
            self.status_bar.showMessage(file_path)  # 스테이터스 바에 파일 경로 표시
            self.load_image(file_path)

    def load_image(self, file_name):
        # 사용자가 선택한 이미지를 불러와서 캔버스에 표시
        self.image = imread(file_name)
        self.ax.clear()
        self.ax.imshow(self.image)
        self.ax.axis('on')
        self.canvas.draw()

    def on_click(self, event):
        if self.image is None:
            return
        # 마우스 클릭 이벤트 핸들러: 더블클릭 검출을 위해 클릭 횟수 계산
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
        # 우클릭 이벤트 핸들러: 클릭된 위치에 원을 그림
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
        # 마우스 드래그 이벤트 핸들러: 사각형의 위치와 크기를 실시간으로 조정
        if not self.dragging or not event.inaxes:
            return
        if event.dblclick:
            return
        x0, y0 = self.start_point
        x1, y1 = event.xdata, event.ydata
        self.rect.set_width(x1 - x0)
        self.rect.set_height(y1 - y0)
        self.rect.set_xy((min(x0, x1), min(y0, y1)))
        self.canvas.draw()

    def on_release(self, event):
        if self.image is None:
            return
        # 마우스 버튼 해제 이벤트 핸들러: 사용자가 사각형을 그린 후 마우스 버튼을 놓으면 호출됨.
        if event.button == 3:  # 우클릭인 경우는 무시.
            return
        if self.dragging:
            self.dragging = False
            response = QMessageBox.question(self,
                                            "Confirm",
                                            "Keep the rectangle?",
                                            QMessageBox.Yes | QMessageBox.No)
            if response == QMessageBox.No:
                self.rect.remove()  # 사용자가 'No'를 선택했을 때 사각형 삭제
            self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mwd = InteractivePlot()
    mwd.show()
    sys.exit(app.exec())
