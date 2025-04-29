from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, 
                            QPushButton, QHBoxLayout, QMessageBox, QApplication)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QClipboard

class ClipboardTool(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("剪贴板工具")
        self.setMinimumSize(600, 400)
        self.setModal(True)
        
        # 获取系统剪贴板
        try:
            # 使用QApplication而不是QGuiApplication
            self.clipboard = QApplication.clipboard()
            
            # 创建历史记录列表
            self.history = []
            
            self.init_ui()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"初始化剪贴板工具时出错: {str(e)}")
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 文本编辑区域
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("这里将显示剪贴板内容")
        layout.addWidget(self.text_edit)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        # 获取剪贴板内容按钮
        self.get_btn = QPushButton("获取剪贴板内容")
        self.get_btn.clicked.connect(self.get_clipboard)
        btn_layout.addWidget(self.get_btn)
        
        # 设置剪贴板内容按钮
        self.set_btn = QPushButton("设置剪贴板内容")
        self.set_btn.clicked.connect(self.set_clipboard)
        btn_layout.addWidget(self.set_btn)
        
        # 清空按钮
        self.clear_btn = QPushButton("清空")
        self.clear_btn.clicked.connect(self.clear_content)
        btn_layout.addWidget(self.clear_btn)
        
        layout.addLayout(btn_layout)
        
        # 监控剪贴板变化
        try:
            self.clipboard.dataChanged.connect(self.clipboard_changed)
            
            # 自动获取当前剪贴板内容
            QTimer.singleShot(100, self.get_clipboard)
        except Exception as e:
            self.text_edit.setPlainText(f"无法连接到剪贴板: {str(e)}")
        
    def get_clipboard(self):
        try:
            text = self.clipboard.text()
            self.text_edit.setPlainText(text)
        except Exception as e:
            self.text_edit.setPlainText(f"获取剪贴板内容出错: {str(e)}")
        
    def set_clipboard(self):
        try:
            text = self.text_edit.toPlainText()
            if text:
                self.clipboard.setText(text, QClipboard.Mode.Clipboard)
                QMessageBox.information(self, "成功", "内容已复制到剪贴板")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"设置剪贴板内容出错: {str(e)}")
            
    def clear_content(self):
        self.text_edit.clear()
        
    def clipboard_changed(self):
        try:
            # 当剪贴板内容变化时调用
            if not self.isVisible():
                return
                
            text = self.clipboard.text()
            if text and text not in self.history:
                self.history.append(text)
                # 最多保存最近的10条记录
                if len(self.history) > 10:
                    self.history.pop(0)
                self.text_edit.setPlainText(text)
        except Exception as e:
            self.text_edit.setPlainText(f"处理剪贴板变化出错: {str(e)}") 