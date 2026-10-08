# tinyharness/tools/write_file.py
from pydantic import BaseModel, Field

from tinyharness.tools import register_tool


class WriteFileArgs(BaseModel):
    file_path: str = Field(description="要写入的文件路径。")
    content: str = Field(description="要写入文件的内容。")


@register_tool
def write_file(params: WriteFileArgs):
    """在本地工作区新建文件或完全覆写已存在的文件。"""
    try:
        print(f"\n💾 [Harness 安全拦截] AI 申请写入文件: {params.file_path}")
        confirm = input("👉 主人，您批准这次文件写入吗？(Y/N): ")
        if confirm.upper() != "Y":
            return "[Rejected] 用户拒绝了该写入操作。"

        with open(params.file_path, "w", encoding="utf-8") as f:
            f.write(params.content)

        return f"[Success] 文件 '{params.file_path}' 已成功写入。"
    except Exception as e:
        return f"[Error] 写入失败: {str(e)}"
