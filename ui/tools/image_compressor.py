from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QFileDialog, 
                            QSlider, QMessageBox, QProgressBar)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from PIL import Image
import os

class ImageCompressor(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("图片压缩")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        self.selected_image = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 选择图片按钮
        select_btn = QPushButton("选择图片")
        select_btn.clicked.connect(self.select_image)
        layout.addWidget(select_btn)
        
        # 图片预览
        self.image_preview = QLabel("图片预览")
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setMinimumHeight(200)
        self.image_preview.setStyleSheet("border: 1px solid #ccc;")
        layout.addWidget(self.image_preview)
        
        # 图片信息
        self.image_info = QLabel("未选择图片")
        self.image_info.setFont(QFont("Arial", 12))
        layout.addWidget(self.image_info)
        
        # 压缩质量滑块
        quality_layout = QHBoxLayout()
        
        quality_label = QLabel("压缩质量:")
        quality_label.setFont(QFont("Arial", 12))
        quality_layout.addWidget(quality_label)
        
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setMinimum(1)
        self.quality_slider.setMaximum(100)
        self.quality_slider.setValue(80)
        quality_layout.addWidget(self.quality_slider)
        
        self.quality_value = QLabel("80%")
        self.quality_value.setFont(QFont("Arial", 12))
        quality_layout.addWidget(self.quality_value)
        
        layout.addLayout(quality_layout)
        
        # 压缩按钮
        compress_btn = QPushButton("压缩图片")
        compress_btn.clicked.connect(self.compress_image)
        layout.addWidget(compress_btn)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 质量滑块变化事件
        self.quality_slider.valueChanged.connect(self.update_quality_label)
        
    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "图像文件 (*.jpg *.jpeg *.png *.bmp)"
        )
        
        if file_path:
            self.selected_image = file_path
            
            # 显示图片预览
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(300, 200, Qt.AspectRatioMode.KeepAspectRatio)
                self.image_preview.setPixmap(pixmap)
                
                # 显示图片信息
                try:
                    img = Image.open(file_path)
                    file_size = os.path.getsize(file_path) / 1024  # KB
                    info = f"文件: {os.path.basename(file_path)}\n"
                    info += f"尺寸: {img.width} x {img.height} 像素\n"
                    info += f"大小: {file_size:.2f} KB"
                    self.image_info.setText(info)
                except Exception as e:
                    self.image_info.setText(f"无法读取图片信息: {str(e)}")
            else:
                self.image_preview.setText("预览失败")
                self.image_info.setText(f"文件: {os.path.basename(file_path)}")
                
    def update_quality_label(self, value):
        self.quality_value.setText(f"{value}%")
        
    def compress_image(self):
        if not self.selected_image:
            QMessageBox.warning(self, "警告", "请先选择图片")
            return
            
        output_path, _ = QFileDialog.getSaveFileName(
            self, "保存压缩后的图片", "", "JPEG图像 (*.jpg);;PNG图像 (*.png)"
        )
        
        if not output_path:
            return
            
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(10)
            
            # 打开图片
            img = Image.open(self.selected_image)
            
            self.progress_bar.setValue(30)
            
            # 获取用户选择的质量
            quality = self.quality_slider.value()
            
            # 确定输出格式
            if output_path.lower().endswith('.png'):
                format = 'PNG'
            else:
                format = 'JPEG'
                if not output_path.lower().endswith('.jpg') and not output_path.lower().endswith('.jpeg'):
                    output_path += '.jpg'
                    
            self.progress_bar.setValue(60)
            
            # 保存压缩后的图片
            img.save(output_path, format=format, quality=quality, optimize=True)
            
            self.progress_bar.setValue(100)
            
            # 显示压缩结果
            original_size = os.path.getsize(self.selected_image) / 1024  # KB
            compressed_size = os.path.getsize(output_path) / 1024  # KB
            
            result = f"压缩完成!\n"
            result += f"原始大小: {original_size:.2f} KB\n"
            result += f"压缩后大小: {compressed_size:.2f} KB\n"
            result += f"节省空间: {(original_size - compressed_size):.2f} KB "
            result += f"({(1 - compressed_size/original_size) * 100:.1f}%)"
            
            QMessageBox.information(self, "压缩成功", result)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"压缩图片时出错: {str(e)}")
        finally:
            self.progress_bar.setVisible(False) 