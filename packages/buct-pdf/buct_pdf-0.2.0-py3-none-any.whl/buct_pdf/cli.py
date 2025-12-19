"""命令行接口模块"""

import argparse
import sys
from .core import GetsPdf, LoginError, NetworkError


def main():
    """命令行主程序"""
    parser = argparse.ArgumentParser(description="北化在线PDF下载工具")
    parser.add_argument("--username", help="学号")
    parser.add_argument("--password", help="密码")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互式模式")
    
    args = parser.parse_args()
    
    # 如果没有提供任何参数，进入交互式模式
    if not args.username or not args.password or args.interactive:
        client()
        return
    
    # 非交互式模式 - 仅登录并保持session
    client = GetsPdf()
    try:
        client.login(args.username, args.password)
        print("登录成功！")
        print("使用 Ctrl+C 退出")
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n正在退出...")
    except (LoginError, NetworkError) as e:
        print(f"错误: {str(e)}")
        sys.exit(1)
    finally:
        client.logout()


def client():
    """交互式客户端"""
    client = GetsPdf()
    print("=== 北化在线PDF下载工具 ===")
    
    try:
        username = input("请输入学号: ")
        password = input("请输入密码: ")
        
        client.login(username, password)
        print("登录成功！")

        while True:
            print("\n请选择操作:")
            print("1. 下载PPT(转PDF)")
            print("2. 下载PDF")
            print("3. 退出")

            choice = input("请输入选项 (1/2/3): ")

            if choice == "1":
                url = input("请输入页面uri：")
                output_dir = input("请输入输出目录（回车使用当前目录）：") or "."
                try:
                    pdf_path = client.download_ppt_to_pdf(url, output_dir)
                    print(f"下载完成：{pdf_path}")
                except Exception as e:
                    print(f"下载失败: {str(e)}")
            elif choice == "2":
                url = input("请输入页面uri：")
                output_dir = input("请输入输出目录（回车使用当前目录）：") or "."
                try:
                    pdf_path = client.download_pdf(url, output_dir)
                    print(f"下载完成：{pdf_path}")
                except Exception as e:
                    print(f"下载失败: {str(e)}")
            elif choice == "3":
                print("正在退出...")
                break
            else:
                print("输入错误，请重新选择")

    except (LoginError, NetworkError) as e:
        print(f"错误: {str(e)}")
    except KeyboardInterrupt:
        print("\n用户中断操作")
    finally:
        client.logout()


if __name__ == "__main__":
    main()