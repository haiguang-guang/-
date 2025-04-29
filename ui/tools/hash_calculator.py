from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                           QComboBox, QPushButton, QTextEdit, 
                           QHBoxLayout, QFileDialog, QMessageBox, QDialog, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import hashlib
import sys
try:
    import pyperclip
except ImportError:
    # 如果没有 pyperclip，提供一个替代方案
    class Pyperclip:
        def copy(self, text):
            pass
    pyperclip = Pyperclip()

class HashCalculator(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("哈希计算器")
        self.setModal(True)
        self.md5_hash = ""
        self.sha1_hash = ""
        self.sha256_hash = ""
        self.setupUI()
        
    def setupUI(self):
        layout = QVBoxLayout(self)
        
        # 文本显示区域
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText("请点击\"选择文件\"按钮选择要计算哈希值的文件")
        layout.addWidget(self.text_edit)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        # 选择文件按钮
        self.select_btn = QPushButton("选择文件")
        self.select_btn.clicked.connect(self.calculate_hash)
        btn_layout.addWidget(self.select_btn)
        
        # 复制MD5按钮
        self.copy_md5_btn = QPushButton("复制MD5")
        self.copy_md5_btn.clicked.connect(self.copy_md5)
        btn_layout.addWidget(self.copy_md5_btn)
        
        # 复制SHA1按钮
        self.copy_sha1_btn = QPushButton("复制SHA1")
        self.copy_sha1_btn.clicked.connect(self.copy_sha1)
        btn_layout.addWidget(self.copy_sha1_btn)
        
        # 复制SHA256按钮
        self.copy_sha256_btn = QPushButton("复制SHA256")
        self.copy_sha256_btn.clicked.connect(self.copy_sha256)
        btn_layout.addWidget(self.copy_sha256_btn)
        
        layout.addLayout(btn_layout)
    
    def calculate_hash(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "选择文件")
            if not file_path:
                return
                
            self.text_edit.setPlainText("正在计算哈希值，请稍候...")
            QApplication.processEvents()  # 更新UI
            
            with open(file_path, 'rb') as f:
                content = f.read()
                self.md5_hash = hashlib.md5(content).hexdigest()
                self.sha1_hash = hashlib.sha1(content).hexdigest()
                self.sha256_hash = hashlib.sha256(content).hexdigest()
                
            result = f"文件: {file_path}\n\nMD5: {self.md5_hash}\nSHA1: {self.sha1_hash}\nSHA256: {self.sha256_hash}"
            self.text_edit.setPlainText(result)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"计算哈希值时出错: {str(e)}")
    
    def copy_md5(self):
        try:
            if not self.md5_hash:
                QMessageBox.warning(self, "警告", "请先选择文件计算哈希值")
                return
            pyperclip.copy(self.md5_hash)
            QMessageBox.information(self, "成功", "MD5哈希值已复制到剪贴板")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"复制MD5值时出错: {str(e)}")
    
    def copy_sha1(self):
        try:
            if not self.sha1_hash:
                QMessageBox.warning(self, "警告", "请先选择文件计算哈希值")
                return
            pyperclip.copy(self.sha1_hash)
            QMessageBox.information(self, "成功", "SHA1哈希值已复制到剪贴板")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"复制SHA1值时出错: {str(e)}")
    
    def copy_sha256(self):
        try:
            if not self.sha256_hash:
                QMessageBox.warning(self, "警告", "请先选择文件计算哈希值")
                return
            pyperclip.copy(self.sha256_hash)
            QMessageBox.information(self, "成功", "SHA256哈希值已复制到剪贴板")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"复制SHA256值时出错: {str(e)}") 