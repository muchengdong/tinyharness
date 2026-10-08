# tinyharness/tools/list_dir.py

import os

from pydantic import BaseModel, Field

from tinyharness.tools import register_tool


class ListDirArgs(BaseModel):
    folder_path: str = Field(default=".", description="文件夹路径，默认为当前目录。")


@register_tool
def list_dir(args: ListDirArgs):
    """列出指定目录下的所有文件和文件夹列表。纯本地操作，绝对安全。"""
    try:
        files = os.listdir(args.folder_path)
        return "[Local Files]:\n" + "\n".join(files) if files else "[Info] 目录为空。"
    except Exception as e:
        return f"[Error] 无法读取目录: {str(e)}"
