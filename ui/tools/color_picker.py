from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QColorDialog, QMessageBox, QDialog)
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt
import sys
try:
    import pyperclip
except ImportError:
    # 如果没有 pyperclip，提供一个替代方案
    class Pyperclip:
        def copy(self, text):
            pass
    pyperclip = Pyperclip()

class ColorPicker(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("颜色选择器")
        self.setModal(True)
        self.current_color = QColor(255, 255, 255)  # 初始化为白色
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 颜色预览区域
        self.color_preview = QLabel()
        self.color_preview.setMinimumHeight(100)
        self.color_preview.setStyleSheet("background-color: white; border: 1px solid #ddd;")
        layout.addWidget(self.color_preview)
        
        # 颜色信息显示
        self.color_info = QLabel("RGB: 255, 255, 255\nHEX: #FFFFFF")
        self.color_info.setFont(QFont("Arial", 12))
        self.color_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.color_info)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        # 选择颜色按钮
        self.pick_btn = QPushButton("选择颜色")
        self.pick_btn.clicked.connect(self.pick_color)
        btn_layout.addWidget(self.pick_btn)
        
        # 复制RGB按钮
        self.copy_rgb_btn = QPushButton("复制RGB")
        self.copy_rgb_btn.clicked.connect(self.copy_rgb)
        btn_layout.addWidget(self.copy_rgb_btn)
        
        # 复制HEX按钮
        self.copy_hex_btn = QPushButton("复制HEX")
        self.copy_hex_btn.clicked.connect(self.copy_hex)
        btn_layout.addWidget(self.copy_hex_btn)
        
        layout.addLayout(btn_layout)
        
        # 初始化颜色预览
        self.update_color_preview(self.current_color)
        
    def pick_color(self):
        try:
            color = QColorDialog.getColor(initial=self.current_color, parent=self)
            if color.isValid():
                self.current_color = color
                self.update_color_preview(color)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"选择颜色时出错: {str(e)}")
    
    def update_color_preview(self, color):
        try:
            # 更新预览区域
            self.color_preview.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ddd;")
            
            # 更新颜色信息
            rgb = f"RGB: {color.red()}, {color.green()}, {color.blue()}"
            hex_code = f"HEX: {color.name()}"
            self.color_info.setText(f"{rgb}\n{hex_code}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新颜色预览时出错: {str(e)}")
    
    def copy_rgb(self):
        try:
            if self.current_color is None:
                QMessageBox.warning(self, "警告", "请先选择颜色")
                return
                
            color_text = f"rgb({self.current_color.red()}, {self.current_color.green()}, {self.current_color.blue()})"
            pyperclip.copy(color_text)
            QMessageBox.information(self, "成功", "RGB颜色值已复制到剪贴板")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"复制RGB值时出错: {str(e)}")
    
    def copy_hex(self):
        try:
            if self.current_color is None:
                QMessageBox.warning(self, "警告", "请先选择颜色")
                return
                
            color_text = self.current_color.name()
            pyperclip.copy(color_text)
            QMessageBox.information(self, "成功", "HEX颜色值已复制到剪贴板")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"复制HEX值时出错: {str(e)}") 