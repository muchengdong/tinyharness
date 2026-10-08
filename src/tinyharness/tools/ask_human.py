# tinyharness/tools/ask_human.py
from pydantic import BaseModel, Field

from tinyharness.tools import register_tool
from tinyharness.utils.rich_console import console


class AskHumanArgs(BaseModel):
    question: str = Field(description="AI在遇到障碍时会向人类提问。")


@register_tool
def ask_human(args: AskHumanArgs) -> str:
    """
    当你在执行任务中遇到不确定的关键问题、缺少环境信息、或者要执行高危覆盖操作需要审批时调用此工具向人类提问。
    调用后，终端会卡住等待用户输入，你会直接拿到人类用户的回答作为该工具的返回值。
    """
    console.print(f"\n❓ [AI 遇到障碍向您求助]: {args.question}")

    # 阻断当前线程，交出终端控制权给键盘
    input_tips = "👉 您的回答 (输入 'Y' 允许 / 'N' 拒绝 / 或输入具体文本): "
    user_response = input(input_tips).strip()
    if not user_response:
        return "[提示]: 用户没有进行任何输入，请自行做保守决策。"

    return f"[人类用户的真实反馈]: {user_response}"
