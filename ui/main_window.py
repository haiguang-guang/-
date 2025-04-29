from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QDialog, QMessageBox,
                            QStackedWidget, QFrame, QScrollArea, QTreeWidget, QTreeWidgetItem)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor, QPalette, QGradient, QLinearGradient, QBrush
import os
from .tools.hash_calculator import HashCalculator
from .tools.timestamp_converter import TimestampConverter
from .tools.base64_converter import Base64Converter
from .tools.json_formatter import JsonFormatter
from .tools.clipboard_tool import ClipboardTool
from .tools.qr_code_generator import QRCodeGenerator
from .tools.color_picker import ColorPicker
from .tools.file_renamer import FileRenamer
from .tools.text_encryptor import TextEncryptor
from .tools.image_compressor import ImageCompressor
from .tools.url_shortener import URLShortener
from .tools.calculator import Calculator
from .tools.weather_checker import WeatherChecker
from .tools.text_diff import TextDiff

# 为每个工具类创建一个实例缓存，避免重复创建
tool_instances = {}

class ToolsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("实用工具合集")
        self.setMinimumSize(1100, 800)
        
        # 设置应用图标
        icon_path = os.path.join(os.path.dirname(__file__), "icons/favicon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            QScrollArea, QScrollBar {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QPushButton {
                background-color: #2E7D32;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                min-width: 120px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #388E3C;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
            }
            QPushButton:pressed {
                background-color: #1B5E20;
            }
            QPushButton:checked {
                background-color: #1B5E20;
                border: 2px solid #004D40;
            }
            QTextEdit, QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 6px;
                background-color: white;
                color: #333;
                font-size: 14px;
                selection-background-color: #2E7D32;
                selection-color: white;
            }
            QTextEdit:focus, QLineEdit:focus {
                border: 1px solid #2E7D32;
            }
            QLabel {
                font-size: 14px;
                color: #424242;
                font-weight: 400;
            }
            #sidebarFrame {
                background-color: #2E3440;
                border-radius: 0px;
                padding: 10px;
            }
            #contentFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
                border: 1px solid #e0e0e0;
            }
            #titleLabel {
                color: white;
                font-size: 22px;
                font-weight: bold;
                margin-bottom: 10px;
                font-family: 'Arial', sans-serif;
            }
            #welcomeTitleLabel {
                color: #2E7D32;
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 20px;
                font-family: 'Arial', sans-serif;
            }
            QTreeWidget {
                background-color: transparent;
                border: none;
                color: #eceff4;
                font-size: 14px;
                outline: none;
                padding-top: 5px;
                padding-bottom: 5px;
            }
            QTreeWidget::item {
                height: 32px;
                padding: 6px;
                border-radius: 6px;
                margin: 1px 0;
            }
            QTreeWidget::item:has-children {
                font-weight: bold;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                margin-top: 6px;
                background-color: rgba(143, 188, 187, 0.1);
            }
            QTreeWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QTreeWidget::item:selected {
                background-color: #8FBCBB;
                color: #2E3440;
                font-weight: bold;
            }
            QTreeWidget::branch {
                background: transparent;
            }
            QTreeWidget::branch:has-siblings:!adjoins-item {
                border-image: none;
            }
            QTreeWidget::branch:has-siblings:adjoins-item {
                border-image: none;
            }
            QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {
                border-image: none;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(branch-closed.png);
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings  {
                border-image: none;
                image: url(branch-open.png);
            }
            .CategoryHeader {
                color: #8FBCBB;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
                margin-bottom: 5px;
            }
            .InfoLabel {
                color: #4C566A;
                font-size: 14px;
                margin: 5px 0;
                line-height: 1.5;
            }
            .CategoryIcon {
                margin-right: 10px;
            }
            #browserButton {
                background-color: #5E81AC;
                color: white;
                border-radius: 6px;
                padding: 10px 15px;
                margin-top: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            #browserButton:hover {
                background-color: #81A1C1;
            }
        """)
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 主布局为水平布局
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建左侧边栏框架
        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("sidebarFrame")
        sidebar_frame.setMinimumWidth(260)
        sidebar_frame.setMaximumWidth(260)
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(15, 25, 15, 25)
        sidebar_layout.setSpacing(15)
        
        # 添加标题到侧边栏
        title_layout = QHBoxLayout()
        
        # 如果存在图标则添加
        app_icon_label = QLabel()
        app_icon_path = os.path.join(os.path.dirname(__file__), "icons/favicon.ico")
        if os.path.exists(app_icon_path):
            app_icon = QIcon(app_icon_path).pixmap(32, 32)
            app_icon_label.setPixmap(app_icon)
            title_layout.addWidget(app_icon_label)
        
        # 添加标题文本
        title = QLabel("实用工具合集")
        title.setObjectName("titleLabel")
        title_layout.addWidget(title, 1)
        sidebar_layout.addLayout(title_layout)
        
        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #4C566A; margin: 5px 0;")
        sidebar_layout.addWidget(line)
        
        # 定义分类图标 (如果图标文件存在则加载)
        self.category_icons = {
            "文件工具": os.path.join(os.path.dirname(__file__), "icons/file_tools.png"),
            "编码工具": os.path.join(os.path.dirname(__file__), "icons/coding_tools.png"),
            "格式化工具": os.path.join(os.path.dirname(__file__), "icons/format_tools.png"),
            "实用工具": os.path.join(os.path.dirname(__file__), "icons/utility_tools.png")
        }
        
        # 定义工具分类
        self.tool_categories = {
            "文件工具": [
                {"name": "文件哈希计算", "class": HashCalculator, "icon": "hash.png"},
                {"name": "文件重命名", "class": FileRenamer, "icon": "rename.png"},
                {"name": "图片压缩", "class": ImageCompressor, "icon": "compress.png"},
            ],
            "编码工具": [
                {"name": "Base64编解码", "class": Base64Converter, "icon": "base64.png"},
                {"name": "文本加密", "class": TextEncryptor, "icon": "encrypt.png"},
                {"name": "二维码生成", "class": QRCodeGenerator, "icon": "qrcode.png"},
                {"name": "URL缩短器", "class": URLShortener, "icon": "link.png"},
            ],
            "格式化工具": [
                {"name": "JSON格式化", "class": JsonFormatter, "icon": "json.png"},
                {"name": "时间戳转换", "class": TimestampConverter, "icon": "timestamp.png"},
                {"name": "文本差异比较", "class": TextDiff, "icon": "diff.png"},
            ],
            "实用工具": [
                {"name": "颜色选择器", "class": ColorPicker, "icon": "color.png"},
                {"name": "剪贴板工具", "class": ClipboardTool, "icon": "clipboard.png"},
                {"name": "科学计算器", "class": Calculator, "icon": "calculator.png"},
                {"name": "天气查询", "class": WeatherChecker, "icon": "weather.png"},
            ]
        }
        
        # 创建工具分类树
        self.tool_tree = QTreeWidget()
        self.tool_tree.setHeaderHidden(True)
        self.tool_tree.setIndentation(15)
        self.tool_tree.setAnimated(True)
        self.tool_tree.setExpandsOnDoubleClick(True)
        self.tool_tree.setIconSize(QSize(20, 20))
        
        # 设置固定的更高高度以显示所有项目
        self.tool_tree.setMinimumHeight(500)
        
        # 禁用滚动条
        self.tool_tree.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 添加工具到分类树
        self.tool_items = []
        self.category_items = {}
        tool_index = 0
        
        for category_name, tools in self.tool_categories.items():
            # 创建分类项
            category_item = QTreeWidgetItem(self.tool_tree)
            category_item.setText(0, category_name)
            category_item.setFlags(category_item.flags() | Qt.ItemFlag.ItemIsAutoTristate)
            self.category_items[category_name] = category_item
            
            # 设置分类字体和图标
            font = category_item.font(0)
            font.setBold(True)
            font.setPointSize(11)
            category_item.setFont(0, font)
            
            # 如果有分类图标则设置
            if os.path.exists(self.category_icons.get(category_name, "")):
                category_item.setIcon(0, QIcon(self.category_icons[category_name]))
            
            # 添加工具项
            for tool in tools:
                tool_item = self.add_tree_item(category_name, tool, category_item, tool_index)
                self.tool_items.append(tool_item)
                tool_index += 1
            
            # 默认不展开分类
            # self.tool_tree.expandItem(category_item)
        
        # 连接工具树的点击事件
        self.tool_tree.itemClicked.connect(self.handle_tool_selection)
        
        # 添加工具树到侧边栏
        sidebar_layout.addWidget(self.tool_tree)
        
        # 底部添加"打开浏览器"按钮
        sidebar_layout.addStretch()
        browser_btn = QPushButton("打开浏览器")
        browser_btn.setObjectName("browserButton")
        browser_btn.clicked.connect(self.open_browser)
        sidebar_layout.addWidget(browser_btn)
        
        # 创建右侧内容区域
        content_area = QScrollArea()
        content_area.setWidgetResizable(True)
        content_area.setFrameShape(QFrame.Shape.NoFrame)
        
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(25, 25, 25, 25)
        
        # 创建堆叠部件用于切换不同工具
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)
        
        # 创建欢迎页面
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setContentsMargins(40, 40, 40, 40)
        welcome_layout.setSpacing(20)
        
        # 欢迎标题
        welcome_title = QLabel("欢迎使用实用工具合集")
        welcome_title.setObjectName("welcomeTitleLabel")
        welcome_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.addWidget(welcome_title)
        
        # 欢迎信息
        welcome_message = QLabel("从左侧菜单选择工具开始使用")
        welcome_message.setFont(QFont("Arial", 16))
        welcome_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_message.setStyleSheet("color: #616161; margin-bottom: 20px;")
        welcome_layout.addWidget(welcome_message)
        
        # 分割线
        welcome_line = QFrame()
        welcome_line.setFrameShape(QFrame.Shape.HLine)
        welcome_line.setFrameShadow(QFrame.Shadow.Sunken)
        welcome_line.setStyleSheet("background-color: #e0e0e0; margin: 10px 0;")
        welcome_layout.addWidget(welcome_line)
        
        # 添加分类简介
        categories_info = QLabel("""
