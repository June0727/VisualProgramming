import sys, os
from datetime import datetime

from PySide6.QtWidgets import ( 
                               QApplication, QMainWindow, QStatusBar,
                               QLabel, QProgressBar, QPushButton,
                               )

from PySide6.QtCore import QTimer

class MW(QMainWindow):
    
    def __init__(self):
        
        super(MW, self).__init__()
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.timer0 = QTimer(self)
        self.timer0.timeout.connect(self.update_clk)
        self.timer0.start(1000)
        
        self.clk_label = QLabel()
        self.status_bar.addPermanentWidget(self.clk_label)
        
        self.progress_bar = QProgressBar(self, minimum=0, maximum=100)
        self.status_bar.addWidget(self.progress_bar, 2)
        
        self.btn = QPushButton('Start Progress')
        self.btn.clicked.connect(self.start_progress)
        self.setCentralWidget(self.btn)
        
        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.update_progress)
        self.progress_value = 0
        
        self.show()
        
    def start_progress(self):
        self.progress_value = 0
        self.progress_bar.reset()
        self.progress_bar.setValue(self.progress_value)
        self.timer1.start(100)
        self.status_bar.showMessage('Progress Started...', 2000)
        
    def update_clk(self):
        now = datetime.now()
        now_str = now.strftime('%H:%M:%S')
        self.clk_label.setText(now_str)
        
    def update_progress(self):
        if self.progress_value < 100:
            self.progress_value += 1 
            self.progress_bar.setValue(self.progress_value)
        else:   
            self.timer1.stop()
            self.status_bar.showMessage('Progress completed...', 2000)
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = MW()
    sys.exit(app.exec())
