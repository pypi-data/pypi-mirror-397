import subprocess
import os
import sys
import shutil
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DrawIO-Automation")


def get_drawio_path() -> str:
    """获取 draw.io 可执行文件路径，支持多平台"""
    # 优先使用环境变量
    if env_path := os.environ.get("DRAWIO_PATH"):
        return env_path
    
    # 尝试从 PATH 中查找
    if path := shutil.which("drawio"):
        return path
    if path := shutil.which("draw.io"):
        return path
    
    # 平台特定的默认路径
    platform_paths = {
        "darwin": "/Applications/draw.io.app/Contents/MacOS/draw.io",
        "win32": r"C:\Program Files\draw.io\draw.io.exe",
        "linux": "/usr/bin/drawio",
    }
    
    if default_path := platform_paths.get(sys.platform):
        if os.path.exists(default_path):
            return default_path
    
    raise FileNotFoundError(
        "draw.io not found. Please install draw.io or set DRAWIO_PATH environment variable."
    )


@mcp.tool()
def create_diagram(xml_content: str, file_name: str, output_dir: str) -> str:
    """
    接收 Draw.io XML 内容，保存为图片，返回生成的图片路径。
    
    Args:
        xml_content: Draw.io XML 内容
        file_name: 文件名（不含扩展名或带 .drawio/.png 扩展名均可）
        output_dir: 输出目录路径
    
    Returns:
        生成的 PNG 图片绝对路径
    """
    try:
        drawio_path = get_drawio_path()
    except FileNotFoundError as e:
        return f"Error: {e}"
    
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    base_name = file_name.replace(".png", "").replace(".drawio", "")
    xml_file = os.path.join(output_dir, f"{base_name}.drawio")
    png_file = os.path.join(output_dir, f"{base_name}.png")

    # 1. 保存 XML 文件
    with open(xml_file, "w", encoding="utf-8") as f:
        f.write(xml_content)

    # 2. 调用 CLI 转换为 PNG (scale=4 保证清晰度)
    try:
        subprocess.run(
            [drawio_path, "-x", "-f", "png", "-s", "4", "-o", png_file, xml_file],
            check=True,
        )
    except Exception as e:
        return f"Error: {e}"

    return png_file


def main():
    """入口函数"""
    mcp.run()


if __name__ == "__main__":
    main()

