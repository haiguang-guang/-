from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QGridLayout, 
                            QPushButton, QLineEdit, QHBoxLayout,
                            QLabel, QFrame, QSplitter, QWidget, QScrollArea, QTextEdit, QMessageBox)
from PyQt6.QtGui import QIcon, QFont, QGuiApplication, QPalette, QColor, QLinearGradient, QBrush, QKeyEvent
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QPoint, QTimer
import os
import re
import math

class CalculatorButton(QPushButton):
    def __init__(self, text, color_scheme, tooltip="", parent=None):
        super().__init__(text, parent)
        self.color_scheme = color_scheme
        self.setMinimumSize(50, 50)
        self.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        self.setStyleSheet(self.get_style())
        if tooltip:
            self.setToolTip(tooltip)
        
    def get_style(self):
        base_color, hover_color, text_color = self.color_scheme
        return f"""
            QPushButton {{
                background-color: {base_color};
                color: {text_color};
                border-radius: 8px;
                font-weight: bold;
                border: 2px solid {hover_color};
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                border: 2px solid {text_color};
            }}
            QPushButton:pressed {{
                background-color: {base_color};
                margin-top: 2px;
                margin-bottom: -2px;
            }}
        """

class Calculator(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("科学计算器")
        self.setModal(True)
        self.setMinimumSize(470, 620)  # 调整整体尺寸
        self.current_expression = ""
        self.memory = 0
        self.has_result = False
        self.deg_mode = True  # 角度模式 (True为角度，False为弧度)
        self.setup_ui()
        
        # 启用键盘跟踪
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 设置窗口背景渐变色
        self.set_gradient_background("#ECEFF1", "#B0BEC5")
        
        # 标题区域
        title_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/calculator.png")
        if os.path.exists(icon_path):
            icon_label.setPixmap(QIcon(icon_path).pixmap(QSize(32, 32)))
        
        title_label = QLabel("科学计算器")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1A237E; text-shadow: 1px 1px 1px rgba(0,0,0,0.1);")
        
        # 角度/弧度模式切换
        self.mode_button = QPushButton("DEG")
        self.mode_button.setFixedSize(60, 30)
        self.mode_button.setStyleSheet("""
            QPushButton {
                background-color: #7986CB;
                color: white;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #5C6BC0;
            }
        """)
        self.mode_button.clicked.connect(self.toggle_angle_mode)
        
        # 添加帮助按钮
        self.help_button = QPushButton("?")
        self.help_button.setFixedSize(30, 30)
        self.help_button.setStyleSheet("""
            QPushButton {
                background-color: #5C6BC0;
                color: white;
                border-radius: 15px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #3F51B5;
            }
        """)
        self.help_button.clicked.connect(self.show_help)
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.mode_button)
        title_layout.addWidget(self.help_button)
        
        main_layout.addLayout(title_layout)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #B0BEC5; height: 1px;")
        main_layout.addWidget(separator)
        
        # 显示区域容器
        display_container = QWidget()
        display_container.setStyleSheet("""
            background-color: #E8EAF6;
            border-radius: 10px;
            border: 1px solid #C5CAE9;
            padding: 8px;
        """)
        display_layout = QVBoxLayout(display_container)
        display_layout.setContentsMargins(12, 12, 12, 12)
        display_layout.setSpacing(5)
        
        # 历史显示
        self.history_display = QLineEdit()
        self.history_display.setReadOnly(True)
        self.history_display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.history_display.setFont(QFont("Consolas", 12))
        self.history_display.setStyleSheet("""
            QLineEdit {
                border: none;
                color: #5C6BC0;
                background-color: transparent;
                padding: 5px;
            }
        """)
        display_layout.addWidget(self.history_display)
        
        # 主显示区域
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setFont(QFont("Consolas", 26, QFont.Weight.Bold))
        self.display.setStyleSheet("""
            QLineEdit {
                border: none;
                background-color: transparent;
                color: #1A237E;
                padding: 10px 5px;
            }
        """)
        display_layout.addWidget(self.display)
        
        main_layout.addWidget(display_container)
        
        # 按钮区域容器
        buttons_container = QWidget()
        buttons_container.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 10px;
            border: 1px solid #CFD8DC;
        """)
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(12, 12, 12, 12)
        buttons_layout.setSpacing(10)
        
        # 布局网格
        button_grid = QGridLayout()
        button_grid.setSpacing(6)
        
        # 第一行：内存和特殊功能按钮
        memory_buttons = [
            ("MC", 0, 0, ("#E8EAF6", "#C5CAE9", "#3949AB"), "清除内存"),
            ("MR", 0, 1, ("#E8EAF6", "#C5CAE9", "#3949AB"), "读取内存"),
            ("M+", 0, 2, ("#E8EAF6", "#C5CAE9", "#3949AB"), "将当前值加到内存"),
            ("M-", 0, 3, ("#E8EAF6", "#C5CAE9", "#3949AB"), "从内存减去当前值"),
            ("MS", 0, 4, ("#E8EAF6", "#C5CAE9", "#3949AB"), "保存到内存"),
            ("CE", 0, 5, ("#FFCDD2", "#EF9A9A", "#D32F2F"), "清除当前输入"),
            ("C", 0, 6, ("#FFCDD2", "#EF9A9A", "#D32F2F"), "清除所有内容"),
            ("⌫", 0, 7, ("#FFCDD2", "#EF9A9A", "#D32F2F"), "删除"),
        ]
        
        for text, row, col, color_scheme, tooltip in memory_buttons:
            button = CalculatorButton(text, color_scheme, tooltip)
            button.setFixedSize(50, 40)
            button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            button.clicked.connect(self.button_clicked)
            button_grid.addWidget(button, row, col)
        
        # 第二行：高级科学功能
        scientific_row1 = [
            ("2ⁿᵈ", 1, 0, ("#D1C4E9", "#B39DDB", "#4527A0"), "第二功能"),
            ("π", 1, 1, ("#D1C4E9", "#B39DDB", "#4527A0"), "圆周率"),
            ("e", 1, 2, ("#D1C4E9", "#B39DDB", "#4527A0"), "自然常数"),
            ("ln", 1, 3, ("#D1C4E9", "#B39DDB", "#4527A0"), "自然对数"),
            ("log", 1, 4, ("#D1C4E9", "#B39DDB", "#4527A0"), "常用对数"),
            ("!", 1, 5, ("#D1C4E9", "#B39DDB", "#4527A0"), "阶乘"),
            ("√", 1, 6, ("#D1C4E9", "#B39DDB", "#4527A0"), "平方根"),
            ("^", 1, 7, ("#D1C4E9", "#B39DDB", "#4527A0"), "幂运算"),
        ]
        
        for text, row, col, color_scheme, tooltip in scientific_row1:
            button = CalculatorButton(text, color_scheme, tooltip)
            button.setFixedSize(50, 40)
            button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            button.clicked.connect(self.button_clicked)
            button_grid.addWidget(button, row, col)
            
        # 第三行：三角函数
        scientific_row2 = [
            ("sin", 2, 0, ("#D1C4E9", "#B39DDB", "#4527A0"), "正弦函数"),
            ("cos", 2, 1, ("#D1C4E9", "#B39DDB", "#4527A0"), "余弦函数"),
            ("tan", 2, 2, ("#D1C4E9", "#B39DDB", "#4527A0"), "正切函数"),
            ("asin", 2, 3, ("#D1C4E9", "#B39DDB", "#4527A0"), "反正弦函数"),
            ("acos", 2, 4, ("#D1C4E9", "#B39DDB", "#4527A0"), "反余弦函数"),
            ("atan", 2, 5, ("#D1C4E9", "#B39DDB", "#4527A0"), "反正切函数"),
            ("(", 2, 6, ("#BBDEFB", "#90CAF9", "#1976D2"), "左括号"),
            (")", 2, 7, ("#BBDEFB", "#90CAF9", "#1976D2"), "右括号"),
        ]
        
        for text, row, col, color_scheme, tooltip in scientific_row2:
            button = CalculatorButton(text, color_scheme, tooltip)
            button.setFixedSize(50, 40)
            button.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            button.clicked.connect(self.button_clicked)
            button_grid.addWidget(button, row, col)
        
        # 第四行开始：数字和基本运算
        basic_buttons = [
            ("x²", 3, 0, ("#D1C4E9", "#B39DDB", "#4527A0"), "平方"),
            ("x³", 3, 1, ("#D1C4E9", "#B39DDB", "#4527A0"), "立方"),
            ("1/x", 3, 2, ("#D1C4E9", "#B39DDB", "#4527A0"), "倒数"),
            ("7", 3, 3, ("#ECEFF1", "#CFD8DC", "#37474F"), "数字 7"),
            ("8", 3, 4, ("#ECEFF1", "#CFD8DC", "#37474F"), "数字 8"),
            ("9", 3, 5, ("#ECEFF1", "#CFD8DC", "#37474F"), "数字 9"),
            ("÷", 3, 6, ("#FFE0B2", "#FFCC80", "#E65100"), "除法"),
            ("%", 3, 7, ("#FFE0B2", "#FFCC80", "#E65100"), "百分比"),
            
            ("10ˣ", 4, 0, ("#D1C4E9", "#B39DDB", "#4527A0"), "10的幂"),
            ("exp", 4, 1, ("#D1C4E9", "#B39DDB", "#4527A0"), "e的幂"),
            ("mod", 4, 2, ("#D1C4E9", "#B39DDB", "#4527A0"), "取模运算"),
            ("4", 4, 3, ("#ECEFF1", "#CFD8DC", "#37474F"), "数字 4"),
            ("5", 4, 4, ("#ECEFF1", "#CFD8DC", "#37474F"), "数字 5"),
            ("6", 4, 5, ("#ECEFF1", "#CFD8DC", "#37474F"), "数字 6"),
            ("×", 4, 6, ("#FFE0B2", "#FFCC80", "#E65100"), "乘法"),
            ("±", 4, 7, ("#BBDEFB", "#90CAF9", "#1976D2"), "正负号切换"),
            
            ("sinh", 5, 0, ("#D1C4E9", "#B39DDB", "#4527A0"), "双曲正弦"),
            ("cosh", 5, 1, ("#D1C4E9", "#B39DDB", "#4527A0"), "双曲余弦"),
            ("tanh", 5, 2, ("#D1C4E9", "#B39DDB", "#4527A0"), "双曲正切"),
            ("1", 5, 3, ("#ECEFF1", "#CFD8DC", "#37474F"), "数字 1"),
            ("2", 5, 4, ("#ECEFF1", "#CFD8DC", "#37474F"), "数字 2"),
            ("3", 5, 5, ("#ECEFF1", "#CFD8DC", "#37474F"), "数字 3"),
            ("-", 5, 6, ("#FFE0B2", "#FFCC80", "#E65100"), "减法"),
            ("=", 5, 7, ("#3F51B5", "#5C6BC0", "white"), "计算结果"),
            
            ("rad", 6, 0, ("#D1C4E9", "#B39DDB", "#4527A0"), "切换到弧度模式"),
            ("deg", 6, 1, ("#D1C4E9", "#B39DDB", "#4527A0"), "切换到角度模式"),
            ("rand", 6, 2, ("#D1C4E9", "#B39DDB", "#4527A0"), "随机数生成"),
            ("0", 6, 3, ("#ECEFF1", "#CFD8DC", "#37474F"), "数字 0"),
            ("0", 6, 4, ("#ECEFF1", "#CFD8DC", "#37474F"), "数字 0"),
            (".", 6, 5, ("#ECEFF1", "#CFD8DC", "#37474F"), "小数点"),
            ("+", 6, 6, ("#FFE0B2", "#FFCC80", "#E65100"), "加法"),
            ("=", 6, 7, ("#3F51B5", "#5C6BC0", "white"), "计算结果"),
        ]
        
        # 合并0按钮
        # 创建按钮并添加到布局
        self.buttons = {}
        
        # 添加所有基本按钮
        for text, row, col, color_scheme, tooltip in basic_buttons:
            # 跳过第二个等号按钮
            if row == 6 and col == 7:
                continue
                
            # 合并0按钮
            if text == "0" and col == 4:
                continue
                
            button = CalculatorButton(text, color_scheme, tooltip)
            
            # 设置0按钮宽度为两倍
            if text == "0" and col == 3:
                button.setFixedSize(106, 40)  # 两列宽度加上间距
                button_grid.addWidget(button, row, col, 1, 2)  # 跨越两列
            else:
                button.setFixedSize(50, 40)
                button_grid.addWidget(button, row, col)
                
            # 等号按钮跨两行
            if text == "=" and row == 5 and col == 7:
                button.setFixedSize(50, 86)  # 两行高度加上间距
                button_grid.addWidget(button, row, col, 2, 1)  # 跨越两行
                
            button.clicked.connect(self.button_clicked)
            self.buttons[text] = button
            
        buttons_layout.addLayout(button_grid)
        main_layout.addWidget(buttons_container)
        
    def toggle_angle_mode(self):
        """切换角度/弧度模式"""
        self.deg_mode = not self.deg_mode
        if self.deg_mode:
            self.mode_button.setText("DEG")
        else:
            self.mode_button.setText("RAD")
        
    def set_gradient_background(self, start_color, end_color):
        """设置窗口渐变背景"""
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(start_color))
        gradient.setColorAt(1, QColor(end_color))
        
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        
    def button_clicked(self):
        button = self.sender()
        text = button.text()
        
        # 如果有计算结果且输入新数字，则清除当前表达式
        if self.has_result and text in "0123456789":
            self.current_expression = ""
            self.has_result = False
        
        if text == "=":
            self.calculate()
        elif text == "C":
            self.clear()
        elif text == "CE":
            self.clear_entry()
        elif text == "⌫":
            self.delete_last()
        elif text == "±":
            self.negate()
        elif text == "√":
            self.append_to_expression("sqrt(")
        elif text == "π":
            self.append_to_expression("pi")
        elif text == "e":
            self.append_to_expression("e")
        elif text == "x²":
            self.append_to_expression("^2")
        elif text == "x³":
            self.append_to_expression("^3")
        elif text == "10ˣ":
            self.append_to_expression("10^")
        elif text == "sin":
            self.append_function("sin")
        elif text == "cos":
            self.append_function("cos")
        elif text == "tan":
            self.append_function("tan")
        elif text == "asin":
            self.append_function("asin")
        elif text == "acos":
            self.append_function("acos")
        elif text == "atan":
            self.append_function("atan")
        elif text == "sinh":
            self.append_to_expression("sinh(")
        elif text == "cosh":
            self.append_to_expression("cosh(")
        elif text == "tanh":
            self.append_to_expression("tanh(")
        elif text == "log":
            self.append_to_expression("log10(")
        elif text == "ln":
            self.append_to_expression("log(")
        elif text == "!":
            self.append_to_expression("factorial(")
        elif text == "1/x":
            self.append_to_expression("1/(")
        elif text == "×":
            self.append_to_expression("*")
        elif text == "÷":
            self.append_to_expression("/")
        elif text == "mod":
            self.append_to_expression("%")
        elif text == "exp":
            self.append_to_expression("exp(")
        elif text == "rand":
            self.append_to_expression("random()")
        elif text == "rad":
            self.deg_mode = False
            self.mode_button.setText("RAD")
        elif text == "deg":
            self.deg_mode = True
            self.mode_button.setText("DEG")
        elif text == "MC":
            self.memory = 0
        elif text == "MS":
            try:
                if self.current_expression:
                    self.memory = float(eval(self.current_expression))
            except:
                pass
        elif text == "M+":
            try:
                if self.current_expression:
                    self.memory += float(eval(self.current_expression))
            except:
                pass
        elif text == "M-":
            try:
                if self.current_expression:
                    self.memory -= float(eval(self.current_expression))
            except:
                pass
        elif text == "MR":
            self.current_expression = str(self.memory)
            self.display.setText(self.current_expression)
        elif text == "2ⁿᵈ":
            # 切换第二功能模式 (未实现完整功能)
            self.toggle_second_function()
        elif text == "%":
            self.calculate_percentage()
        else:
            self.append_to_expression(text)
    
    def append_function(self, func_name):
        """根据当前角度/弧度模式添加三角函数"""
        if self.deg_mode and func_name in ["sin", "cos", "tan"]:
            # 如果是角度模式，需要将角度转换为弧度
            self.append_to_expression(f"{func_name}(radians(")
        else:
            self.append_to_expression(f"{func_name}(")
    
    def toggle_second_function(self):
        """切换第二功能模式"""
        # 这里可以实现切换2nd功能的逻辑
        pass
        
    def calculate_percentage(self):
        """计算百分比"""
        try:
            if self.current_expression:
                # 找到最后一个操作符
                last_op_index = max(
                    self.current_expression.rfind('+'),
                    self.current_expression.rfind('-'),
                    self.current_expression.rfind('*'),
                    self.current_expression.rfind('/')
                )
                
                if last_op_index > 0:
                    # 获取操作数和操作符
                    operator = self.current_expression[last_op_index]
                    left_operand = float(eval(self.current_expression[:last_op_index]))
                    right_operand = float(eval(self.current_expression[last_op_index+1:]))
                    
                    # 计算百分比
                    if operator in ['+', '-']:
                        result = left_operand * (1 + (right_operand/100 * (1 if operator == '+' else -1)))
                    else:  # * or /
                        result = eval(f"{left_operand}{operator}{right_operand/100}")
                        
                    self.current_expression = str(result)
                    self.display.setText(self.current_expression)
                else:
                    # 如果没有操作符，将数字转为百分比
                    result = float(eval(self.current_expression)) / 100
                    self.current_expression = str(result)
                    self.display.setText(self.current_expression)
        except:
            pass
        
    def append_to_expression(self, text):
        self.current_expression += text
        self.display.setText(self.current_expression)
        
    def clear(self):
        self.current_expression = ""
        self.display.clear()
        self.history_display.clear()
        self.has_result = False
    
    def clear_entry(self):
        # 只清除当前输入，保留历史记录
        self.current_expression = ""
        self.display.clear()
        self.has_result = False
        
    def delete_last(self):
        self.current_expression = self.current_expression[:-1]
        self.display.setText(self.current_expression)
        
    def negate(self):
        # 如果表达式为空或者只是一个负号，直接添加负号
        if not self.current_expression or self.current_expression == "-":
            self.current_expression = "-"
        else:
            # 检查表达式最后一个数字
            match = re.search(r'([-+*/^(]?)(\d+\.?\d*)$', self.current_expression)
            if match:
                prefix, number = match.groups()
                if prefix == "-":
                    # 如果已经是负数，移除负号
                    self.current_expression = self.current_expression[:-len(number)-1] + number
                else:
                    # 如果不是负数，添加负号
                    self.current_expression = self.current_expression[:-len(number)] + "-" + number
            else:
                # 如果没有找到数字，检查是否有括号等情况
                self.current_expression += "(-"
        
        self.display.setText(self.current_expression)
        
    def calculate(self):
        try:
            # 保存当前表达式到历史记录
            original_expression = self.current_expression
            self.history_display.setText(original_expression)
            
            # 替换数学函数和运算符为Python函数
            expression = self.current_expression
            expression = expression.replace("^", "**")
            expression = expression.replace("×", "*")  # 确保乘号正确替换
            expression = expression.replace("÷", "/")  # 确保除号正确替换
            expression = expression.replace("pi", "math.pi")
            expression = expression.replace("e", "math.e")
            expression = expression.replace("sqrt", "math.sqrt")
            expression = expression.replace("sin", "math.sin")
            expression = expression.replace("cos", "math.cos")
            expression = expression.replace("tan", "math.tan")
            expression = expression.replace("asin", "math.asin")
            expression = expression.replace("acos", "math.acos")
            expression = expression.replace("atan", "math.atan")
            expression = expression.replace("sinh", "math.sinh")
            expression = expression.replace("cosh", "math.cosh")
            expression = expression.replace("tanh", "math.tanh")
            expression = expression.replace("log10", "math.log10")
            expression = expression.replace("log", "math.log")
            expression = expression.replace("exp", "math.exp")
            expression = expression.replace("factorial", "math.factorial")
            expression = expression.replace("radians", "math.radians")
            expression = expression.replace("random()", "random.random()")
            
            # 检查表达式是否为空
            if not expression.strip():
                self.display.setText("0")
                self.current_expression = "0"
                return
                
            # 检查括号是否匹配
            if expression.count('(') != expression.count(')'):
                raise ValueError("括号不匹配")
                
            # 导入random模块
            import random
            
            # 计算表达式
            try:
                result = eval(expression)
            except SyntaxError:
                # 尝试修复常见的语法错误
                if expression.endswith(('*', '/', '+', '-', '**')):
                    # 结尾有未完成的运算符
                    expression = expression[:-1]
                    result = eval(expression)
                else:
                    raise
            
            # 显示结果
            if isinstance(result, complex):
                self.current_expression = str(result).replace('j', 'i')
            elif result == int(result):
                result = int(result)
                self.current_expression = str(result)
            else:
                # 限制小数位数，避免过长的小数
                result = round(result, 10)
                # 移除尾部不必要的零
                self.current_expression = str(result).rstrip('0').rstrip('.') if '.' in str(result) else str(result)
            
            self.display.setText(self.current_expression)
            self.has_result = True
            
        except Exception as e:
            error_msg = str(e)
            self.display.setText("错误")
            self.history_display.setText(f"错误: {error_msg} (在表达式: {original_expression})")
            self.current_expression = ""
    
    def show_help(self):
        """显示帮助信息"""
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("计算器使用帮助")
        help_dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(help_dialog)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        
        # 创建内容容器
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # 标题
        title_label = QLabel("科学计算器使用指南")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #3F51B5;
            margin-bottom: 10px;
        """)
        content_layout.addWidget(title_label)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #E0E0E0;")
        content_layout.addWidget(separator)
        
        # 帮助内容
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setStyleSheet("""
            border: none;
            background-color: white;
            font-size: 14px;
        """)
        
        help_content = """
        <h3>基本按键</h3>
        <p><b>数字键 (0-9)</b>：输入数字</p>
        <p><b>小数点 (.)</b>：输入小数点</p>
        <p><b>基本运算符 (+, -, ×, ÷)</b>：执行加、减、乘、除运算</p>
        <p><b>等号 (=)</b>：计算结果</p>
        <p><b>C</b>：清除所有内容</p>
        <p><b>CE</b>：只清除当前输入</p>
        <p><b>⌫</b>：删除最后一个字符</p>
        <p><b>±</b>：正负号切换</p>
        
        <h3>科学函数</h3>
        <p><b>三角函数</b>：sin, cos, tan, asin, acos, atan</p>
        <p><b>双曲函数</b>：sinh, cosh, tanh</p>
        <p><b>对数函数</b>：log (常用对数), ln (自然对数)</p>
        <p><b>指数与幂</b>：x², x³, 10ˣ, ^（任意次幂）</p>
        <p><b>其他函数</b>：√ (平方根), exp (e的指数), ! (阶乘)</p>
        <p><b>常数</b>：π (圆周率), e (自然常数)</p>
        
        <h3>内存功能</h3>
        <p><b>MC</b>：清除内存</p>
        <p><b>MR</b>：调用内存中的值</p>
        <p><b>MS</b>：将当前值存入内存</p>
        <p><b>M+</b>：将当前值加到内存中</p>
        <p><b>M-</b>：从内存中减去当前值</p>
        
        <h3>角度与弧度</h3>
        <p><b>DEG/RAD按钮</b>：切换角度模式和弧度模式</p>
        <p><b>deg</b>：将计算模式设为角度模式</p>
        <p><b>rad</b>：将计算模式设为弧度模式</p>
        <p><i>注意：角度模式下，三角函数的参数是角度值；弧度模式下，参数是弧度值</i></p>
        
        <h3>特殊功能</h3>
        <p><b>%</b>：百分比计算</p>
        <p><b>1/x</b>：计算倒数</p>
        <p><b>rand</b>：生成0到1之间的随机数</p>
        <p><b>mod</b>：取模运算</p>
        
        <h3>使用示例</h3>
        <p><b>基本计算</b>：输入 2+3×4=，得到 14</p>
        <p><b>三角函数</b>：切换到角度模式(DEG)，输入 sin(30)=，得到 0.5</p>
        <p><b>幂运算</b>：输入 2^3=，得到 8</p>
        <p><b>对数计算</b>：输入 log(100)=，得到 2</p>
        """
        
        help_text.setHtml(help_content)
        content_layout.addWidget(help_text)
        
        # 设置滚动区域内容
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # 确定按钮
        ok_button = QPushButton("我知道了")
        ok_button.clicked.connect(help_dialog.accept)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        layout.addWidget(ok_button)
        
        help_dialog.exec()

    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘按键事件"""
        key = event.key()
        text = event.text()
        
        # 处理数字键 (0-9对应的ASCII码是48-57)
        if 48 <= key <= 57:
            self.process_key_input(text)
        # 处理运算符
        elif text in "+-*/^%()":
            # 替换乘除符号为显示符号
            if text == "*":
                self.process_key_input("×")
            elif text == "/":
                self.process_key_input("÷")
            else:
                self.process_key_input(text)
        # 处理小数点
        elif text == ".":
            self.process_key_input(".")
        # 处理回车和等号键
        elif key in [Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Equal]:
            self.calculate()
        # 处理Backspace键
        elif key == Qt.Key.Key_Backspace:
            self.delete_last()
        # 处理Escape键
        elif key == Qt.Key.Key_Escape:
            self.clear()
        # 处理Delete键
        elif key == Qt.Key.Key_Delete:
            self.clear_entry()
        else:
            # 对于三角函数等快捷键支持
            if text == "s":  # s for sin
                self.append_function("sin")
            elif text == "c":  # c for cos
                self.append_function("cos")
            elif text == "t":  # t for tan
                self.append_function("tan")
            elif text == "l":  # l for log
                self.append_to_expression("log10(")
            elif text == "n":  # n for ln
                self.append_to_expression("log(")
            elif text == "q":  # q for sqrt
                self.append_to_expression("sqrt(")
            elif text == "p":  # p for pi
                self.append_to_expression("pi")
            elif text == "e":  # e for e
                self.append_to_expression("e")
            else:
                # 调用父类的keyPressEvent处理其他按键
                super().keyPressEvent(event)

    def process_key_input(self, text):
        """处理键盘输入"""
        # 如果有计算结果且输入新数字，则清除当前表达式
        if self.has_result and text in "0123456789":
            self.current_expression = ""
            self.has_result = False
        
        self.append_to_expression(text)
        
        # 如果有对应的按钮，模拟点击效果
        if text in self.buttons:
            button = self.buttons[text]
            # 临时改变按钮样式以显示"按下"效果
            original_style = button.styleSheet()
            pressed_style = button.styleSheet() + "background-color: #B0BEC5; margin-top: 2px; margin-bottom: -2px;"
            button.setStyleSheet(pressed_style)
            
            # 使用QTimer在短暂延迟后恢复原样式
            QTimer.singleShot(100, lambda: button.setStyleSheet(original_style)) 