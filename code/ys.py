import os
from PIL import Image

def compress_image_fixed_quality(input_path, output_path, quality):
    """使用固定质量压缩图片"""
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

def compress_image_to_size(input_path, output_path, target_size):
    """压缩单张图片到目标大小"""
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

def get_image_files(path):
    """获取图片文件列表"""
    image_files = []
    
    if os.path.isfile(path):
        # 单张图片
        if path.lower().endswith((".jpg", ".jpeg", ".png")):
            image_files.append((os.path.dirname(path), os.path.basename(path)))
    elif os.path.isdir(path):
        # 文件夹
        for root, _, files in os.walk(path):
            for file in files:
                if file.lower().endswith((".jpg", ".jpeg", ".png")):
                    file_path = os.path.join(root, file)
                    # 跳过输出目录
                    if "compressed" in file_path and os.path.commonpath([path, file_path]) == path:
                        continue
                    image_files.append((root, file))
    
    return image_files

def main():
    print("=" * 50)
    print("图片压缩工具")
    print("=" * 50)
    print()
    
    # 1. 选择输入（文件夹或单张图片）
    while True:
        input_path = input("请输入图片路径（文件夹或单张图片）: ").strip().strip('"')
        if os.path.exists(input_path):
            break
        print("❌ 路径不存在，请重新输入！")
    
    # 2. 选择输出目录
    print()
    output_dir = input("请输入输出目录（直接回车使用默认: 输入目录/compressed）: ").strip().strip('"')
    if not output_dir:
        if os.path.isfile(input_path):
            output_dir = os.path.join(os.path.dirname(input_path), "compressed")
        else:
            output_dir = os.path.join(input_path, "compressed")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 3. 选择压缩模式
    print()
    print("请选择压缩模式：")
    print("1. 固定质量压缩（推荐，速度快）")
    print("2. 目标大小压缩（压缩到指定总大小）")
    while True:
        mode = input("请选择 (1 或 2): ").strip()
        if mode in ("1", "2"):
            break
        print("❌ 请输入 1 或 2！")
    
    quality = 85  # 默认质量
    if mode == "1":
        # 固定质量模式
        print()
        while True:
            try:
                quality_input = input("请输入JPEG质量 (1-100，推荐60-85，直接回车使用85): ").strip()
                if not quality_input:
                    quality = 85
                    break
                quality = int(quality_input)
                if 1 <= quality <= 100:
                    break
                print("❌ 质量值必须在 1-100 之间！")
            except ValueError:
                print("❌ 请输入有效的数字！")
    else:
        # 目标大小模式
        print()
        while True:
            try:
                size_input = input("请输入目标总大小（MB，直接回车使用20MB）: ").strip()
                if not size_input:
                    total_max_size = 20 * 1024 * 1024
                    break
                total_max_size_mb = float(size_input)
                if total_max_size_mb > 0:
                    total_max_size = int(total_max_size_mb * 1024 * 1024)
                    break
                print("❌ 大小必须大于 0！")
            except ValueError:
                print("❌ 请输入有效的数字！")
    
    # 获取图片文件列表
    print()
    print("正在扫描图片文件...")
    image_files = get_image_files(input_path)
    
    if not image_files:
        print("❌ 未找到任何图片文件！")
        return
    
    print(f"找到 {len(image_files)} 张图片")
    print()
    
    # 开始压缩
    total_size = 0
    success_count = 0
    fail_count = 0
    
    if mode == "1":
        # 固定质量模式
        print(f"开始压缩（质量: {quality}）...")
        print("-" * 50)
        for root, file in image_files:
            input_file_path = os.path.join(root, file)
            
            # 保持相对路径结构
            if os.path.isfile(input_path):
                output_path = os.path.join(output_dir, file)
            else:
                rel_path = os.path.relpath(root, input_path)
                if rel_path == ".":
                    output_path = os.path.join(output_dir, file)
                else:
                    output_subdir = os.path.join(output_dir, rel_path)
                    os.makedirs(output_subdir, exist_ok=True)
                    output_path = os.path.join(output_subdir, file)
            
            try:
                compress_image_fixed_quality(input_file_path, output_path, quality)
                size = os.path.getsize(output_path)
                total_size += size
                size_mb = size / 1024 / 1024
                success_count += 1
                print(f"✔ [{success_count}/{len(image_files)}] {file} → {size_mb:.2f}MB")
            except Exception as e:
                fail_count += 1
                print(f"✖ {file} 压缩失败: {e}")
    else:
        # 目标大小模式
        target_size_per_image = total_max_size // len(image_files)
        print(f"目标总大小: {total_max_size / 1024 / 1024:.2f}MB")
        print(f"平均每张目标大小: {target_size_per_image / 1024 / 1024:.2f}MB")
        print("-" * 50)
        
        for root, file in image_files:
            input_file_path = os.path.join(root, file)
            
            # 保持相对路径结构
            if os.path.isfile(input_path):
                output_path = os.path.join(output_dir, file)
            else:
                rel_path = os.path.relpath(root, input_path)
                if rel_path == ".":
                    output_path = os.path.join(output_dir, file)
                else:
                    output_subdir = os.path.join(output_dir, rel_path)
                    os.makedirs(output_subdir, exist_ok=True)
                    output_path = os.path.join(output_subdir, file)
            
            try:
                compress_image_to_size(input_file_path, output_path, target_size_per_image)
                size = os.path.getsize(output_path)
                total_size += size
                size_mb = size / 1024 / 1024
                success_count += 1
                print(f"✔ [{success_count}/{len(image_files)}] {file} → {size_mb:.2f}MB (累计: {total_size / 1024 / 1024:.2f}MB)")
            except Exception as e:
                fail_count += 1
                print(f"✖ {file} 压缩失败: {e}")
    
    # 输出结果
    print("-" * 50)
    print(f"\n=== 处理完成 ===")
    print(f"成功: {success_count} 张")
    if fail_count > 0:
        print(f"失败: {fail_count} 张")
    print(f"总大小: {total_size / 1024 / 1024:.2f}MB")
    print(f"输出目录: {output_dir}")
    
    if mode == "2":
        print(f"目标大小: {total_max_size / 1024 / 1024:.2f}MB")
        if total_size <= total_max_size:
            print("✓ 已达到目标大小要求")
        else:
            print(f"⚠ 超出目标大小 {((total_size - total_max_size) / 1024 / 1024):.2f}MB")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已取消")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        input("\n按回车键退出...")
