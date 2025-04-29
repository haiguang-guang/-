from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QTextEdit, QPushButton, QMessageBox,
                            QLabel, QFrame, QSplitter)
from PyQt6.QtGui import QIcon, QFont, QTextCharFormat, QColor, QSyntaxHighlighter, QTextDocument
from PyQt6.QtCore import Qt, QRegularExpression
import os
import difflib

class DiffHighlighter(QSyntaxHighlighter):
    """文本差异的语法高亮器"""
    def __init__(self, document, diff_type="added"):
        super().__init__(document)
        self.diff_type = diff_type
        
        # 添加的文本格式 (绿色背景)
        self.added_format = QTextCharFormat()
        self.added_format.setBackground(QColor("#E6FFED"))
        self.added_format.setForeground(QColor("#22863A"))
        
        # 删除的文本格式 (红色背景)
        self.removed_format = QTextCharFormat()
        self.removed_format.setBackground(QColor("#FFEEF0"))
        self.removed_format.setForeground(QColor("#CB2431"))
        
        # 修改的文本格式 (黄色背景)
        self.modified_format = QTextCharFormat()
        self.modified_format.setBackground(QColor("#FFF5B1"))
        self.modified_format.setForeground(QColor("#735C0F"))
        
    def highlightBlock(self, text):
        # 对于添加的文本块，开头有 "+"
        if self.diff_type == "added" and text.startswith("+"):
            self.setFormat(0, len(text), self.added_format)
        # 对于删除的文本块，开头有 "-"
        elif self.diff_type == "removed" and text.startswith("-"):
            self.setFormat(0, len(text), self.removed_format)
        # 对于修改的行，用 "!" 标记
        elif text.startswith("!"):
            self.setFormat(0, len(text), self.modified_format)

class TextDiff(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("文本差异比较")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题区域
        title_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/diff.png")
        if os.path.exists(icon_path):
            icon_label.setPixmap(QIcon(icon_path).pixmap(32, 32))
        
        title_label = QLabel("文本差异比较工具")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #6200EA;")
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        main_layout.addLayout(title_layout)
        
        # 说明文字
        info_label = QLabel("比较两段文本之间的差异。将原始文本粘贴到左侧，将修改后的文本粘贴到右侧，然后点击\"比较差异\"按钮。")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 13px; margin-bottom: 10px;")
        main_layout.addWidget(info_label)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #e0e0e0;")
        main_layout.addWidget(separator)
        
        # 创建输入区域的布局
        input_layout = QHBoxLayout()
        
        # 左侧（原始文本）
        left_layout = QVBoxLayout()
        left_label = QLabel("原始文本:")
        left_label.setFont(QFont("Arial", 12))
        self.left_text = QTextEdit()
        self.left_text.setPlaceholderText("在此粘贴原始文本...")
        self.left_text.setFont(QFont("Consolas", 10))
        self.left_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
                background-color: #fafafa;
            }
            QTextEdit:focus {
                border: 1px solid #6200EA;
                background-color: white;
            }
        """)
        left_layout.addWidget(left_label)
        left_layout.addWidget(self.left_text)
        
        # 右侧（修改后文本）
        right_layout = QVBoxLayout()
        right_label = QLabel("修改后文本:")
        right_label.setFont(QFont("Arial", 12))
        self.right_text = QTextEdit()
        self.right_text.setPlaceholderText("在此粘贴修改后的文本...")
        self.right_text.setFont(QFont("Consolas", 10))
        self.right_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
                background-color: #fafafa;
            }
            QTextEdit:focus {
                border: 1px solid #6200EA;
                background-color: white;
            }
        """)
        right_layout.addWidget(right_label)
        right_layout.addWidget(self.right_text)
        
        input_layout.addLayout(left_layout)
        input_layout.addLayout(right_layout)
        main_layout.addLayout(input_layout)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        self.compare_btn = QPushButton("比较差异")
        self.compare_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/compare.png")))
        self.compare_btn.clicked.connect(self.compare_text)
        self.compare_btn.setStyleSheet("""
            QPushButton {
                background-color: #6200EA;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7C4DFF;
            }
        """)
        
        self.clear_btn = QPushButton("清除")
        self.clear_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/clear.png")))
        self.clear_btn.clicked.connect(self.clear_text)
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
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.compare_btn)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch()
        
        main_layout.addLayout(btn_layout)
        
        # 差异结果区域
        result_label = QLabel("差异结果:")
        result_label.setFont(QFont("Arial", 12))
        main_layout.addWidget(result_label)
        
        self.diff_result = QTextEdit()
        self.diff_result.setReadOnly(True)
        self.diff_result.setPlaceholderText("差异比较结果将显示在这里...")
        self.diff_result.setFont(QFont("Consolas", 10))
        self.diff_result.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
                background-color: #f5f5f5;
                line-height: 1.4;
            }
        """)
        main_layout.addWidget(self.diff_result, 1)
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        main_layout.addWidget(self.status_label)
        
        # 创建语法高亮器
        self.diff_highlighter = DiffHighlighter(self.diff_result.document())
        
    def compare_text(self):
        try:
            # 获取两个文本框的内容
            left_content = self.left_text.toPlainText()
            right_content = self.right_text.toPlainText()
            
            if not left_content or not right_content:
                QMessageBox.warning(self, "警告", "请在两个文本框中都输入内容")
                return
            
            # 将文本分割成行
            left_lines = left_content.splitlines()
            right_lines = right_content.splitlines()
            
            # 计算差异
            self.status_label.setText("正在计算差异...")
            self.status_label.setStyleSheet("color: #6200EA;")
            
            diff = difflib.Differ()
            diff_result = list(diff.compare(left_lines, right_lines))
            
            # 显示差异结果
            self.diff_result.clear()
            self.diff_result.setPlainText("\n".join(diff_result))
            
            # 结果统计
            added = sum(1 for line in diff_result if line.startswith("+ "))
            removed = sum(1 for line in diff_result if line.startswith("- "))
            changed = sum(1 for line in diff_result if line.startswith("? "))
            
            self.status_label.setText(f"比较完成。发现 {added} 行新增, {removed} 行删除, {changed} 行变更。")
            self.status_label.setStyleSheet("color: #4CAF50;")
            
        except Exception as e:
            self.status_label.setText(f"比较失败: {str(e)}")
            self.status_label.setStyleSheet("color: #D32F2F;")
            QMessageBox.critical(self, "错误", f"比较文本时出错: {str(e)}")
    
    def clear_text(self):
        """清除所有文本区域的内容"""
        self.left_text.clear()
        self.right_text.clear()
        self.diff_result.clear()
        self.status_label.setText("已清除所有内容")
        self.status_label.setStyleSheet("color: #666; font-style: italic;") 