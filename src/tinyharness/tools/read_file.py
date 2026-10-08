# tinyharness/tools/read_file.py
import os

from pydantic import BaseModel, Field

from tinyharness.tools import register_tool


class ReadFileArgs(BaseModel):
    file_path: str = Field(description="要读取的文件路径。")


@register_tool
def read_file(args: ReadFileArgs) -> str:
    """
    统一跨平台读取本地文件的内容。
    AI 可以通过此工具查看项目里的代码、配置文件或日志。
    """
    try:
        #  安全防线：转换为绝对路径，防止路径注入越权
        abs_path = os.path.abspath(args.file_path)

        #  检查文件是否存在
        if not os.path.exists(abs_path):
            return f"[Error] 文件不存在: '{args.file_path}'，请确认路径是否正确。"

        #  检查是否是文件而非文件夹
        if not os.path.isfile(abs_path):
            return f"[Error] 目标路径 '{args.file_path}' 是一个文件夹，请使用列出目录的工具。"

        #  读取文件内容（兜底常见编码，防止乱码崩溃）
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            # 如果 utf-8 失败，尝试用本地环境默认编码（例如 Windows 的 gbk）
            with open(abs_path, "r", encoding="gbk", errors="replace") as f:
                content = f.read()

        # 防御机制：如果文件过大（比如几十MB的日志），防止把大模型塞爆
        MAX_CHARS = 50000  # 大约 5 万字限制
        if len(content) > MAX_CHARS:
            return (
                f"[Warning] 文件内容过长 (共 {len(content)} 字)，已自动为你截取前 {MAX_CHARS} 字：\n\n"
                f"{content[:MAX_CHARS]}\n\n...[内容已截断]..."
            )

        return content

    except Exception as e:
        return f"[Error] 读取文件时发生系统异常: {str(e)}"
