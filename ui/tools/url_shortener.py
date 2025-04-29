from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QLineEdit, QPushButton, QMessageBox,
                            QLabel, QFrame)
from PyQt6.QtGui import QIcon, QFont, QGuiApplication
from PyQt6.QtCore import Qt, QUrl
import os
import requests
import json

class URLShortener(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("URL缩短器")
        self.setModal(True)
        self.setMinimumSize(600, 400)
        self.shortened_url = None
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题区域
        title_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/link.png")
        if os.path.exists(icon_path):
            icon_label.setPixmap(QIcon(icon_path).pixmap(32, 32))
        
        title_label = QLabel("URL缩短工具")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1976D2;")
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        main_layout.addLayout(title_layout)
        
        # 说明文字
        info_label = QLabel("将长URL转换为短URL，便于分享和使用。使用TinyURL API进行缩短。")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 13px; margin-bottom: 10px;")
        main_layout.addWidget(info_label)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #e0e0e0;")
        main_layout.addWidget(separator)
        
        # 输入框
        input_label = QLabel("输入长URL:")
        input_label.setFont(QFont("Arial", 12))
        main_layout.addWidget(input_label)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com/very/long/url/path...")
        self.url_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: #fafafa;
            }
            QLineEdit:focus {
                border: 1px solid #1976D2;
                background-color: white;
            }
        """)
        main_layout.addWidget(self.url_input)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        self.shorten_btn = QPushButton("缩短URL")
        self.shorten_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/compress.png")))
        self.shorten_btn.clicked.connect(self.shorten_url)
        self.shorten_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1E88E5;
            }
        """)
        btn_layout.addWidget(self.shorten_btn)
        
        self.clear_btn = QPushButton("清除")
        self.clear_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/clear.png")))
        self.clear_btn.clicked.connect(self.clear_fields)
        self.clear_btn.setStyleSheet("""
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
        btn_layout.addWidget(self.clear_btn)
        
        main_layout.addLayout(btn_layout)
        
        # 结果区域
        result_label = QLabel("缩短后的URL:")
        result_label.setFont(QFont("Arial", 12))
        main_layout.addWidget(result_label)
        
        self.result_output = QLineEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText("缩短后的URL将显示在这里...")
        self.result_output.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: #f0f0f0;
            }
        """)
        main_layout.addWidget(self.result_output)
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        main_layout.addWidget(self.status_label)
        
        # 复制按钮
        copy_layout = QHBoxLayout()
        
        self.copy_btn = QPushButton("复制短URL")
        self.copy_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/copy.png")))
        self.copy_btn.clicked.connect(self.copy_url)
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }
        """)
        copy_layout.addStretch()
        copy_layout.addWidget(self.copy_btn)
        copy_layout.addStretch()
        
        main_layout.addLayout(copy_layout)
        main_layout.addStretch()
        
    def shorten_url(self):
        try:
            long_url = self.url_input.text().strip()
            if not long_url:
                QMessageBox.warning(self, "警告", "请输入要缩短的URL")
                return
                
            if not (long_url.startswith("http://") or long_url.startswith("https://")):
                long_url = "https://" + long_url
                
            # 验证URL格式
            url = QUrl(long_url)
            if not url.isValid():
                QMessageBox.warning(self, "警告", "请输入有效的URL")
                return
                
            self.status_label.setText("正在缩短URL...")
            self.status_label.setStyleSheet("color: #1976D2;")
            
            # 使用TinyURL API
            api_url = f"https://tinyurl.com/api-create.php?url={long_url}"
            response = requests.get(api_url)
            
            if response.status_code == 200:
                short_url = response.text
                self.shortened_url = short_url
                self.result_output.setText(short_url)
                
                self.status_label.setText("URL缩短成功!")
                self.status_label.setStyleSheet("color: #4CAF50;")
            else:
                raise Exception(f"API返回错误: {response.status_code}")
                
        except Exception as e:
            self.status_label.setText(f"缩短URL失败: {str(e)}")
            self.status_label.setStyleSheet("color: #D32F2F;")
            QMessageBox.critical(self, "错误", f"缩短URL时出错: {str(e)}")
            
    def clear_fields(self):
        self.url_input.clear()
        self.result_output.clear()
        self.shortened_url = None
        self.status_label.setText("准备就绪")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        
    def copy_url(self):
        try:
            short_url = self.result_output.text()
            if not short_url:
                QMessageBox.warning(self, "警告", "没有可复制的短URL")
                return
                
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(short_url)
            
            self.status_label.setText("短URL已复制到剪贴板")
            QMessageBox.information(self, "成功", "短URL已复制到剪贴板")
        except Exception as e:
            self.status_label.setText(f"复制URL失败: {str(e)}")
            self.status_label.setStyleSheet("color: #D32F2F;")
            QMessageBox.critical(self, "错误", f"复制URL时出错: {str(e)}") 