<h3 style="color: #2E7D32; margin-bottom: 15px;">工具分类说明：</h3>
<div style="margin-left: 10px;">
    <p style="margin-bottom: 15px;"><b style="color: #2E7D32;">文件工具</b> - 处理文件相关操作</p>
    <ul style="margin-left: 20px; margin-bottom: 15px;">
        <li style="margin-bottom: 5px;">文件哈希计算 - 计算文件的MD5、SHA1和SHA256哈希值</li>
        <li style="margin-bottom: 5px;">文件重命名 - 批量重命名文件，支持模式替换</li>
        <li style="margin-bottom: 5px;">图片压缩 - 无损压缩图片减小体积</li>
    </ul>
    
    <p style="margin-bottom: 15px;"><b style="color: #2E7D32;">编码工具</b> - 文本编码与转换</p>
    <ul style="margin-left: 20px; margin-bottom: 15px;">
        <li style="margin-bottom: 5px;">Base64编解码 - 文本与Base64格式互相转换</li>
        <li style="margin-bottom: 5px;">文本加密 - 使用对称加密算法加密文本</li>
        <li style="margin-bottom: 5px;">二维码生成 - 将文本或URL转换为二维码</li>
        <li style="margin-bottom: 5px;">URL缩短器 - 将长URL转换成短链接</li>
    </ul>
    
    <p style="margin-bottom: 15px;"><b style="color: #2E7D32;">格式化工具</b> - 数据格式转换</p>
    <ul style="margin-left: 20px; margin-bottom: 15px;">
        <li style="margin-bottom: 5px;">JSON格式化 - 美化或压缩JSON数据</li>
        <li style="margin-bottom: 5px;">时间戳转换 - 时间戳与日期时间格式转换</li>
        <li style="margin-bottom: 5px;">文本差异比较 - 比较两段文本的差异</li>
    </ul>
    
    <p style="margin-bottom: 15px;"><b style="color: #2E7D32;">实用工具</b> - 日常实用功能</p>
    <ul style="margin-left: 20px; margin-bottom: 15px;">
        <li style="margin-bottom: 5px;">颜色选择器 - 选择颜色并获取RGB/HEX值</li>
        <li style="margin-bottom: 5px;">剪贴板工具 - 增强的剪贴板功能</li>
        <li style="margin-bottom: 5px;">科学计算器 - 执行复杂的数学计算</li>
        <li style="margin-bottom: 5px;">天气查询 - 查询实时天气信息</li>
    </ul>
