"""
文件处理工具模块
"""
import os


def get_image_files(path):
    """
    获取图片文件列表
    
    Args:
        path: 文件或文件夹路径
    
    Returns:
        list: [(root, filename), ...] 格式的图片文件列表
    """
    image_files = []
    supported_formats = (".jpg", ".jpeg", ".png", ".bmp", ".webp")
    
    if os.path.isfile(path):
        # 单张图片
        if path.lower().endswith(supported_formats):
            image_files.append((os.path.dirname(path), os.path.basename(path)))
    elif os.path.isdir(path):
        # 文件夹
        for root, _, files in os.walk(path):
            for file in files:
                if file.lower().endswith(supported_formats):
                    file_path = os.path.join(root, file)
                    # 跳过输出目录
                    if "compressed" in file_path:
                        try:
                            common_path = os.path.commonpath([path, file_path])
                            if common_path == path:
                                continue
                        except ValueError:
                            pass
                    image_files.append((root, file))
    
    return image_files


def get_output_path(input_path, input_base_path, output_dir):
    """
    根据输入路径生成输出路径，保持相对路径结构
    
    Args:
        input_path: 输入文件的完整路径
        input_base_path: 输入的基准路径（文件夹或单文件）
        output_dir: 输出目录
    
    Returns:
        str: 输出文件路径
    """
    if os.path.isfile(input_base_path):
        # 如果输入是单文件，直接输出到输出目录
        filename = os.path.basename(input_path)
        return os.path.join(output_dir, filename)
    else:
        # 如果输入是文件夹，保持相对路径结构
        rel_path = os.path.relpath(os.path.dirname(input_path), input_base_path)
        filename = os.path.basename(input_path)
        
        if rel_path == ".":
            output_path = os.path.join(output_dir, filename)
        else:
            output_subdir = os.path.join(output_dir, rel_path)
            os.makedirs(output_subdir, exist_ok=True)
            output_path = os.path.join(output_subdir, filename)
        
        return output_path


def format_size(size_bytes):
    """
    格式化文件大小
    
    Args:
        size_bytes: 字节数
    
    Returns:
        str: 格式化后的大小字符串
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / 1024 / 1024:.2f} MB"

