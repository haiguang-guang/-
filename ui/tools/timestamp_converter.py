from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton)
from PyQt6.QtGui import QFont
from datetime import datetime

class TimestampConverter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("时间戳转换")
        self.setMinimumWidth(400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        input_label = QLabel("输入时间戳:")
        input_label.setFont(QFont("Arial", 12))
        layout.addWidget(input_label)
        
        self.entry = QLineEdit()
        self.entry.setFont(QFont("Arial", 12))
        layout.addWidget(self.entry)
        
        self.result_label = QLabel("")
        self.result_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.result_label)
        
        convert_btn = QPushButton("转换")
        convert_btn.clicked.connect(self.convert)
        layout.addWidget(convert_btn)
    
    def convert(self):
        try:
            timestamp = float(self.entry.text())
            dt = datetime.fromtimestamp(timestamp)
            self.result_label.setText(f"转换结果: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        except ValueError:
            self.result_label.setText("请输入有效的时间戳") 