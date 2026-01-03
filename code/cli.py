"""
命令行界面模块
"""
import os
from compressors import compress_image_fixed_quality, compress_image_to_size
from file_utils import get_image_files, get_output_path, format_size


def main():
    """命令行主函数"""
    print("=" * 50)
    print("图片压缩工具 (CLI模式)")
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
            output_file_path = get_output_path(input_file_path, input_path, output_dir)
            
            try:
                if compress_image_fixed_quality(input_file_path, output_file_path, quality):
                    size = os.path.getsize(output_file_path)
                    total_size += size
                    success_count += 1
                    print(f"✔ [{success_count}/{len(image_files)}] {file} → {format_size(size)}")
                else:
                    fail_count += 1
                    print(f"✖ {file} 压缩失败")
            except Exception as e:
                fail_count += 1
                print(f"✖ {file} 压缩失败: {e}")
    else:
        # 目标大小模式
        target_size_per_image = total_max_size // len(image_files)
        print(f"目标总大小: {format_size(total_max_size)}")
        print(f"平均每张目标大小: {format_size(target_size_per_image)}")
        print("-" * 50)
        
        for root, file in image_files:
            input_file_path = os.path.join(root, file)
            output_file_path = get_output_path(input_file_path, input_path, output_dir)
            
            try:
                if compress_image_to_size(input_file_path, output_file_path, target_size_per_image):
                    size = os.path.getsize(output_file_path)
                    total_size += size
                    success_count += 1
                    print(f"✔ [{success_count}/{len(image_files)}] {file} → {format_size(size)} (累计: {format_size(total_size)})")
                else:
                    fail_count += 1
                    print(f"✖ {file} 压缩失败")
            except Exception as e:
                fail_count += 1
                print(f"✖ {file} 压缩失败: {e}")
    
    # 输出结果
    print("-" * 50)
    print(f"\n=== 处理完成 ===")
    print(f"成功: {success_count} 张")
    if fail_count > 0:
        print(f"失败: {fail_count} 张")
    print(f"总大小: {format_size(total_size)}")
    print(f"输出目录: {output_dir}")
    
    if mode == "2":
        if total_size <= total_max_size:
            print("✓ 已达到目标大小要求")
        else:
            overflow = total_size - total_max_size
            print(f"⚠ 超出目标大小 {format_size(overflow)}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已取消")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        input("\n按回车键退出...")

