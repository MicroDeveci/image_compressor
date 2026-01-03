"""
GUI界面模块 - Windows 11 Fluent UI风格
"""
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# Windows高DPI支持
if sys.platform == "win32":
    try:
        # 尝试设置DPI感知
        from ctypes import windll, byref, c_int
        # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
        windll.shcore.SetProcessDpiAwareness(2)
    except:
        try:
            # 降级到旧版API
            windll.user32.SetProcessDPIAware()
        except:
            pass

from compressors import compress_image_fixed_quality, compress_image_to_size
from file_utils import get_image_files, get_output_path, format_size


class FluentStyle:
    """Fluent UI样式定义"""
    # 颜色主题（Windows 11浅色模式）
    BACKGROUND = "#FFFFFF"  # 白色背景
    SURFACE = "#F3F3F3"     # 表面颜色
    ACCENT = "#0078D4"      # 微软蓝（主要强调色）
    ACCENT_HOVER = "#106EBE"
    ACCENT_PRESSED = "#005A9E"
    TEXT_PRIMARY = "#000000"  # 主要文本
    TEXT_SECONDARY = "#6B6B6B"  # 次要文本
    BORDER = "#E1E1E1"  # 边框
    CONTROL = "#FFFFFF"  # 控件背景
    CONTROL_HOVER = "#F5F5F5"
    
    # 字体（使用Windows 11默认字体）
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_LARGE = 24  # 标题
    FONT_SIZE_MEDIUM = 12  # 正文
    FONT_SIZE_SMALL = 11  # 辅助文本


