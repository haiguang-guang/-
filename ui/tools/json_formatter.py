from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, 
                            QPushButton, QHBoxLayout, QMessageBox,
                            QLabel, QFrame, QSplitter, QComboBox)
from PyQt6.QtGui import QIcon, QFont, QColor, QTextCharFormat, QSyntaxHighlighter, QGuiApplication
from PyQt6.QtCore import Qt, QRegularExpression
import json
import os

class JsonHighlighter(QSyntaxHighlighter):
    """JSON语法高亮器"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # 字符串格式
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#689F38"))
        self.highlighting_rules.append((QRegularExpression('"[^"]*"'), string_format))
        
        # 数字格式
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#F57C00"))
        self.highlighting_rules.append((QRegularExpression(r'\b\d+\b'), number_format))
        
        # 布尔值和null格式
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#7B1FA2"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = ['true', 'false', 'null']
        for word in keywords:
            pattern = QRegularExpression(r'\b' + word + r'\b')
            self.highlighting_rules.append((pattern, keyword_format))
        
        # 冒号格式
        colon_format = QTextCharFormat()
        colon_format.setForeground(QColor("#546E7A"))
        self.highlighting_rules.append((QRegularExpression(':'), colon_format))
        
        # 括号格式
        bracket_format = QTextCharFormat()
        bracket_format.setForeground(QColor("#1565C0"))
        bracket_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((QRegularExpression(r'[\[\]\{\}]'), bracket_format))
            
    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

class JsonFormatter(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("JSON格式化")
        self.setMinimumSize(700, 550)
        self.setModal(True)
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题区域
        title_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/json.png")
        if os.path.exists(icon_path):
            icon_label.setPixmap(QIcon(icon_path).pixmap(32, 32))
        
        title_label = QLabel("JSON格式化工具")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1565C0;")
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        main_layout.addLayout(title_layout)
        
        # 说明文字
        info_label = QLabel("美化或压缩JSON数据，提高可读性或减小数据体积。支持语法高亮显示。")
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
        self.text_edit.setPlaceholderText("在此输入要格式化的JSON...")
        self.text_edit.setFont(QFont("Consolas", 12))
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
                background-color: #fafafa;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border: 1px solid #1565C0;
                background-color: white;
            }
        """)
        
        # 设置JSON语法高亮
        self.highlighter = JsonHighlighter(self.text_edit.document())
        
        main_layout.addWidget(self.text_edit, 1)
        
        # 格式选项
        options_layout = QHBoxLayout()
        
        options_label = QLabel("缩进空格数:")
        options_label.setStyleSheet("color: #666;")
        
        self.indent_combo = QComboBox()
        self.indent_combo.addItems(["2", "4", "8"])
        self.indent_combo.setCurrentIndex(1)  # 默认4空格
        self.indent_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
                background: white;
                min-width: 60px;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
        """)
        
        options_layout.addWidget(options_label)
        options_layout.addWidget(self.indent_combo)
        options_layout.addStretch()
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        options_layout.addWidget(self.status_label)
        
        main_layout.addLayout(options_layout)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        # 格式化按钮
        self.format_btn = QPushButton("格式化")
        self.format_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/format.png")))
        self.format_btn.clicked.connect(self.format_json)
        self.format_btn.setStyleSheet("""
            QPushButton {
                background-color: #1565C0;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        btn_layout.addWidget(self.format_btn)
        
        # 压缩按钮
        self.compress_btn = QPushButton("压缩")
        self.compress_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/compress.png")))
        self.compress_btn.clicked.connect(self.compress_json)
        self.compress_btn.setStyleSheet("""
            QPushButton {
                background-color: #00796B;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00897B;
            }
        """)
        btn_layout.addWidget(self.compress_btn)
        
        # 验证按钮
        self.validate_btn = QPushButton("验证")
        self.validate_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/check.png")))
        self.validate_btn.clicked.connect(self.validate_json)
        self.validate_btn.setStyleSheet("""
            QPushButton {
                background-color: #455A64;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #546E7A;
            }
        """)
        btn_layout.addWidget(self.validate_btn)
        
        # 复制按钮
        self.copy_btn = QPushButton("复制")
        self.copy_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/copy.png")))
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.copy_btn.setStyleSheet("""
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
        btn_layout.addWidget(self.copy_btn)
        
        main_layout.addLayout(btn_layout)
        
    def format_json(self):
        text = self.text_edit.toPlainText()
        if not text:
            return
            
        try:
            self.status_label.setText("正在格式化...")
            self.status_label.setStyleSheet("color: #1565C0;")
            
            indent = int(self.indent_combo.currentText())
            data = json.loads(text)
            formatted = json.dumps(data, indent=indent, ensure_ascii=False)
            self.text_edit.setPlainText(formatted)
            
            self.status_label.setText("格式化成功")
            self.status_label.setStyleSheet("color: #2E7D32;")
        except Exception as e:
            self.status_label.setText(f"格式化错误: {str(e)}")
            self.status_label.setStyleSheet("color: #D32F2F;")
            QMessageBox.warning(self, "格式化错误", f"JSON格式错误: {str(e)}")
            
    def compress_json(self):
        text = self.text_edit.toPlainText()
        if not text:
            return
            
        try:
            self.status_label.setText("正在压缩...")
            self.status_label.setStyleSheet("color: #00796B;")
            
            data = json.loads(text)
            compressed = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
            self.text_edit.setPlainText(compressed)
            
            # 计算压缩率
            original_size = len(text)
            compressed_size = len(compressed)
            reduction = (original_size - compressed_size) / original_size * 100
            
            self.status_label.setText(f"压缩成功 (减少了 {reduction:.1f}%)")
            self.status_label.setStyleSheet("color: #2E7D32;")
        except Exception as e:
            self.status_label.setText(f"压缩错误: {str(e)}")
            self.status_label.setStyleSheet("color: #D32F2F;")
            QMessageBox.warning(self, "压缩错误", f"JSON格式错误: {str(e)}")
    
    def validate_json(self):
        """验证JSON是否有效"""
        text = self.text_edit.toPlainText()
        if not text:
            self.status_label.setText("请先输入JSON数据")
            self.status_label.setStyleSheet("color: #FF9800;")
            return
            
        try:
            self.status_label.setText("正在验证...")
            self.status_label.setStyleSheet("color: #455A64;")
            
            data = json.loads(text)
            
            # 计算JSON统计信息
            stats = self.get_json_stats(data)
            
            self.status_label.setText("JSON有效")
            self.status_label.setStyleSheet("color: #2E7D32;")
            
            QMessageBox.information(self, "验证成功", 
                                  f"JSON格式有效!\n\n"
                                  f"对象数: {stats['objects']}\n"
                                  f"数组数: {stats['arrays']}\n"
                                  f"字符串数: {stats['strings']}\n"
                                  f"数字数: {stats['numbers']}\n"
                                  f"布尔值数: {stats['booleans']}\n"
                                  f"null值数: {stats['nulls']}\n"
                                  f"层级深度: {stats['depth']}")
            
        except Exception as e:
            self.status_label.setText(f"验证失败: {str(e)}")
            self.status_label.setStyleSheet("color: #D32F2F;")
            QMessageBox.warning(self, "验证错误", f"JSON格式无效: {str(e)}")
    
    def get_json_stats(self, data, depth=0):
        """获取JSON结构的统计信息"""
        stats = {'objects': 0, 'arrays': 0, 'strings': 0, 
                'numbers': 0, 'booleans': 0, 'nulls': 0, 'depth': depth}
        
        if isinstance(data, dict):
            stats['objects'] += 1
            max_depth = depth
            
            for key, value in data.items():
                stats['strings'] += 1  # 键都是字符串
                child_stats = self.get_json_stats(value, depth + 1)
                
                for k in stats:
                    if k != 'depth':
                        stats[k] += child_stats[k]
                        
                max_depth = max(max_depth, child_stats['depth'])
            
            stats['depth'] = max_depth
            
        elif isinstance(data, list):
            stats['arrays'] += 1
            max_depth = depth
            
            for item in data:
                child_stats = self.get_json_stats(item, depth + 1)
                
                for k in stats:
                    if k != 'depth':
                        stats[k] += child_stats[k]
                        
                max_depth = max(max_depth, child_stats['depth'])
            
            stats['depth'] = max_depth
            
        elif isinstance(data, str):
            stats['strings'] += 1
        elif isinstance(data, (int, float)):
            stats['numbers'] += 1
        elif isinstance(data, bool):
            stats['booleans'] += 1
        elif data is None:
            stats['nulls'] += 1
            
        return stats
    
    def copy_to_clipboard(self):
        """复制内容到剪贴板"""
        text = self.text_edit.toPlainText()
        if not text:
            self.status_label.setText("没有内容可复制")
            self.status_label.setStyleSheet("color: #FF9800;")
            return
            
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)
        
        self.status_label.setText("已复制到剪贴板")
        self.status_label.setStyleSheet("color: #2E7D32;") 