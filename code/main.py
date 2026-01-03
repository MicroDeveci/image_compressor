"""
主程序入口
支持GUI和CLI两种模式
"""
import sys
import os


def main():
    """主函数"""
    # 检查是否有命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        # CLI模式
        from cli import main as cli_main
        cli_main()
    else:
        # GUI模式（默认）
        try:
            from gui import main as gui_main
            gui_main()
        except ImportError as e:
            print(f"GUI模式启动失败: {e}")
            print("尝试使用命令行模式: python main.py --cli")
            sys.exit(1)


if __name__ == "__main__":
    main()

