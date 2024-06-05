import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Event Handling with Matplotlib and PySide6")
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure) 
        self.ax = self.figure.add_subplot(111)  
        self.ax.plot([1, 2, 3, 4], [1, 4, 9, 16])
        
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        layout = QVBoxLayout()
        widget = QWidget()
        self.setCentralWidget(widget)
        widget.setLayout(layout)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()
        
        self.canvas.mpl_connect("button_press_event", self.on_press)
        self.canvas.mpl_connect("button_release_event", self.on_release)
        #self.canvas.mpl_connect("motion_notify_event", self.on_motion)
        self.canvas.mpl_connect("key_press_event", self.on_key_press)
        self.canvas.mpl_connect("key_release_event", self.on_key_release)
        
    def on_press(self, event):
        print(f"Mouse button pressed at ({event.xdata:.2f}, {event.ydata:.2f})")
        print(f"Mouse button is ({event.button}, it is clicked with the pressed key {event.key})")
        print(f"Mouse button is double clicked: {event.dblclick}")
        print('------------------------\n')

    # 마우스 버튼이 떼어졌을 때 호출되는 메소드
    def on_release(self, event):
        print("Mouse button released")
        print('------------------------\n')

    # 마우스가 움직였을 때 호출되는 메소드
    #def on_motion(self, event):
        #if event.xdata is not None and event.ydata is not None:  # 마우스 위치가 유효한 경우
        #    print(f"Mouse moved to ({event.xdata:.2f}, {event.ydata:.2f})")
        #    print('------------------------')

    # 키보드 키가 눌렸을 때 호출되는 메소드
    def on_key_press(self, event):
        print(f"Key pressed: {event.key}")
        print('------------------------\n')

    # 키보드 키가 떼어졌을 때 호출되는 메소드
    def on_key_release(self, event):
        print("Key released")
        print('------------------------\n')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()    
    main_window.show()            
    sys.exit(app.exec())          