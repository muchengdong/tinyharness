import sys
import os
import json
from openai import OpenAI
from tinyharness.tools import openai_tools_schema, available_tools, _tool_models
from tinyharness.env import env
from rich.console import Console

console = Console()

def main():
    api_key = env.llm_api_key
    base_url = env.llm_base_url
    model_id = env.llm_model_id
    client = OpenAI(api_key=api_key, base_url=base_url)

    console.print("==========================================================")
    console.print("   👑 TinyHarness 常驻会话终端版 | 启动成功                ")
    console.print("   👉 提示：输入 'exit' 或 'quit' 退出会话；按 Ctrl+C 强退 ")
    console.print("==========================================================")

    # 💡 【极其重要】：把全局记忆（对话历史）提到无限循环的外面！
    messages = [
        {
            "role": "system",
            "content": "你是一个运行在本地终端里的独立智能体。你必须且只能通过调用工具操作本地文件，绝对不允许写任何底层的 shell 命令。",
        }
    ]

    while True:
        try:
            # 1. 持续阻塞等待用户输入下一个任务
            user_goal = input("\n🧑 主人，请下达下一个任务 > ").strip()

            if not user_goal:
                continue

            # 输入 exit 优雅退出
            if user_goal.lower() in ["exit", "quit"]:
                console.print("👋 收到退出指令，正在关闭 TinyHarness 帝国。再见！")
                break

            # 2. 将新任务拼接到拥有持久记忆的 messages 列表中
            messages.append({"role": "user", "content": user_goal})
            console.print("🚀 开始执行当前任务...")

            # 3. 智能体思考与工具拦截的内部循环
            loop_count = 0
            max_loops = 5
            task_completed = False

            while loop_count < max_loops and not task_completed:
                loop_count += 1

                # 呼叫大模型，由于开启了 stream=True，response 是一个流式生成器
                response = client.chat.completions.create(
                    model=model_id,
                    messages=messages,
                    tools=openai_tools_schema,
                    tool_choice="auto",
                    temperature=0,
                    stream=True,  # 开启打字机效果
                )

                # 🆕 准备在内存中还原和拼接流式切碎的文本与工具参数
                response_text = ""
                tool_calls_chunks = {}

                # 🆕 遍历流式区块 (Chunks)
                for chunk in response:
                    if not chunk.choices:
                        continue
                    delta = chunk.choices[0].delta

                    # 1. 拼接并实时打印普通的文本回复（打字机效果）
                    if delta.content:
                        console.print(delta.content, end="")
                        response_text += delta.content

                    # 2. 收集并拼接流式吐出的工具调用参数碎片
                    if delta.tool_calls:
                        for tool_call in delta.tool_calls:
                            idx = tool_call.index
                            if idx not in tool_calls_chunks:
                                tool_calls_chunks[idx] = tool_call
                            else:
                                # 核心：将不断吐出来的 arguments 字符串拼接起来
                                tool_calls_chunks[idx].function.arguments += (
                                    tool_call.function.arguments
                                )

                # 🆕 将拼接完整的消息还原为一个模拟的 assistant message 对象
                simulated_message = {
                    "role": "assistant",
                    "content": response_text if response_text else None,
                    "tool_calls": (
                        [v for v in tool_calls_chunks.values()]
                        if tool_calls_chunks
                        else None
                    ),
                }

                # 塞进历史记录，维持多轮会话
                messages.append(simulated_message)
                tool_calls = simulated_message["tool_calls"]

                # 情况 A：AI 觉得当前任务办完了，不需要调工具了
                if not tool_calls:
                    console.print()  # 在打字机效果结束后打印一个换行美化
                    task_completed = True  # 标记当前输入任务完成，跳出内部循环
                    break

                # 情况 B：闭环分发工具执行
                for tool_call in tool_calls:
                    function_name = tool_call.function.name

                    console.print(f"\n⚙️  [Harness 自动分发组件]: 执行 {function_name}...")

                    if function_name in available_tools:
                        try:
                            # 🎯 核心修复：拿到对应的 Pydantic 模型类，利用 arguments 字符串直接实例化对象
                            args_model = _tool_models[function_name]
                            validated_args_obj = args_model.model_validate_json(tool_call.function.arguments)

                            # 🎯 严格遵循铁律规则：不使用 ** 字典解包，直接传入整个模型实例对象
                            tool_result = available_tools[function_name](validated_args_obj)
                        except Exception as e:
                            tool_result = f"[Error] 工具执行或参数验证失败: {str(e)}"

                        messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content": str(tool_result),  # 强转为纯字符串，防止 API 报错
                            }
                        )
                    else:
                        messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content": "[Error] 未找到该注册工具。",
                            }
                        )

            if loop_count >= max_loops and not task_completed:
                console.print(
                    "\n⚠️ [TinyHarness] 达到单次任务安全循环上限，已中止本轮思考。"
                )

        except KeyboardInterrupt:
            # 优雅处理用户在终端按下 Ctrl + C 强退的场景
            console.print(
                "\n👋 检测到强退信号 (Ctrl+C)，TinyHarness 已安全退出会话。"
            )
            break


if __name__ == "__main__":
    main()
