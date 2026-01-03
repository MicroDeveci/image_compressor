"""
日志查看器页面
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTextEdit, QPushButton, QFileDialog

from siui.components import SiTitledWidgetGroup
from siui.components.page import SiPage
from siui.components.widgets import (
    SiDenseHContainer,
    SiDenseVContainer,
    SiLabel,
    SiPushButton,
)
from siui.core import SiGlobal


class LogViewerPage(SiPage):
    """日志查看器页面"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.setPadding(64)
        self.setScrollMaximumWidth(1000)
        self.setScrollAlignment(Qt.AlignLeft)
        self.setTitle("日志查看器")
        
        # 创建控件组
        self.titled_widgets_group = SiTitledWidgetGroup(self)
        self.titled_widgets_group.setSpacing(32)
        self.titled_widgets_group.setAdjustWidgetsSize(True)
        
        # 日志显示区域
        with self.titled_widgets_group as group:
            group.addTitle("日志内容")
            
            # 操作按钮容器
            button_container = SiDenseHContainer(self)
            button_container.setSpacing(12)
            
            # 清空日志按钮
            self.clear_button = SiPushButton(self)
            self.clear_button.attachment().setText("清空日志")
            self.clear_button.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_delete_regular"))
            self.clear_button.resize(120, 32)
            self.clear_button.clicked.connect(self.clear_log)
            
            # 保存日志按钮
            self.save_button = SiPushButton(self)
            self.save_button.attachment().setText("保存日志")
            self.save_button.attachment().load(SiGlobal.siui.iconpack.get("ic_fluent_save_regular"))
            self.save_button.resize(120, 32)
            self.save_button.clicked.connect(self.save_log)
            
            button_container.addWidget(self.clear_button)
            button_container.addWidget(self.save_button)
            
            group.addWidget(button_container)
            
            # 使用 QTextEdit 显示日志，支持滚动
            self.log_text = QTextEdit(self)
            self.log_text.setReadOnly(True)
            self.log_text.setStyleSheet(
                "background-color: {}; "
                "border-radius: 4px; "
                "padding: 12px; "
                "color: {}; "
                "font-family: 'Consolas', 'Monaco', monospace; "
                "font-size: 11px; "
                "border: 1px solid {};".format(
                    SiGlobal.siui.colors["INTERFACE_BG_E"],
                    SiGlobal.siui.colors["TEXT_A"],
                    SiGlobal.siui.colors["INTERFACE_BG_D"]
                )
            )
            # 设置最小高度，让日志区域可以占据更多空间
            self.log_text.setMinimumHeight(400)
            self.log_text.setPlainText("日志查看器已就绪。\n\n图片压缩工具的处理日志将显示在这里。")
            
            group.addWidget(self.log_text)
        
        # 添加页脚的空白
        self.titled_widgets_group.addPlaceholder(64)
        
        # 设置控件组为页面对象
        self.setAttachment(self.titled_widgets_group)
    
    def append_log(self, message):
        """添加日志消息"""
        current_text = self.log_text.toPlainText()
        if current_text == "日志查看器已就绪。\n\n图片压缩工具的处理日志将显示在这里。":
            self.log_text.setPlainText(message)
        else:
            self.log_text.setPlainText(current_text + "\n" + message)
        # 自动滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def clear_log(self):
        """清空日志"""
        self.log_text.setPlainText("日志已清空。")
    
    def save_log(self):
        """保存日志到文件"""
        log_content = self.log_text.toPlainText()
        if not log_content or log_content == "日志已清空。":
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存日志",
            "",
            "文本文件 (*.txt);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                self.append_log(f"\n日志已保存到: {file_path}")
            except Exception as e:
                self.append_log(f"\n保存日志失败: {str(e)}")
    
    def get_log_text_widget(self):
        """获取日志文本控件（供其他页面使用）"""
        return self.log_text

