from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, 
                            QFileDialog, QListWidget, QMessageBox)
from PyQt6.QtGui import QFont
import os

class FileRenamer(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("文件重命名")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        self.selected_files = []
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 选择文件按钮
        select_btn = QPushButton("选择文件")
        select_btn.clicked.connect(self.select_files)
        layout.addWidget(select_btn)
        
        # 选择的文件列表
        self.file_list = QListWidget()
        layout.addWidget(self.file_list)
        
        # 重命名规则
        rule_layout = QHBoxLayout()
        
        rule_label = QLabel("重命名规则:")
        rule_label.setFont(QFont("Arial", 12))
        rule_layout.addWidget(rule_label)
        
        self.rule_input = QLineEdit()
        self.rule_input.setFont(QFont("Arial", 12))
        self.rule_input.setPlaceholderText("例如: 文件{index} (使用{index}作为序号占位符)")
        rule_layout.addWidget(self.rule_input)
        
        layout.addLayout(rule_layout)
        
        # 重命名按钮
        rename_btn = QPushButton("重命名")
        rename_btn.clicked.connect(self.rename_files)
        layout.addWidget(rename_btn)
        
        # 帮助说明
        help_text = """
        重命名规则说明:
        - {index}: 序号占位符，如"文件{index}" → 文件1, 文件2, ...
        - {name}: 原文件名占位符(不含扩展名)
        - {ext}: 扩展名占位符
        """
        help_label = QLabel(help_text)
        help_label.setFont(QFont("Arial", 10))
        layout.addWidget(help_label)
        
    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择文件")
        
        if files:
            self.selected_files = files
            self.file_list.clear()
            for file in files:
                self.file_list.addItem(os.path.basename(file))
                
    def rename_files(self):
        if not self.selected_files:
            QMessageBox.warning(self, "警告", "请先选择文件")
            return
            
        rule = self.rule_input.text()
        if not rule:
            QMessageBox.warning(self, "警告", "请输入重命名规则")
            return
        
        try:
            renamed_count = 0
            
            for i, file_path in enumerate(self.selected_files):
                directory = os.path.dirname(file_path)
                filename = os.path.basename(file_path)
                name, ext = os.path.splitext(filename)
                
                # 应用规则
                new_name = rule.replace("{index}", str(i+1))
                new_name = new_name.replace("{name}", name)
                new_name = new_name.replace("{ext}", ext)
                
                # 确保有扩展名
                if not new_name.endswith(ext):
                    new_name += ext
                    
                new_path = os.path.join(directory, new_name)
                
                # 重命名文件
                os.rename(file_path, new_path)
                renamed_count += 1
                
            QMessageBox.information(self, "成功", f"已重命名 {renamed_count} 个文件")
            
            # 更新列表
            self.file_list.clear()
            self.selected_files = []
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"重命名文件时出错: {str(e)}") 