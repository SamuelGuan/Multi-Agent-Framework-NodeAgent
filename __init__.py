'''
Multi-Agent Framework NodeAgent Main Package

这是一个多智能体框架的主包，包含了各种LLM接口、基础代理类和工具类。
'''

# 导入主要的类和模块
from .BaseAgent import BaseAgent
from .LLMs import ZhiPu_LLM, Qwen_LLM, Kimi_LLM, DouBao_LLM
from .BaseTool import BaseToolProtocol
from .AgentTools import StrFileReadTool, Plus, Sub, Mul, Div
from .MultiAgentComponents import *

__version__ = "1.0.0"
__author__ = "Multi-Agent Framework Team"

__all__ = [
    'BaseAgent',
    'ZhiPu_LLM',
    'Qwen_LLM', 
    'Kimi_LLM',
    'DouBao_LLM',
    'BaseToolProtocol',
    'StrFileReadTool',
    'Plus',
    'Sub', 
    'Mul',
    'Div'
]