</div>
<p style="color: #616161; font-style: italic; margin-top: 20px;">点击左侧的分类名称即可展开各类工具</p>
        """)
        categories_info.setTextFormat(Qt.TextFormat.RichText)
        welcome_layout.addWidget(categories_info)
        
        welcome_layout.addStretch()
        
        # 添加欢迎页面到堆叠部件
        self.stacked_widget.addWidget(welcome_widget)
        
        # 创建所有工具实例的列表
        self.tools_list = []
        for category in self.tool_categories.values():
            self.tools_list.extend(category)
            
        # 初始化工具页面
        self.init_tool_pages()
        
        # 设置内容区域
        content_area.setWidget(content_frame)
        
        # 将侧边栏和内容区域添加到主布局
        main_layout.addWidget(sidebar_frame)
        main_layout.addWidget(content_area, 1)
    
    def init_tool_pages(self):
        """初始化所有工具页面"""
        for tool in self.tools_list:
            # 创建工具实例并添加到堆叠部件
            tool_instance = tool["class"](self)
            
            # 存储工具实例
            tool_instances[tool["class"].__name__] = tool_instance
            
            # 将工具实例添加到堆叠部件
            self.stacked_widget.addWidget(tool_instance)
    
    def handle_tool_selection(self, item, column):
        """处理工具树项目的选择"""
        # 获取项目数据
        tool_index = item.data(0, Qt.ItemDataRole.UserRole)
        
        # 如果点击的是分类，就展开/折叠它
        if tool_index is None:
            if item.isExpanded():
                self.tool_tree.collapseItem(item)
            else:
                self.tool_tree.expandItem(item)
            return
        
        # 显示对应的工具页面
        try:
            self.stacked_widget.setCurrentIndex(tool_index + 1)  # +1 是因为0是欢迎页面
        except Exception as e:
            QMessageBox.critical(self, "错误", f"显示工具时出错: {str(e)}")
            print(f"Error showing tool: {e}, tool_index: {tool_index}, type: {type(tool_index)}")
    
    def open_browser(self):
        """打开浏览器"""
        try:
            import webbrowser
            webbrowser.open("https://www.google.com")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开浏览器时出错: {str(e)}")
    
    def add_tree_item(self, category_name, tool_cls, category_item=None, tool_index=None):
        """添加工具到树形控件"""
        # 如果没有提供分类项，则创建新的分类
        if category_item is None:
            category_item = self.category_items.get(category_name)
            if category_item is None:
                category_item = QTreeWidgetItem(self.tool_tree)
                category_item.setText(0, category_name)
                # 设置分类图标
                if category_name == "文本处理":
                    category_item.setIcon(0, QIcon(":/icons/text.png"))
                elif category_name == "图像处理":
                    category_item.setIcon(0, QIcon(":/icons/image.png"))
                elif category_name == "系统工具":
                    category_item.setIcon(0, QIcon(":/icons/system.png"))
                elif category_name == "网络工具":
                    category_item.setIcon(0, QIcon(":/icons/network.png"))
                elif category_name == "开发工具":
                    category_item.setIcon(0, QIcon(":/icons/dev.png"))
                else:
                    category_item.setIcon(0, QIcon(":/icons/tools.png"))
                self.category_items[category_name] = category_item

        # 创建工具项
        tool_item = QTreeWidgetItem(category_item)
        tool_item.setText(0, tool_cls["name"])
        # 设置工具图标
        tool_item.setIcon(0, QIcon(":/icons/tool.png"))
        # 使用工具索引作为用户数据，而不是工具类
        tool_item.setData(0, Qt.ItemDataRole.UserRole, tool_index)

        return tool_item 