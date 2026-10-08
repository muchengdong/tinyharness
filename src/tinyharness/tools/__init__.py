# tinyharness/tools/__init__.py
import os
import inspect
import importlib
from typing import Callable, Dict, Type
from openai import pydantic_function_tool
from pydantic import BaseModel

# 全局注册中心：供 cli.py 直接调用
openai_tools_schema = []
available_tools = {}
_tool_models: Dict[str, Type[BaseModel]] = {}


def register_tool(func: Callable) -> Callable:
    """
    【极致纯粹的工具注册装饰器】
    要求：被装饰的函数必须有且仅有一个继承自 BaseModel 的参数。
    """
    name = func.__name__
    doc = func.__doc__ or f"执行 {name} 操作"
    
    # 直接获取函数的第一个参数的类型注解（即 Pydantic 模型类）
    sig = inspect.signature(func)
    params = list(sig.parameters.values())
    
    if not params or not issubclass(params[0].annotation, BaseModel):
        raise TypeError(f"函数 {name} 必须声明一个 Pydantic BaseModel 作为首个参数")
        
    model_class = params[0].annotation

    # 生成标准的 OpenAI Schema
    tool_schema = pydantic_function_tool(
        name=name,
        description=doc.strip(),
        model=model_class
    )
    
    # 注册工具链
    openai_tools_schema.append(tool_schema)
    available_tools[name] = func
    _tool_models[name] = model_class
    
    return func



def autodiscover_tools():
    """工具链自动发现
    """
    openai_tools_schema.clear()
    available_tools.clear()

    current_dir = os.path.dirname(__file__)
    for filename in os.listdir(current_dir):
        # 过滤掉 __init__.py 本身和非 py 文件
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            # 动态导入该模块，这会触发模块内函数的 @register_tool 装饰器
            importlib.import_module(f"tinyharness.tools.{module_name}")


autodiscover_tools()
