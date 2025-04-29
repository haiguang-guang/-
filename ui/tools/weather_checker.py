from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QLineEdit, QPushButton, QMessageBox,
                            QLabel, QFrame, QGridLayout, QDialogButtonBox)
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings
import os
import requests
import json
import time

class WeatherThread(QThread):
    """线程用于在后台获取天气数据"""
    result_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    
    def __init__(self, city, api_key):
        super().__init__()
        self.city = city
        self.api_key = api_key
        
    def run(self):
        try:
            # 使用OpenWeatherMap API
            url = f"https://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.api_key}&units=metric&lang=zh_cn"
            
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                self.result_signal.emit(data)
            else:
                error_msg = f"API返回错误: {response.status_code}"
                if response.status_code == 404:
                    error_msg = "找不到该城市，请检查拼写"
                elif response.status_code == 401:
                    error_msg = "API密钥无效"
                self.error_signal.emit(error_msg)
                
        except Exception as e:
            self.error_signal.emit(str(e))

class APIKeyDialog(QDialog):
    """API密钥设置对话框"""
    def __init__(self, parent=None, current_key=""):
        super().__init__(parent)
        self.setWindowTitle("设置API密钥")
        self.setMinimumWidth(400)
        self.api_key = current_key
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 说明标签
        info_label = QLabel("请输入您的OpenWeatherMap API密钥:")
        info_label.setFont(QFont("Arial", 10))
        layout.addWidget(info_label)
        
        # 密钥输入框
        self.key_input = QLineEdit()
        self.key_input.setText(self.api_key)
        self.key_input.setPlaceholderText("例如: 1234567890abcdef1234567890abcdef")
        layout.addWidget(self.key_input)
        
        # 链接说明
        link_label = QLabel("您可以在<a href='https://openweathermap.org/api'>OpenWeatherMap</a>获取免费API密钥")
        link_label.setOpenExternalLinks(True)
        layout.addWidget(link_label)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_api_key(self):
        return self.key_input.text().strip()

