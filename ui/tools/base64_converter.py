from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, 
                            QPushButton, QHBoxLayout)
import base64

class Base64Converter(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Base64编解码")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 文本输入区域
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("输入要编码或解码的文本")
        layout.addWidget(self.text_edit)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        # 编码按钮
        self.encode_btn = QPushButton("编码")
        self.encode_btn.clicked.connect(self.encode_text)
        btn_layout.addWidget(self.encode_btn)
        
        # 解码按钮
        self.decode_btn = QPushButton("解码")
        self.decode_btn.clicked.connect(self.decode_text)
        btn_layout.addWidget(self.decode_btn)
        
        layout.addLayout(btn_layout)
        
    def encode_text(self):
        text = self.text_edit.toPlainText()
        if text:
            encoded = base64.b64encode(text.encode()).decode()
            self.text_edit.setPlainText(encoded)
            
    def decode_text(self):
        text = self.text_edit.toPlainText()
        if text:
            try:
                decoded = base64.b64decode(text).decode()
                self.text_edit.setPlainText(decoded)
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "解码错误", f"无法解码: {str(e)}") 