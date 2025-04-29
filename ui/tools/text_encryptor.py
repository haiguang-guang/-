from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QTextEdit, QPushButton, QMessageBox,
                            QLabel, QFrame, QSplitter)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt
from cryptography.fernet import Fernet
import os
import sys
try:
    import pyperclip
except ImportError:
    # 如果没有 pyperclip，提供一个替代方案
    class Pyperclip:
        def copy(self, text):
            pass
    pyperclip = Pyperclip()

class TextEncryptor(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("文本加密/解密")
        self.setModal(True)
        self.setMinimumSize(650, 500)
        self.current_key = None
        self.current_result = None
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题区域
        title_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/encrypt.png")
        if os.path.exists(icon_path):
            icon_label.setPixmap(QIcon(icon_path).pixmap(32, 32))
        
        title_label = QLabel("文本加密与解密工具")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2E7D32;")
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        main_layout.addLayout(title_layout)
        
        # 说明文字
        info_label = QLabel("使用强大的加密算法保护您的文本信息安全。加密后会生成密钥，解密时需要提供正确的密钥。")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 13px; margin-bottom: 10px;")
        main_layout.addWidget(info_label)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #e0e0e0;")
        main_layout.addWidget(separator)
        
        # 文本编辑区域
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("在此输入要加密或解密的文本...")
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: #fafafa;
            }
            QTextEdit:focus {
                border: 1px solid #2E7D32;
                background-color: white;
            }
        """)
        main_layout.addWidget(self.text_edit)
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        main_layout.addWidget(self.status_label)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        # 加密按钮
        self.encrypt_btn = QPushButton("加密文本")
        self.encrypt_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/lock.png")))
        self.encrypt_btn.clicked.connect(self.encrypt)
        self.encrypt_btn.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        btn_layout.addWidget(self.encrypt_btn)
        
        # 解密按钮
        self.decrypt_btn = QPushButton("解密文本")
        self.decrypt_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/unlock.png")))
        self.decrypt_btn.clicked.connect(self.decrypt)
        self.decrypt_btn.setStyleSheet("""
            QPushButton {
                background-color: #0277BD;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0288D1;
            }
        """)
        btn_layout.addWidget(self.decrypt_btn)
        
        # 复制密钥按钮
        self.copy_key_btn = QPushButton("复制密钥")
        self.copy_key_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/key.png")))
        self.copy_key_btn.clicked.connect(self.copy_key)
        self.copy_key_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF8F00;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFA000;
            }
        """)
        btn_layout.addWidget(self.copy_key_btn)
        
        # 复制结果按钮
        self.copy_result_btn = QPushButton("复制结果")
        self.copy_result_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/copy.png")))
        self.copy_result_btn.clicked.connect(self.copy_result)
        self.copy_result_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #9E9E9E;
            }
        """)
        btn_layout.addWidget(self.copy_result_btn)
        
        main_layout.addLayout(btn_layout)
        
    def encrypt(self):
        try:
            text = self.text_edit.toPlainText()
            if not text:
                QMessageBox.warning(self, "警告", "请输入要加密的文本")
                return
                
            self.status_label.setText("正在加密...")
            self.status_label.setStyleSheet("color: #2E7D32;")
            
            self.current_key = Fernet.generate_key()
            f = Fernet(self.current_key)
            self.current_result = f.encrypt(text.encode())
            
            result_text = f"密钥: {self.current_key.decode()}\n加密结果: {self.current_result.decode()}"
            self.text_edit.setPlainText(result_text)
            
            self.status_label.setText("加密成功！密钥已生成，请妥善保管。")
            
            QMessageBox.information(self, "成功", "文本已成功加密！\n请保存生成的密钥，解密时将需要使用。")
        except Exception as e:
            self.status_label.setText(f"加密失败: {str(e)}")
            self.status_label.setStyleSheet("color: #D32F2F;")
            QMessageBox.critical(self, "错误", f"加密时出错: {str(e)}")
            
    def decrypt(self):
        try:
            text = self.text_edit.toPlainText()
            if not text:
                QMessageBox.warning(self, "警告", "请输入要解密的文本")
                return
                
            self.status_label.setText("正在解密...")
            self.status_label.setStyleSheet("color: #0277BD;")
                
            lines = text.split('\n')
            if len(lines) < 2:
                raise ValueError("请提供密钥和加密文本，格式为：\n密钥: xxx\n加密结果: xxx")
                
            key = lines[0].split(': ')[1].encode()
            encrypted = lines[1].split(': ')[1].encode()
            
            f = Fernet(key)
            decrypted = f.decrypt(encrypted)
            self.current_result = decrypted
            self.text_edit.setPlainText(decrypted.decode())
            
            self.status_label.setText("解密成功！文本已恢复。")
            
            QMessageBox.information(self, "成功", "文本已成功解密！")
        except Exception as e:
            self.status_label.setText(f"解密失败: {str(e)}")
            self.status_label.setStyleSheet("color: #D32F2F;")
            QMessageBox.critical(self, "错误", f"解密时出错: {str(e)}")
    
    def copy_key(self):
        try:
            if not self.current_key:
                QMessageBox.warning(self, "警告", "请先进行加密操作生成密钥")
                return
                
            pyperclip.copy(self.current_key.decode())
            self.status_label.setText("密钥已复制到剪贴板！")
            QMessageBox.information(self, "成功", "密钥已复制到剪贴板")
        except Exception as e:
            self.status_label.setText(f"复制密钥失败: {str(e)}")
            self.status_label.setStyleSheet("color: #D32F2F;")
            QMessageBox.critical(self, "错误", f"复制密钥时出错: {str(e)}")
    
    def copy_result(self):
        try:
            if not self.current_result:
                QMessageBox.warning(self, "警告", "请先进行加密或解密操作")
                return
                
            pyperclip.copy(self.current_result.decode())
            self.status_label.setText("结果已复制到剪贴板！")
            QMessageBox.information(self, "成功", "结果已复制到剪贴板")
        except Exception as e:
            self.status_label.setText(f"复制结果失败: {str(e)}")
            self.status_label.setStyleSheet("color: #D32F2F;")
            QMessageBox.critical(self, "错误", f"复制结果时出错: {str(e)}") 