class WeatherChecker(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("天气查询")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        self.weather_thread = None
        
        # 从设置中加载API密钥
        self.settings = QSettings("WeatherChecker", "APIKey")
        self.api_key = self.settings.value("api_key", "")
        
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题区域
        title_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/weather.png")
        if os.path.exists(icon_path):
            icon_label.setPixmap(QIcon(icon_path).pixmap(32, 32))
        
        title_label = QLabel("天气查询工具")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #03A9F4;")
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 添加设置按钮
        self.settings_btn = QPushButton("设置API密钥")
        self.settings_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/settings.png")))
        self.settings_btn.clicked.connect(self.open_api_settings)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #9E9E9E;
            }
        """)
        title_layout.addWidget(self.settings_btn)
        
        main_layout.addLayout(title_layout)
        
        # 说明文字
        info_label = QLabel("查询全球城市的实时天气信息。输入城市名称（如北京、上海、纽约等）获取当前天气状况。")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 13px; margin-bottom: 10px;")
        main_layout.addWidget(info_label)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #e0e0e0;")
        main_layout.addWidget(separator)
        
        # 搜索区域
        search_layout = QHBoxLayout()
        
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("输入城市名称（如：北京、上海、纽约）")
        self.city_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: #fafafa;
            }
            QLineEdit:focus {
                border: 1px solid #03A9F4;
                background-color: white;
            }
        """)
        
        self.search_btn = QPushButton("查询")
        self.search_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/search.png")))
        self.search_btn.clicked.connect(self.get_weather)
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: #03A9F4;
                color: white;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #29B6F6;
            }
        """)
        
        search_layout.addWidget(self.city_input, 1)
        search_layout.addWidget(self.search_btn, 0)
        
        main_layout.addLayout(search_layout)
        
        # 状态标签
        self.status_label = QLabel("请输入城市名称进行查询")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        main_layout.addWidget(self.status_label)
        
        # 天气显示区域
        self.weather_frame = QFrame()
        self.weather_frame.setFrameShape(QFrame.Shape.Box)
        self.weather_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.weather_frame.setStyleSheet("""
            QFrame {
                background-color: #E1F5FE;
                border: 1px solid #81D4FA;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.weather_frame.setVisible(False)
        
        weather_layout = QVBoxLayout(self.weather_frame)
        
        # 城市和日期
        header_layout = QHBoxLayout()
        
        self.city_label = QLabel("城市名称")
        self.city_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.city_label.setStyleSheet("color: #0288D1;")
        
        self.date_label = QLabel("日期时间")
        self.date_label.setStyleSheet("color: #666;")
        
        header_layout.addWidget(self.city_label)
        header_layout.addStretch()
        header_layout.addWidget(self.date_label)
        
        weather_layout.addLayout(header_layout)
        
        # 温度和天气图标
        temp_layout = QHBoxLayout()
        
        self.temp_label = QLabel("--°C")
        self.temp_label.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        self.temp_label.setStyleSheet("color: #FF9800;")
        
        self.icon_weather = QLabel()
        self.icon_weather.setFixedSize(100, 100)
        self.icon_weather.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        temp_layout.addWidget(self.temp_label)
        temp_layout.addStretch()
        temp_layout.addWidget(self.icon_weather)
        
        weather_layout.addLayout(temp_layout)
        
        # 天气描述
        self.description_label = QLabel("天气描述")
        self.description_label.setFont(QFont("Arial", 14))
        self.description_label.setStyleSheet("color: #546E7A;")
        weather_layout.addWidget(self.description_label)
        
        # 分隔线
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        separator2.setStyleSheet("background-color: #B3E5FC;")
        weather_layout.addWidget(separator2)
        
        # 详细信息
        details_layout = QGridLayout()
        details_layout.setVerticalSpacing(15)
        details_layout.setHorizontalSpacing(30)
        
        # 湿度
        humidity_label = QLabel("湿度")
        humidity_label.setStyleSheet("color: #666; font-weight: bold;")
        self.humidity_value = QLabel("--")
        details_layout.addWidget(humidity_label, 0, 0)
        details_layout.addWidget(self.humidity_value, 1, 0)
        
        # 风速
        wind_label = QLabel("风速")
        wind_label.setStyleSheet("color: #666; font-weight: bold;")
        self.wind_value = QLabel("--")
        details_layout.addWidget(wind_label, 0, 1)
        details_layout.addWidget(self.wind_value, 1, 1)
        
        # 气压
        pressure_label = QLabel("气压")
        pressure_label.setStyleSheet("color: #666; font-weight: bold;")
        self.pressure_value = QLabel("--")
        details_layout.addWidget(pressure_label, 0, 2)
        details_layout.addWidget(self.pressure_value, 1, 2)
        
        # 能见度
        visibility_label = QLabel("能见度")
        visibility_label.setStyleSheet("color: #666; font-weight: bold;")
        self.visibility_value = QLabel("--")
        details_layout.addWidget(visibility_label, 0, 3)
        details_layout.addWidget(self.visibility_value, 1, 3)
        
        weather_layout.addLayout(details_layout)
        
        main_layout.addWidget(self.weather_frame)
        main_layout.addStretch()
        
        # API密钥状态提示
        self.api_status_label = QLabel()
        if not self.api_key:
            self.api_status_label.setText("注意: 未设置API密钥，请点击右上角的\"设置API密钥\"按钮进行设置")
            self.api_status_label.setStyleSheet("color: #F44336; font-style: italic; font-size: 12px;")
        else:
            self.api_status_label.setText("API密钥已设置")
            self.api_status_label.setStyleSheet("color: #4CAF50; font-style: italic; font-size: 12px;")
        main_layout.addWidget(self.api_status_label)
        
    def open_api_settings(self):
        """打开API密钥设置对话框"""
        dialog = APIKeyDialog(self, self.api_key)
        if dialog.exec():
            new_key = dialog.get_api_key()
            if new_key != self.api_key:
                self.api_key = new_key
                # 保存到设置
                self.settings.setValue("api_key", self.api_key)
                if self.api_key:
                    self.api_status_label.setText("API密钥已更新")
                    self.api_status_label.setStyleSheet("color: #4CAF50; font-style: italic; font-size: 12px;")
                else:
                    self.api_status_label.setText("注意: 未设置API密钥，请点击右上角的\"设置API密钥\"按钮进行设置")
                    self.api_status_label.setStyleSheet("color: #F44336; font-style: italic; font-size: 12px;")
        
    def get_weather(self):
        city = self.city_input.text().strip()
        if not city:
            QMessageBox.warning(self, "警告", "请输入城市名称")
            return
            
        if not self.api_key:
            result = QMessageBox.question(
                self, 
                "API密钥未设置", 
                "您尚未设置OpenWeatherMap API密钥，无法获取天气数据。是否现在设置API密钥？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if result == QMessageBox.StandardButton.Yes:
                self.open_api_settings()
            return
            
        self.status_label.setText(f"正在查询 {city} 的天气信息...")
        self.status_label.setStyleSheet("color: #03A9F4;")
        
        # 禁用搜索按钮
        self.search_btn.setEnabled(False)
        
        # 创建并启动线程
        self.weather_thread = WeatherThread(city, self.api_key)
        self.weather_thread.result_signal.connect(self.handle_weather_data)
        self.weather_thread.error_signal.connect(self.handle_weather_error)
        self.weather_thread.finished.connect(lambda: self.search_btn.setEnabled(True))
        self.weather_thread.start()
        
    def handle_weather_data(self, data):
        try:
            # 更新城市标签
            self.city_label.setText(f"{data['name']}, {data['sys']['country']}")
            
            # 更新日期标签
            timestamp = data['dt']
            date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(timestamp))
            self.date_label.setText(date_str)
            
            # 更新温度标签
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            self.temp_label.setText(f"{temp:.1f}°C")
            
            # 更新天气描述
            weather = data['weather'][0]
            description = weather['description']
            self.description_label.setText(f"{description.capitalize()}（体感温度: {feels_like:.1f}°C）")
            
            # 更新天气图标
            icon_code = weather['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
            
            # 尝试下载天气图标
            try:
                response = requests.get(icon_url)
                if response.status_code == 200:
                    icon_data = response.content
                    pixmap = QPixmap()
                    pixmap.loadFromData(icon_data)
                    if not pixmap.isNull():
                        self.icon_weather.setPixmap(pixmap)
            except:
                # 下载图标失败时不处理
                pass
            
            # 更新详细信息
            humidity = data['main']['humidity']
            self.humidity_value.setText(f"{humidity}%")
            
            wind_speed = data['wind']['speed']
            self.wind_value.setText(f"{wind_speed} m/s")
            
            pressure = data['main']['pressure']
            self.pressure_value.setText(f"{pressure} hPa")
            
            visibility = data.get('visibility', 0)
            self.visibility_value.setText(f"{visibility/1000:.1f} km")
            
            # 显示天气框
            self.weather_frame.setVisible(True)
            
            self.status_label.setText(f"{data['name']} 天气数据获取成功")
            self.status_label.setStyleSheet("color: #4CAF50;")
            
        except Exception as e:
            self.status_label.setText(f"处理天气数据时出错: {str(e)}")
            self.status_label.setStyleSheet("color: #D32F2F;")
            self.weather_frame.setVisible(False)
            
    def handle_weather_error(self, error_msg):
        self.status_label.setText(f"获取天气数据失败: {error_msg}")
        self.status_label.setStyleSheet("color: #D32F2F;")
        self.weather_frame.setVisible(False)
        QMessageBox.critical(self, "错误", f"获取天气数据失败: {error_msg}")
        self.search_btn.setEnabled(True) 