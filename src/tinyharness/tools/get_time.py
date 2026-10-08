# tinyharness/tools/get_time.py
from datetime import datetime

from pydantic import BaseModel

from tinyharness.tools import register_tool


class GetCurrentTimeArgs(BaseModel): ...


@register_tool
def get_current_time(args: GetCurrentTimeArgs):
    """获取本地系统当前的精确时间。"""
    return datetime.now().strftime(r"%Y-%m-%d %H:%M:%S")
