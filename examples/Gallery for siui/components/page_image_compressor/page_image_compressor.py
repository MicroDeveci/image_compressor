"""
图片压缩工具页面
"""
import os
import sys
import threading
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTextEdit

from siui.components import SiTitledWidgetGroup
from siui.components.page import SiPage
from siui.components.progress_bar import SiProgressBar
from siui.components.widgets import (
    SiDenseHContainer,
    SiDenseVContainer,
    SiLabel,
    SiLineEdit,
    SiPushButton,
    SiRadioButton,
    SiSimpleButton,
)
from siui.components.spinbox.spinbox import SiIntSpinBox, SiDoubleSpinBox
from siui.core import SiGlobal

# 导入压缩功能模块
# 计算 code 目录的路径：从当前文件位置回到项目根目录
_current_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_current_dir, '../../../../'))
_code_dir = os.path.join(_project_root, 'code')
sys.path.insert(0, _code_dir)
from compressors import compress_image_fixed_quality, compress_image_to_size
from file_utils import get_image_files, get_output_path, format_size


class CompressionWorker(QThread):
    """压缩工作线程"""
    progress_updated = pyqtSignal(int, int)  # 当前索引, 总数
    log_message = pyqtSignal(str)  # 日志消息
    finished = pyqtSignal(int, int, int)  # 成功数, 失败数, 总大小

    def __init__(self, input_path, output_dir, mode, quality=None, target_size_mb=None):
        super().__init__()
        self.input_path = input_path
        self.output_dir = output_dir
        self.mode = mode
        self.quality = quality
        self.target_size_mb = target_size_mb
        self.is_cancelled = False

    def cancel(self):
        """取消压缩"""
        self.is_cancelled = True

    def run(self):
        """执行压缩"""
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            
            self.log_message.emit("正在扫描图片文件...")
            image_files = get_image_files(self.input_path)
            
            if not image_files:
                self.log_message.emit("❌ 未找到任何图片文件！")
                self.finished.emit(0, 0, 0)
                return
            
            total_files = len(image_files)
            self.log_message.emit(f"找到 {total_files} 张图片\n")
            
            total_size = 0
            success_count = 0
            fail_count = 0
            
            if self.mode == "quality":
                self.log_message.emit(f"开始压缩（质量: {self.quality}）...\n")
                
                for idx, (root, file) in enumerate(image_files, 1):
                    if self.is_cancelled:
                        break
                    
                    input_file_path = os.path.join(root, file)
                    output_file_path = get_output_path(input_file_path, self.input_path, self.output_dir)
                    
                    try:
                        if compress_image_fixed_quality(input_file_path, output_file_path, self.quality):
                            size = os.path.getsize(output_file_path)
                            total_size += size
                            success_count += 1
                            self.log_message.emit(f"✔ [{idx}/{total_files}] {file} → {format_size(size)}")
                        else:
                            fail_count += 1
                            self.log_message.emit(f"✖ [{idx}/{total_files}] {file} 压缩失败")
                    except Exception as e:
                        fail_count += 1
                        self.log_message.emit(f"✖ [{idx}/{total_files}] {file} 压缩失败: {str(e)}")
                    
                    self.progress_updated.emit(idx, total_files)
            
            else:  # size mode
                total_max_size = int(self.target_size_mb * 1024 * 1024)
                target_size_per_image = total_max_size // total_files
                
                self.log_message.emit(f"目标总大小: {format_size(total_max_size)}")
                self.log_message.emit(f"平均每张目标大小: {format_size(target_size_per_image)}\n")
                
                for idx, (root, file) in enumerate(image_files, 1):
                    if self.is_cancelled:
                        break
                    
                    input_file_path = os.path.join(root, file)
                    output_file_path = get_output_path(input_file_path, self.input_path, self.output_dir)
                    
                    try:
                        if compress_image_to_size(input_file_path, output_file_path, target_size_per_image):
                            size = os.path.getsize(output_file_path)
                            total_size += size
                            success_count += 1
                            self.log_message.emit(f"✔ [{idx}/{total_files}] {file} → {format_size(size)} (累计: {format_size(total_size)})")
                        else:
                            fail_count += 1
                            self.log_message.emit(f"✖ [{idx}/{total_files}] {file} 压缩失败")
                    except Exception as e:
                        fail_count += 1
                        self.log_message.emit(f"✖ [{idx}/{total_files}] {file} 压缩失败: {str(e)}")
                    
                    self.progress_updated.emit(idx, total_files)
                
                # 在 size 模式下检查是否达到目标大小
                self.log_message.emit("\n" + "="*50)
                self.log_message.emit("=== 处理完成 ===")
                self.log_message.emit(f"成功: {success_count} 张")
                if fail_count > 0:
                    self.log_message.emit(f"失败: {fail_count} 张")
                self.log_message.emit(f"总大小: {format_size(total_size)}")
                self.log_message.emit(f"输出目录: {self.output_dir}")
                
                if total_size <= total_max_size:
                    self.log_message.emit("✓ 已达到目标大小要求")
                else:
                    overflow = total_size - total_max_size
                    self.log_message.emit(f"⚠ 超出目标大小 {format_size(overflow)}")
                
                self.finished.emit(success_count, fail_count, total_size)
                return
            
            # quality 模式的处理完成信息
            self.log_message.emit("\n" + "="*50)
            self.log_message.emit("=== 处理完成 ===")
            self.log_message.emit(f"成功: {success_count} 张")
            if fail_count > 0:
                self.log_message.emit(f"失败: {fail_count} 张")
            self.log_message.emit(f"总大小: {format_size(total_size)}")
            self.log_message.emit(f"输出目录: {self.output_dir}")
            
            self.finished.emit(success_count, fail_count, total_size)
        
        except Exception as e:
            self.log_message.emit(f"\n❌ 发生错误: {str(e)}")
            self.finished.emit(0, 0, 0)


