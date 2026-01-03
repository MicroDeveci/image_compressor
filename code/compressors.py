"""
图片压缩核心功能模块
"""
import os
from PIL import Image


def compress_image_fixed_quality(input_path, output_path, quality):
    """
    使用固定质量压缩图片
    
    Args:
        input_path: 输入图片路径
        output_path: 输出图片路径
        quality: JPEG质量 (1-100)
    
    Returns:
        bool: 是否成功
    """
    try:
        img = Image.open(input_path)
        
        # 统一转 RGB，避免 PNG / RGBA 报错
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        img.save(
            output_path,
            format="JPEG",
            quality=quality,
            optimize=True
        )
        return True
    except Exception:
        return False


def compress_image_to_size(input_path, output_path, target_size):
    """
    压缩单张图片到目标大小
    
    Args:
        input_path: 输入图片路径
        output_path: 输出图片路径
        target_size: 目标大小（字节）
    
    Returns:
        bool: 是否成功
    """
    try:
        img = Image.open(input_path)
        original_size = img.size

        # 统一转 RGB，避免 PNG / RGBA 报错
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # 质量压缩（从较低质量开始，更激进）
        quality = 60
        min_quality = 15
        scale = 1.0
        
        while True:
            # 如果已经缩小过，需要重新打开原图
            if scale < 1.0:
                img = Image.open(input_path)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
                img = img.resize(new_size, Image.LANCZOS)
            
            # 尝试保存
            img.save(
                output_path,
                format="JPEG",
                quality=quality,
                optimize=True
            )
            
            current_size = os.path.getsize(output_path)
            
            if current_size <= target_size:
                break
            
            # 如果质量还可以继续降低
            if quality > min_quality:
                quality -= 5
            # 如果质量已经最低，开始缩小尺寸
            elif scale > 0.5:
                scale -= 0.1
                quality = 60  # 重置质量，从头开始
            else:
                # 已经压缩到极限
                break
        return True
    except Exception:
        return False