class ImageCompressorGUI:
    """图片压缩工具GUI主类 - Fluent UI风格"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("图片压缩工具")
        self.root.geometry("750x700")
        self.root.resizable(True, True)
        
        # 设置背景色
        self.root.configure(bg=FluentStyle.BACKGROUND)
        
        # 配置ttk样式
        self.setup_styles()
        
        # 变量
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.compression_mode = tk.StringVar(value="quality")
        self.quality_value = tk.IntVar(value=85)
        self.target_size_mb = tk.DoubleVar(value=20.0)
        self.is_processing = False
        
        # 创建界面
        self.create_widgets()
        
        # 居中窗口
        self.center_window()
    
    def setup_styles(self):
        """设置Fluent UI样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        fs = FluentStyle
        
        # 配置基础样式
        style.configure("TFrame", background=fs.BACKGROUND)
        style.configure("TLabel", background=fs.BACKGROUND, foreground=fs.TEXT_PRIMARY, 
                       font=(fs.FONT_FAMILY, fs.FONT_SIZE_MEDIUM))
        style.configure("TEntry", fieldbackground=fs.CONTROL, borderwidth=1, 
                       relief="solid", padding=8)
        style.map("TEntry", 
                 fieldbackground=[("focus", fs.CONTROL)],
                 bordercolor=[("focus", fs.ACCENT)])
        
        # 标题样式
        style.configure("Title.TLabel", font=(fs.FONT_FAMILY, fs.FONT_SIZE_LARGE, "normal"),
                       background=fs.BACKGROUND, foreground=fs.TEXT_PRIMARY)
        
        # 次要文本样式
        style.configure("Secondary.TLabel", foreground=fs.TEXT_SECONDARY,
                       font=(fs.FONT_FAMILY, fs.FONT_SIZE_SMALL))
        
        # 按钮样式
        style.configure("TButton", padding=(20, 10), borderwidth=0, 
                       font=(fs.FONT_FAMILY, fs.FONT_SIZE_MEDIUM))
        style.map("TButton",
                 background=[("active", fs.CONTROL_HOVER), ("!active", fs.CONTROL)],
                 foreground=[("active", fs.TEXT_PRIMARY), ("!active", fs.TEXT_PRIMARY)])
        
        # 主要按钮样式（Accent Button）
        style.configure("Accent.TButton", background=fs.ACCENT, foreground="white",
                       padding=(24, 12), font=(fs.FONT_FAMILY, fs.FONT_SIZE_MEDIUM, "normal"))
        style.map("Accent.TButton",
                 background=[("active", fs.ACCENT_HOVER), 
                           ("pressed", fs.ACCENT_PRESSED),
                           ("!active", fs.ACCENT)],
                 foreground=[("active", "white"), ("!active", "white")],
                 relief=[("pressed", "sunken"), ("!pressed", "flat")])
        
        # LabelFrame样式
        style.configure("TLabelframe", background=fs.SURFACE, borderwidth=1,
                       relief="solid", bordercolor=fs.BORDER)
        style.configure("TLabelframe.Label", background=fs.SURFACE,
                       foreground=fs.TEXT_PRIMARY, font=(fs.FONT_FAMILY, fs.FONT_SIZE_MEDIUM, "normal"))
        
        # Radiobutton样式
        style.configure("TRadiobutton", background=fs.SURFACE, foreground=fs.TEXT_PRIMARY,
                       font=(fs.FONT_FAMILY, fs.FONT_SIZE_MEDIUM))
        style.map("TRadiobutton",
                 background=[("selected", fs.SURFACE), ("!selected", fs.SURFACE)],
                 foreground=[("selected", fs.TEXT_PRIMARY), ("!selected", fs.TEXT_PRIMARY)])
        
        # Spinbox样式
        style.configure("TSpinbox", fieldbackground=fs.CONTROL, borderwidth=1,
                       relief="solid", padding=6, arrowcolor=fs.TEXT_SECONDARY)
        style.map("TSpinbox",
                 fieldbackground=[("focus", fs.CONTROL)],
                 bordercolor=[("focus", fs.ACCENT)],
                 arrowcolor=[("active", fs.ACCENT)])
        
        # Progressbar样式
        style.configure("TProgressbar", background=fs.ACCENT, borderwidth=0,
                       troughcolor=fs.SURFACE, thickness=6)
        
        # Scrollbar样式
        style.configure("TScrollbar", background=fs.SURFACE, borderwidth=0,
                       arrowcolor=fs.TEXT_SECONDARY, troughcolor=fs.BACKGROUND)
        style.map("TScrollbar",
                 background=[("active", fs.BORDER)],
                 arrowcolor=[("active", fs.ACCENT)])
    
    def center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """创建界面组件"""
        fs = FluentStyle
        
        # 主容器
        main_frame = ttk.Frame(self.root, padding="24")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="图片压缩工具", 
            style="Title.TLabel"
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 8))
        
        # 副标题
        subtitle_label = ttk.Label(
            main_frame,
            text="快速压缩图片，支持固定质量和目标大小两种模式",
            style="Secondary.TLabel"
        )
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 24))
        
        # 输入路径选择
        row = 2
        input_label = ttk.Label(main_frame, text="输入路径", font=(fs.FONT_FAMILY, fs.FONT_SIZE_MEDIUM))
        input_label.grid(row=row, column=0, sticky=tk.W, pady=(0, 6))
        
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=row+1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 16))
        input_frame.columnconfigure(0, weight=1)
        
        input_entry = ttk.Entry(input_frame, textvariable=self.input_path, font=(fs.FONT_FAMILY, fs.FONT_SIZE_MEDIUM))
        input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 8))
        
        input_button = ttk.Button(input_frame, text="浏览", command=self.browse_input, width=12)
        input_button.grid(row=0, column=1)
        
        # 输出路径选择
        row += 3
        output_label = ttk.Label(main_frame, text="输出目录", font=(fs.FONT_FAMILY, fs.FONT_SIZE_MEDIUM))
        output_label.grid(row=row, column=0, sticky=tk.W, pady=(0, 6))
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=row+1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 24))
        output_frame.columnconfigure(0, weight=1)
        
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path, font=(fs.FONT_FAMILY, fs.FONT_SIZE_MEDIUM))
        output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 8))
        
        output_button = ttk.Button(output_frame, text="浏览", command=self.browse_output, width=12)
        output_button.grid(row=0, column=1)
        
        # 压缩模式选择
        row += 3
        mode_frame = ttk.LabelFrame(main_frame, text="压缩模式", padding="16")
        mode_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 16))
        mode_frame.columnconfigure(0, weight=1)
        
        # 固定质量模式
        quality_radio = ttk.Radiobutton(
            mode_frame, 
            text="固定质量压缩（推荐，速度快）", 
            variable=self.compression_mode, 
            value="quality",
            command=self.on_mode_change
        )
        quality_radio.grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        
        quality_frame = ttk.Frame(mode_frame)
        quality_frame.grid(row=1, column=0, sticky=tk.W, padx=(32, 0), pady=(0, 16))
        
        ttk.Label(quality_frame, text="JPEG质量:", font=(fs.FONT_FAMILY, fs.FONT_SIZE_MEDIUM)).pack(side=tk.LEFT, padx=(0, 8))
        quality_spinbox = ttk.Spinbox(
            quality_frame, 
            from_=1, 
            to=100, 
            textvariable=self.quality_value, 
            width=8,
            font=(fs.FONT_FAMILY, fs.FONT_SIZE_MEDIUM)
        )
        quality_spinbox.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(quality_frame, text="(1-100，推荐60-85)", style="Secondary.TLabel").pack(side=tk.LEFT)
        
        # 目标大小模式
        size_radio = ttk.Radiobutton(
            mode_frame, 
            text="目标大小压缩（压缩到指定总大小）", 
            variable=self.compression_mode, 
            value="size",
            command=self.on_mode_change
        )
        size_radio.grid(row=2, column=0, sticky=tk.W, pady=(0, 8))
        
        size_frame = ttk.Frame(mode_frame)
        size_frame.grid(row=3, column=0, sticky=tk.W, padx=(32, 0))
        
        ttk.Label(size_frame, text="目标总大小:", font=(fs.FONT_FAMILY, fs.FONT_SIZE_MEDIUM)).pack(side=tk.LEFT, padx=(0, 8))
        size_spinbox = ttk.Spinbox(
            size_frame, 
            from_=0.1, 
            to=1000, 
            textvariable=self.target_size_mb, 
            width=8,
            increment=1.0,
            font=(fs.FONT_FAMILY, fs.FONT_SIZE_MEDIUM)
        )
        size_spinbox.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(size_frame, text="MB", font=(fs.FONT_FAMILY, fs.FONT_SIZE_MEDIUM)).pack(side=tk.LEFT)
        
        # 开始按钮
        row += 2
        self.start_button = ttk.Button(
            main_frame, 
            text="开始压缩", 
            command=self.start_compression,
            style="Accent.TButton"
        )
        self.start_button.grid(row=row, column=0, columnspan=3, pady=(0, 16))
        
        # 进度条
        row += 1
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, 
            variable=self.progress_var, 
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 8))
        
        self.progress_label = ttk.Label(main_frame, text="", style="Secondary.TLabel")
        self.progress_label.grid(row=row+1, column=0, columnspan=3, pady=(0, 16))
        
        # 日志输出区域
        row += 3
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding="12")
        log_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(row, weight=1)
        
        # 配置日志文本框样式
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=12, 
            wrap=tk.WORD,
            font=(FluentStyle.FONT_FAMILY, 10),
            bg=FluentStyle.CONTROL,
            fg=FluentStyle.TEXT_PRIMARY,
            borderwidth=1,
            relief="solid",
            padx=12,
            pady=12,
            insertbackground=FluentStyle.ACCENT
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 初始化模式
        self.on_mode_change()
    
    def on_mode_change(self):
        """压缩模式改变时的回调"""
        pass
    
    def browse_input(self):
        """浏览输入路径"""
        path = filedialog.askdirectory(title="选择输入文件夹")
        if not path:
            path = filedialog.askopenfilename(
                title="选择输入图片",
                filetypes=[
                    ("图片文件", "*.jpg *.jpeg *.png *.bmp *.webp"),
                    ("所有文件", "*.*")
                ]
            )
        if path:
            self.input_path.set(path)
            if not self.output_path.get():
                if os.path.isfile(path):
                    self.output_path.set(os.path.join(os.path.dirname(path), "compressed"))
                else:
                    self.output_path.set(os.path.join(path, "compressed"))
    
    def browse_output(self):
        """浏览输出路径"""
        path = filedialog.askdirectory(title="选择输出文件夹")
        if path:
            self.output_path.set(path)
    
    def log(self, message):
        """添加日志"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_compression(self):
        """开始压缩"""
        if self.is_processing:
            messagebox.showwarning("警告", "正在处理中，请等待...")
            return
        
        input_path = self.input_path.get().strip()
        if not input_path or not os.path.exists(input_path):
            messagebox.showerror("错误", "请输入有效的输入路径！")
            return
        
        output_path = self.output_path.get().strip()
        if not output_path:
            messagebox.showerror("错误", "请输入输出目录！")
            return
        
        thread = threading.Thread(target=self.process_images, daemon=True)
        thread.start()
    
    def process_images(self):
        """处理图片（在后台线程中执行）"""
        self.is_processing = True
        self.start_button.config(state="disabled")
        self.log_text.delete(1.0, tk.END)
        
        try:
            input_path = self.input_path.get().strip()
            output_dir = self.output_path.get().strip()
            os.makedirs(output_dir, exist_ok=True)
            
            self.log("正在扫描图片文件...")
            image_files = get_image_files(input_path)
            
            if not image_files:
                self.log("❌ 未找到任何图片文件！")
                messagebox.showwarning("警告", "未找到任何图片文件！")
                return
            
            total_files = len(image_files)
            self.log(f"找到 {total_files} 张图片\n")
            
            total_size = 0
            success_count = 0
            fail_count = 0
            mode = self.compression_mode.get()
            
            if mode == "quality":
                quality = self.quality_value.get()
                self.log(f"开始压缩（质量: {quality}）...\n")
                
                for idx, (root, file) in enumerate(image_files, 1):
                    input_file_path = os.path.join(root, file)
                    output_file_path = get_output_path(input_file_path, input_path, output_dir)
                    
                    try:
                        if compress_image_fixed_quality(input_file_path, output_file_path, quality):
                            size = os.path.getsize(output_file_path)
                            total_size += size
                            success_count += 1
                            self.log(f"✔ [{idx}/{total_files}] {file} → {format_size(size)}")
                        else:
                            fail_count += 1
                            self.log(f"✖ [{idx}/{total_files}] {file} 压缩失败")
                    except Exception as e:
                        fail_count += 1
                        self.log(f"✖ [{idx}/{total_files}] {file} 压缩失败: {str(e)}")
                    
                    progress = (idx / total_files) * 100
                    self.progress_var.set(progress)
                    self.progress_label.config(text=f"处理中: {idx}/{total_files}")
                    self.root.update_idletasks()
            
            else:  # size mode
                total_max_size = int(self.target_size_mb.get() * 1024 * 1024)
                target_size_per_image = total_max_size // total_files
                
                self.log(f"目标总大小: {format_size(total_max_size)}")
                self.log(f"平均每张目标大小: {format_size(target_size_per_image)}\n")
                
                for idx, (root, file) in enumerate(image_files, 1):
                    input_file_path = os.path.join(root, file)
                    output_file_path = get_output_path(input_file_path, input_path, output_dir)
                    
                    try:
                        if compress_image_to_size(input_file_path, output_file_path, target_size_per_image):
                            size = os.path.getsize(output_file_path)
                            total_size += size
                            success_count += 1
                            self.log(f"✔ [{idx}/{total_files}] {file} → {format_size(size)} (累计: {format_size(total_size)})")
                        else:
                            fail_count += 1
                            self.log(f"✖ [{idx}/{total_files}] {file} 压缩失败")
                    except Exception as e:
                        fail_count += 1
                        self.log(f"✖ [{idx}/{total_files}] {file} 压缩失败: {str(e)}")
                    
                    progress = (idx / total_files) * 100
                    self.progress_var.set(progress)
                    self.progress_label.config(text=f"处理中: {idx}/{total_files}")
                    self.root.update_idletasks()
            
            self.log("\n" + "="*50)
            self.log("=== 处理完成 ===")
            self.log(f"成功: {success_count} 张")
            if fail_count > 0:
                self.log(f"失败: {fail_count} 张")
            self.log(f"总大小: {format_size(total_size)}")
            self.log(f"输出目录: {output_dir}")
            
            if mode == "size":
                if total_size <= total_max_size:
                    self.log("✓ 已达到目标大小要求")
                else:
                    overflow = total_size - total_max_size
                    self.log(f"⚠ 超出目标大小 {format_size(overflow)}")
            
            self.progress_label.config(text=f"完成: {success_count}/{total_files}")
            messagebox.showinfo("完成", f"压缩完成！\n成功: {success_count} 张\n失败: {fail_count} 张")
        
        except Exception as e:
            self.log(f"\n❌ 发生错误: {str(e)}")
            messagebox.showerror("错误", f"发生错误: {str(e)}")
        
        finally:
            self.is_processing = False
            self.start_button.config(state="normal")


def main():
    """启动GUI"""
    root = tk.Tk()
    app = ImageCompressorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