class ImageCompressorPage(SiPage):
    """图片压缩工具页面"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.setPadding(64)
        self.setScrollMaximumWidth(1000)
        self.setScrollAlignment(Qt.AlignLeft)
        self.setTitle("图片压缩工具")
        
        # 创建控件组
        self.titled_widgets_group = SiTitledWidgetGroup(self)
        self.titled_widgets_group.setSpacing(32)
        self.titled_widgets_group.setAdjustWidgetsSize(True)
        
        # 输入路径选择
        with self.titled_widgets_group as group:
            group.addTitle("输入设置")
            
            input_container = SiDenseVContainer(self)
            input_container.setSpacing(12)
            
            # 输入路径
            input_path_container = SiDenseHContainer(self)
            input_path_container.setSpacing(8)
            
            self.input_path_edit = SiLineEdit(self)
            self.input_path_edit.lineEdit().setPlaceholderText("选择输入文件夹或单张图片")
            self.input_path_edit.resize(400, 32)
            
            self.browse_input_btn = SiPushButton(self)
            self.browse_input_btn.attachment().setText("浏览")
            self.browse_input_btn.resize(80, 32)
            self.browse_input_btn.clicked.connect(self.browse_input)
            
            input_path_container.addWidget(self.input_path_edit)
            input_path_container.addWidget(self.browse_input_btn)
            
            # 输出路径
            output_path_container = SiDenseHContainer(self)
            output_path_container.setSpacing(8)
            
            self.output_path_edit = SiLineEdit(self)
            self.output_path_edit.lineEdit().setPlaceholderText("选择输出目录（默认：输入目录/compressed）")
            self.output_path_edit.resize(400, 32)
            
            self.browse_output_btn = SiPushButton(self)
            self.browse_output_btn.attachment().setText("浏览")
            self.browse_output_btn.resize(80, 32)
            self.browse_output_btn.clicked.connect(self.browse_output)
            
            output_path_container.addWidget(self.output_path_edit)
            output_path_container.addWidget(self.browse_output_btn)
            
            input_container.addWidget(input_path_container)
            input_container.addWidget(output_path_container)
            
            group.addWidget(input_container)
        
        # 压缩模式选择
        with self.titled_widgets_group as group:
            group.addTitle("压缩模式")
            
            mode_container = SiDenseVContainer(self)
            mode_container.setSpacing(16)
            
            # 固定质量模式
            quality_mode_container = SiDenseVContainer(self)
            quality_mode_container.setSpacing(8)
            
            self.quality_radio = SiRadioButton(self)
            self.quality_radio.setText("固定质量压缩（推荐，速度快）")
            self.quality_radio.setChecked(True)
            self.quality_radio.toggled.connect(self.on_mode_change)
            
            quality_setting_container = SiDenseHContainer(self)
            quality_setting_container.setSpacing(8)
            quality_setting_container.move(32, 0)
            
            quality_label = SiLabel(self)
            quality_label.setText("JPEG质量:")
            quality_label.resize(80, 32)
            
            self.quality_spinbox = SiIntSpinBox(self)
            self.quality_spinbox.setMinimum(1)
            self.quality_spinbox.setMaximum(100)
            self.quality_spinbox.setValue(85)
            self.quality_spinbox.resize(100, 32)
            
            quality_hint_label = SiLabel(self)
            quality_hint_label.setText("(1-100，推荐60-85)")
            quality_hint_label.setStyleSheet("color: {}".format(SiGlobal.siui.colors["TEXT_B"]))
            
            quality_setting_container.addWidget(quality_label)
            quality_setting_container.addWidget(self.quality_spinbox)
            quality_setting_container.addWidget(quality_hint_label)
            
            quality_mode_container.addWidget(self.quality_radio)
            quality_mode_container.addWidget(quality_setting_container)
            
            # 目标大小模式
            size_mode_container = SiDenseVContainer(self)
            size_mode_container.setSpacing(8)
            
            self.size_radio = SiRadioButton(self)
            self.size_radio.setText("目标大小压缩（压缩到指定总大小）")
            self.size_radio.toggled.connect(self.on_mode_change)
            
            size_setting_container = SiDenseHContainer(self)
            size_setting_container.setSpacing(8)
            size_setting_container.move(32, 0)
            
            size_label = SiLabel(self)
            size_label.setText("目标总大小:")
            size_label.resize(100, 32)
            
            self.size_spinbox = SiDoubleSpinBox(self)
            self.size_spinbox.setMinimum(0.1)
            self.size_spinbox.setMaximum(1000.0)
            self.size_spinbox.setValue(20.0)
            self.size_spinbox.setSingleStep(1.0)
            self.size_spinbox.resize(100, 32)
            
            size_unit_label = SiLabel(self)
            size_unit_label.setText("MB")
            size_unit_label.resize(40, 32)
            
            size_setting_container.addWidget(size_label)
            size_setting_container.addWidget(self.size_spinbox)
            size_setting_container.addWidget(size_unit_label)
            
            size_mode_container.addWidget(self.size_radio)
            size_mode_container.addWidget(size_setting_container)
            
            mode_container.addWidget(quality_mode_container)
            mode_container.addWidget(size_mode_container)
            
            group.addWidget(mode_container)
        
        # 开始按钮和进度条
        with self.titled_widgets_group as group:
            group.addTitle("执行压缩")
            
            action_container = SiDenseVContainer(self)
            action_container.setSpacing(12)
            
            # 开始按钮
            self.start_button = SiPushButton(self)
            self.start_button.attachment().setText("开始压缩")
            self.start_button.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_play_filled"))
            self.start_button.resize(150, 36)
            self.start_button.clicked.connect(self.start_compression)
            
            # 取消按钮（初始隐藏）
            self.cancel_button = SiPushButton(self)
            self.cancel_button.attachment().setText("取消")
            self.cancel_button.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_dismiss_filled"))
            self.cancel_button.resize(150, 36)
            self.cancel_button.hide()
            self.cancel_button.clicked.connect(self.cancel_compression)
            
            button_container = SiDenseHContainer(self)
            button_container.setSpacing(12)
            button_container.addWidget(self.start_button)
            button_container.addWidget(self.cancel_button)
            
            # 进度条
            self.progress_bar = SiProgressBar(self)
            self.progress_bar.resize(500, 32)
            
            self.progress_label = SiLabel(self)
            self.progress_label.setText("")
            self.progress_label.setStyleSheet("color: {}".format(SiGlobal.siui.colors["TEXT_B"]))
            
            action_container.addWidget(button_container)
            action_container.addWidget(self.progress_bar)
            action_container.addWidget(self.progress_label)
            
            group.addWidget(action_container)
        
        # 添加提示信息
        with self.titled_widgets_group as group:
            group.addTitle("提示")
            
            hint_label = SiLabel(self)
            hint_label.setWordWrap(True)
            hint_label.setStyleSheet("color: {};".format(SiGlobal.siui.colors["TEXT_B"]))
            hint_label.setText("处理日志将显示在\"日志查看器\"页面中。\n开始压缩后，请切换到日志查看器页面查看详细处理信息。")
            hint_label.setAlignment(Qt.AlignLeft)
            
            group.addWidget(hint_label)
        
        # 添加页脚的空白
        self.titled_widgets_group.addPlaceholder(64)
        
        # 设置控件组为页面对象
        self.setAttachment(self.titled_widgets_group)
        
        # 工作线程
        self.worker = None
        
        # 日志查看器页面引用
        self.log_viewer_page = None
        
        # 初始化模式
        self.on_mode_change()
    
    def set_log_viewer(self, log_viewer_page):
        """设置日志查看器页面"""
        self.log_viewer_page = log_viewer_page
    
    def on_mode_change(self):
        """压缩模式改变时的回调"""
        if self.quality_radio.isChecked():
            self.quality_spinbox.setEnabled(True)
            self.size_spinbox.setEnabled(False)
        else:
            self.quality_spinbox.setEnabled(False)
            self.size_spinbox.setEnabled(True)
    
    def browse_input(self):
        """浏览输入路径"""
        # 先尝试选择文件夹
        path = QFileDialog.getExistingDirectory(self, "选择输入文件夹")
        if not path:
            # 如果取消，尝试选择文件
            path, _ = QFileDialog.getOpenFileName(
                self,
                "选择输入图片",
                "",
                "图片文件 (*.jpg *.jpeg *.png *.bmp *.webp);;所有文件 (*.*)"
            )
        
        if path:
            self.input_path_edit.lineEdit().setText(path)
            if not self.output_path_edit.lineEdit().text():
                if os.path.isfile(path):
                    output_dir = os.path.join(os.path.dirname(path), "compressed")
                else:
                    output_dir = os.path.join(path, "compressed")
                self.output_path_edit.lineEdit().setText(output_dir)
    
    def browse_output(self):
        """浏览输出路径"""
        path = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if path:
            self.output_path_edit.lineEdit().setText(path)
    
    def log(self, message):
        """添加日志到日志查看器页面"""
        if self.log_viewer_page:
            self.log_viewer_page.append_log(message)
    
    def start_compression(self):
        """开始压缩"""
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "警告", "正在处理中，请等待...")
            return
        
        input_path = self.input_path_edit.lineEdit().text().strip()
        if not input_path or not os.path.exists(input_path):
            QMessageBox.critical(self, "错误", "请输入有效的输入路径！")
            return
        
        output_path = self.output_path_edit.lineEdit().text().strip()
        if not output_path:
            QMessageBox.critical(self, "错误", "请输入输出目录！")
            return
        
        # 确定压缩模式
        if self.quality_radio.isChecked():
            mode = "quality"
            quality = self.quality_spinbox.value()
            target_size_mb = None
        else:
            mode = "size"
            quality = None
            target_size_mb = self.size_spinbox.value()
        
        # 清空日志查看器（如果存在）
        if self.log_viewer_page:
            self.log_viewer_page.clear_log()
            self.log_viewer_page.append_log("开始新的压缩任务...")
        
        # 创建并启动工作线程
        self.worker = CompressionWorker(input_path, output_path, mode, quality, target_size_mb)
        self.worker.progress_updated.connect(self.on_progress_updated)
        self.worker.log_message.connect(self.log)
        self.worker.finished.connect(self.on_compression_finished)
        
        # 更新UI状态
        self.start_button.setEnabled(False)
        self.cancel_button.show()
        self.cancel_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("准备中...")
        
        self.worker.start()
    
    def cancel_compression(self):
        """取消压缩"""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.log("用户取消了压缩操作")
            self.cancel_button.setEnabled(False)
    
    def on_progress_updated(self, current, total):
        """进度更新"""
        progress = (current / total) * 100 if total > 0 else 0
        self.progress_bar.setValue(progress / 100.0)
        self.progress_label.setText(f"处理中: {current}/{total}")
    
    def on_compression_finished(self, success_count, fail_count, total_size):
        """压缩完成"""
        self.start_button.setEnabled(True)
        self.cancel_button.hide()
        self.progress_label.setText(f"完成: {success_count} 张成功，{fail_count} 张失败")
        
        QMessageBox.information(
            self,
            "完成",
            f"压缩完成！\n成功: {success_count} 张\n失败: {fail_count} 张\n总大小: {format_size(total_size)}"
        )

