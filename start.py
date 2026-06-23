"""
myrag 快速启动脚本
"""
import subprocess
import sys
from pathlib import Path


def check_env():
    """检查环境"""
    print("=" * 60)
    print("myrag - 个人知识库系统")
    print("=" * 60)
    
    # 检查 .env 文件
    env_path = Path(".env")
    if not env_path.exists():
        print("\n⚠️  未找到 .env 文件")
        print("正在从 .env.example 复制...")
        env_example = Path(".env.example")
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_path)
            print("✅ 已创建 .env 文件")
            print("请编辑 .env 文件，填入您的 DASHSCOPE_API_KEY")
            print("\n获取 API Key: https://dashscope.console.aliyun.com/")
            return False
    
    # 检查 API Key
    with env_path.open("r", encoding="utf-8") as f:
        content = f.read()
        if "your_api_key_here" in content:
            print("\n⚠️  请编辑 .env 文件，填入您的 DASHSCOPE_API_KEY")
            return False
    
    return True


def create_data_dirs():
    """创建数据目录"""
    from pyprojroot import here
    root = here()
    
    dirs = [
        "data/stock_data/pdf_reports",
        "data/stock_data/debug_data/01_parsed_reports",
        "data/stock_data/debug_data/02_merged_reports",
        "data/stock_data/debug_data/03_reports_markdown",
        "data/stock_data/databases/chunked_reports",
        "data/stock_data/databases/vector_dbs",
    ]
    
    for d in dirs:
        dir_path = root / d
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("\n✅ 数据目录已创建")


def main():
    """主函数"""
    # 检查环境
    if not check_env():
        print("\n按回车键退出...")
        input()
        return
    
    # 创建目录
    create_data_dirs()
    
    print("\n🚀 启动 Streamlit 前端...")
    print("=" * 60)
    print("\n提示：如果看到邮箱输入提示，请直接按 Enter 键跳过！")
    print("\n启动中，请稍候...\n")
    
    try:
        # 添加 --server.headless true 来跳过交互提示
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "app/streamlit_app.py",
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 再见！")


if __name__ == "__main__":
    main()
