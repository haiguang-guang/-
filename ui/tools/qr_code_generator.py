from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, 
                            QPushButton, QLabel, QFileDialog, QMessageBox,
                            QHBoxLayout, QFrame, QComboBox, QSpinBox, QDialog)
from PyQt6.QtGui import QPixmap, QFont, QIcon, QImage, QGuiApplication
from PyQt6.QtCore import Qt, QSize
import qrcode
from PIL import Image
import os
import traceback
import sys

class QRCodeGenerator(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("二维码生成器")
        self.setModal(True)
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 标题区域
        title_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/qrcode.png")
        if os.path.exists(icon_path):
            icon_label.setPixmap(QIcon(icon_path).pixmap(32, 32))
        
        title_label = QLabel("二维码生成工具")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #673AB7;")
        
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        main_layout.addLayout(title_layout)
        
        # 说明文字
        info_label = QLabel("生成二维码以便分享链接和文本信息。支持自定义大小和颜色。")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 13px; margin-bottom: 10px;")
        main_layout.addWidget(info_label)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #e0e0e0;")
        main_layout.addWidget(separator)
        
        # 输入区域
        input_layout = QHBoxLayout()
        
        input_label = QLabel("输入文本或URL:")
        input_label.setFont(QFont("Arial", 12))
        input_label.setStyleSheet("color: #333;")
        
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("请输入要生成二维码的文本或URL...")
        self.text_input.setFont(QFont("Arial", 12))
        self.text_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px;
                background-color: #fafafa;
            }
            QLineEdit:focus {
                border: 1px solid #673AB7;
                background-color: white;
            }
        """)
        
        input_layout.addWidget(input_label, 0)
        input_layout.addWidget(self.text_input, 1)
        
        main_layout.addLayout(input_layout)
        
        # 选项区域
        options_layout = QHBoxLayout()
        
        # 大小选项
        size_label = QLabel("尺寸:")
        size_label.setStyleSheet("color: #666;")
        
        self.size_spinner = QSpinBox()
        self.size_spinner.setMinimum(1)
        self.size_spinner.setMaximum(10)
        self.size_spinner.setValue(5)
        self.size_spinner.setStyleSheet("""
            QSpinBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
                background: white;
                min-width: 60px;
            }
        """)
        
        # 错误校正选项
        error_label = QLabel("纠错级别:")
        error_label.setStyleSheet("color: #666;")
        
        self.error_combo = QComboBox()
        self.error_combo.addItems(["低", "中", "高", "最高"])
        self.error_combo.setCurrentIndex(1)  # 默认中
        self.error_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
                background: white;
                min-width: 80px;
            }
        """)
        
        options_layout.addWidget(size_label)
        options_layout.addWidget(self.size_spinner)
        options_layout.addSpacing(20)
        options_layout.addWidget(error_label)
        options_layout.addWidget(self.error_combo)
        options_layout.addStretch()
        
        main_layout.addLayout(options_layout)
        
        # 生成按钮
        generate_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("生成二维码")
        self.generate_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/generate.png")))
        self.generate_btn.clicked.connect(self.generate_qr)
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #673AB7;
                color: white;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 14px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #7E57C2;
            }
        """)
        
        generate_layout.addStretch()
        generate_layout.addWidget(self.generate_btn)
        generate_layout.addStretch()
        
        main_layout.addLayout(generate_layout)
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        main_layout.addWidget(self.status_label)
        
        # 二维码显示区域
        self.qr_frame = QFrame()
        self.qr_frame.setFrameShape(QFrame.Shape.Box)
        self.qr_frame.setFrameShadow(QFrame.Shadow.Sunken)
        self.qr_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px dashed #ccc;
                border-radius: 10px;
            }
        """)
        self.qr_frame.setMinimumHeight(300)
        
        qr_layout = QVBoxLayout(self.qr_frame)
        
        self.qr_label = QLabel("在此处显示二维码")
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setStyleSheet("border: none; color: #999; font-style: italic;")
        qr_layout.addWidget(self.qr_label)
        
        main_layout.addWidget(self.qr_frame, 1)
        
        # 保存按钮
        btn_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("保存二维码")
        self.save_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/save.png")))
        self.save_btn.clicked.connect(self.save_qr)
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #EEEEEE;
            }
        """)
        
        self.copy_btn = QPushButton("复制二维码")
        self.copy_btn.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons/copy.png")))
        self.copy_btn.clicked.connect(self.copy_qr)
        self.copy_btn.setEnabled(False)
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #EEEEEE;
            }
        """)
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.copy_btn)
        
        main_layout.addLayout(btn_layout)
        
    def generate_qr(self):
        try:
            text = self.text_input.text()
            if not text:
                QMessageBox.warning(self, "警告", "请输入文本或URL")
                return
            
            self.status_label.setText("正在生成二维码...")
            self.status_label.setStyleSheet("color: #673AB7; font-style: italic;")
            
            # 获取用户选项
            box_size = self.size_spinner.value() * 2  # 乘2以获得更合适的尺寸
            
            # 获取错误校正级别
            error_corrections = [
                qrcode.constants.ERROR_CORRECT_L,
                qrcode.constants.ERROR_CORRECT_M,
                qrcode.constants.ERROR_CORRECT_Q,
                qrcode.constants.ERROR_CORRECT_H
            ]
            error_level = error_corrections[self.error_combo.currentIndex()]
            
            # 创建二维码
            qr = qrcode.QRCode(
                version=1,
                error_correction=error_level,
                box_size=box_size,
                border=4,
            )
            qr.add_data(text)
            qr.make(fit=True)
            
            # 生成二维码图片
            self.qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # 将PIL图像转换为QPixmap
            img_path = os.path.join(os.path.dirname(__file__), "temp_qr.png")
            self.qr_image.save(img_path)
            
            pixmap = QPixmap(img_path)
            if os.path.exists(img_path):
                os.remove(img_path)
            
            # 调整大小并显示
            if not pixmap.isNull():
                size = min(self.qr_frame.width(), self.qr_frame.height()) - 30
                pixmap = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.qr_label.setPixmap(pixmap)
                self.qr_label.setStyleSheet("border: none;")
                
                # 激活按钮
                self.save_btn.setEnabled(True)
                self.copy_btn.setEnabled(True)
                
                # 更新状态
                self.status_label.setText("二维码已生成，内容: " + (text[:30] + "..." if len(text) > 30 else text))
                self.status_label.setStyleSheet("color: #4CAF50; font-style: normal;")
            else:
                self.qr_label.setText("无法显示二维码")
                self.status_label.setText("生成二维码失败")
                self.status_label.setStyleSheet("color: #F44336; font-style: italic;")
                self.save_btn.setEnabled(False)
                self.copy_btn.setEnabled(False)
            
        except Exception as e:
            error_details = traceback.format_exc()
            self.qr_label.setText("生成二维码失败")
            self.status_label.setText(f"错误: {str(e)}")
            self.status_label.setStyleSheet("color: #F44336; font-style: italic;")
            QMessageBox.critical(self, "错误", f"生成二维码时出错: {str(e)}\n\n详细信息:\n{error_details}")
            self.save_btn.setEnabled(False)
            self.copy_btn.setEnabled(False)
            
    def save_qr(self):
        try:
            if not hasattr(self, 'qr_image'):
                QMessageBox.warning(self, "警告", "请先生成二维码")
                return
                
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存二维码", "", "PNG图像 (*.png);;所有文件 (*)"
            )
            
            if file_path:
                # 确保文件扩展名为.png
                if not file_path.lower().endswith('.png'):
                    file_path += '.png'
                    
                self.qr_image.save(file_path)
                self.status_label.setText(f"二维码已保存到: {os.path.basename(file_path)}")
                self.status_label.setStyleSheet("color: #4CAF50; font-style: normal;")
                QMessageBox.information(self, "成功", f"二维码已保存到: {file_path}")
        except Exception as e:
            error_details = traceback.format_exc()
            self.status_label.setText(f"保存失败: {str(e)}")
            self.status_label.setStyleSheet("color: #F44336; font-style: italic;")
            QMessageBox.critical(self, "错误", f"保存二维码时出错: {str(e)}\n\n详细信息:\n{error_details}")
            
    def copy_qr(self):
        """复制二维码到剪贴板"""
        try:
            if not hasattr(self, 'qr_image'):
                QMessageBox.warning(self, "警告", "请先生成二维码")
                return
                
            # 临时保存图像
            temp_path = os.path.join(os.path.dirname(__file__), "temp_qr_copy.png")
            self.qr_image.save(temp_path)
            
            # 加载为QPixmap
            pixmap = QPixmap(temp_path)
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            # 复制到剪贴板
            clipboard = QGuiApplication.clipboard()
            clipboard.setPixmap(pixmap)
            
            self.status_label.setText("二维码已复制到剪贴板")
            self.status_label.setStyleSheet("color: #4CAF50; font-style: normal;")
            QMessageBox.information(self, "成功", "二维码已复制到剪贴板")
        except Exception as e:
            self.status_label.setText(f"复制失败: {str(e)}")
            self.status_label.setStyleSheet("color: #F44336; font-style: italic;")
            QMessageBox.critical(self, "错误", f"复制二维码时出错: {str(e)}") 