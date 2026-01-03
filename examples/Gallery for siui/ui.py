import icons
from components.page_about import About
from components.page_image_compressor import ImageCompressorPage
from components.page_log_viewer import LogViewerPage
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDesktopWidget

import siui
from siui.core import SiColor, SiGlobal
from siui.templates.application.application import SiliconApplication

# 载入图标
siui.core.globals.SiGlobal.siui.loadIcons(
    icons.IconDictionary(color=SiGlobal.siui.colors.fromToken(SiColor.SVG_NORMAL)).icons
)


class MySiliconApp(SiliconApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        screen_geo = QDesktopWidget().screenGeometry()
        self.setMinimumSize(1024, 380)
        self.resize(1366, 916)
        self.move((screen_geo.width() - self.width()) // 2, (screen_geo.height() - self.height()) // 2)
        self.layerMain().setTitle("图片压缩工具")
        self.setWindowTitle("图片压缩工具")
        self.setWindowIcon(QIcon("./img/empty_icon.png"))

        # 第一个：图片压缩工具
        self.image_compressor_page = ImageCompressorPage(self)
        self.layerMain().addPage(self.image_compressor_page,
                                 icon=SiGlobal.siui.iconpack.get("ic_fluent_image_regular"),
                                 hint="图片压缩工具", side="top")
        
        # 第二个：日志查看器
        self.log_viewer_page = LogViewerPage(self)
        self.layerMain().addPage(self.log_viewer_page,
                                 icon=SiGlobal.siui.iconpack.get("ic_fluent_text_regular"),
                                 hint="日志查看器", side="top")
        
        # 最底下：关于
        self.layerMain().addPage(About(self),
                                 icon=SiGlobal.siui.iconpack.get("ic_fluent_info_filled"),
                                 hint="关于", side="bottom")
        
        # 将日志查看器页面传递给图片压缩工具页面，以便输出日志
        self.image_compressor_page.set_log_viewer(self.log_viewer_page)

        self.layerMain().setPage(0)

        SiGlobal.siui.reloadAllWindowsStyleSheet()
