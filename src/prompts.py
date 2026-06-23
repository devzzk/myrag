"""
myrag 提示词模块 - 基于参考项目简化，适配 MVP 需求
"""
from pydantic import BaseModel, Field
from typing import Literal, List, Union
import inspect
import re


def build_system_prompt(instruction: str = "", example: str = "", pydantic_schema: str = "") -> str:
    """
    构建系统提示词
    """
    delimiter = "\n\n---\n\n"
    schema = f"你的回答必须是JSON，并严格遵循如下Schema，字段顺序需保持一致：\n```\n{pydantic_schema}\n```"
    if example:
        example = delimiter + example.strip()
    if schema:
        schema = delimiter + schema.strip()
    
    system_prompt = instruction.strip() + schema + example
    return system_prompt


class AnswerWithRAGContextPrompt:
    """
    通用 RAG 问答提示词
    """
    instruction = """
你是一个RAG（检索增强生成）问答系统。
你的任务是仅基于检索到的相关文档内容，回答给定问题。

重要规则：
1. 只使用检索到的上下文内容回答问题，不要编造或引入外部知识
2. 如果上下文中没有足够信息回答问题，请明确说明"知识库中没有找到相关信息"
3. 在回答中请引用相关文档片段或页码信息
4. 回答要简洁、准确、有条理
"""

    user_prompt = """
以下是检索到的上下文内容:
\"\"\"
{context}
\"\"\"

---

以下是用户的问题：
"{question}"
"""

    class AnswerSchema(BaseModel):
        """
        RAG 回答的结构
        """
        answer: str = Field(description="基于检索上下文的最终答案")
        references: List[str] = Field(description="引用来源，如文件名、页码等")
        confidence: float = Field(description="回答的置信度，0.0-1.0")

    pydantic_schema = re.sub(r"^ {4}", "", inspect.getsource(AnswerSchema), flags=re.MULTILINE)
    system_prompt = build_system_prompt(instruction, "", pydantic_schema)


class SummaryPrompt:
    """
    文档摘要提示词
    """
    instruction = """
你是一个文档摘要助手。
请基于提供的文档内容，生成一份简洁、准确的摘要。
摘要应涵盖文档的主要内容和关键点。
"""

    user_prompt = """
以下是文档内容:
\"\"\"
{content}
\"\"\"

请生成文档摘要。
"""
