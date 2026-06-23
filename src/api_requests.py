"""
myrag API 请求模块 - 基于 DashScope
"""
import os
import json
from dotenv import load_dotenv
from typing import Optional, Type, Union, Dict
from pydantic import BaseModel
import dashscope

# Optional imports with fallback
try:
    from tenacity import retry, wait_fixed, stop_after_attempt
    HAS_TENACITY = True
except ImportError:
    HAS_TENACITY = False
    # Define a dummy decorator if tenacity is not available
    def retry(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

from src.prompts import AnswerWithRAGContextPrompt


class BaseDashscopeProcessor:
    """
    DashScope 基础处理器
    """
    def __init__(self):
        # 只在实际需要时才加载环境变量
        self._api_key_loaded = False
        self._api_key = None
        self.default_model = 'qwen-plus'
        self.response_data = None
        # 不设置 base_http_api_url，让 SDK 使用默认配置
    
    def _ensure_api_key(self):
        """确保 API Key 已加载（仅在第一次使用时调用）"""
        if not self._api_key_loaded:
            load_dotenv()
            self._api_key = os.getenv("DASHSCOPE_API_KEY")
            dashscope.api_key = self._api_key
            self._api_key_loaded = True
            
            # 检查 API Key 是否存在
            if not self._api_key:
                raise ValueError(
                    "未找到 DASHSCOPE_API_KEY 环境变量！\n"
                    "请在项目根目录创建 .env 文件，内容如下：\n"
                    "DASHSCOPE_API_KEY=your-api-key-here\n\n"
                    "获取 API Key: https://dashscope.console.aliyun.com/"
                )
    
    def send_message(
        self,
        model: Optional[str] = None,
        temperature: float = 0.1,
        system_content: str = "You are a helpful assistant.",
        human_content: str = "Hello!",
        is_structured: bool = False,
        response_format: Optional[Type[BaseModel]] = None,
    ):
        """
        发送消息到 DashScope Qwen 大模型
        """
        self._ensure_api_key()
        
        if model is None:
            model = self.default_model
        
        messages = []
        if system_content:
            messages.append({"role": "system", "content": system_content})
        if human_content:
            messages.append({"role": "user", "content": human_content})
        
        try:
            response = dashscope.Generation.call(
                model=model,
                messages=messages,
                temperature=temperature,
                result_format='message'
            )
        except Exception as e:
            raise Exception(f"API 调用失败: {e}\n"
                          f"请检查:\n"
                          f"1. API Key 是否正确\n"
                          f"2. 网络连接是否正常\n"
                          f"3. 模型名称是否正确\n"
                          f"4. API 地址是否正确")
        
        if response.status_code == 200:
            content = response.output.choices[0].message.content
            self.response_data = {
                "model": model,
                "input_tokens": response.usage.input_tokens if hasattr(response.usage, 'input_tokens') else None,
                "output_tokens": response.usage.output_tokens if hasattr(response.usage, 'output_tokens') else None,
            }
            
            # Try to parse structured output
            if is_structured and response_format:
                try:
                    # Extract JSON part
                    json_start = content.find('{')
                    json_end = content.rfind('}')
                    if json_start != -1 and json_end != -1:
                        json_str = content[json_start:json_end+1]
                        parsed = json.loads(json_str)
                        return response_format(**parsed)
                except Exception:
                    pass
            
            return content
        else:
            error_msg = f"DashScope API 请求失败 (状态码 {response.status_code})\n"
            if hasattr(response, 'message'):
                error_msg += f"消息: {response.message}\n"
            if hasattr(response, 'code'):
                error_msg += f"错误码: {response.code}\n"
            error_msg += "\n排查建议:\n"
            error_msg += "1. 检查 API Key 是否正确且有效\n"
            error_msg += "2. 检查账户是否有足够的余额\n"
            error_msg += "3. 检查模型名称是否正确\n"
            error_msg += "4. 访问: https://help.aliyun.com/zh/model-studio/error-code"
            raise Exception(error_msg)
    
    def get_embeddings(self, texts: Union[str, list], model: Optional[str] = None):
        """
        获取文本嵌入向量
        """
        self._ensure_api_key()
        
        # 使用默认模型
        if model is None:
            model = "gte-rerank-v2"
        
        if isinstance(texts, str):
            texts = [texts]
        
        # Filter empty strings
        texts = [t for t in texts if t.strip()]
        
        if not texts:
            return []
        
        embeddings = []
        
        try:
            # Process in batches (max 25 per batch)
            batch_size = 25
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                resp = dashscope.TextEmbedding.call(
                    model=model,
                    input=batch
                )
                
                if resp.status_code == 200:
                    if 'output' in resp and 'embeddings' in resp['output']:
                        for emb in resp['output']['embeddings']:
                            embeddings.append(emb['embedding'])
                else:
                    raise Exception(f"嵌入API调用失败: {resp.message if hasattr(resp, 'message') else resp}")
        except Exception as e:
            raise Exception(f"获取嵌入向量失败: {e}\n"
                          f"请检查 API Key 是否正确")
        
        return embeddings


class APIProcessor:
    """
    API 处理器 - 统一接口
    """
    def __init__(self, provider: str = "dashscope"):
        self.provider = provider
        self.processor = BaseDashscopeProcessor()
    
    def get_answer_from_rag(self, question: str, context: str, model: Optional[str] = None):
        """
        基于 RAG 上下文获取答案
        """
        answer_obj = self.processor.send_message(
            model=model,
            system_content=AnswerWithRAGContextPrompt.system_prompt,
            human_content=AnswerWithRAGContextPrompt.user_prompt.format(
                context=context,
                question=question
            ),
            is_structured=False,
        )
        
        if isinstance(answer_obj, str):
            try:
                json_start = answer_obj.find('{')
                json_end = answer_obj.rfind('}')
                if json_start != -1 and json_end != -1:
                    json_str = answer_obj[json_start:json_end+1]
                    parsed = json.loads(json_str)
                    return {
                        "answer": parsed.get("answer", answer_obj),
                        "references": parsed.get("references", []),
                        "confidence": parsed.get("confidence", 0.5)
                    }
            except Exception:
                pass
            
            return {
                "answer": answer_obj,
                "references": [],
                "confidence": 0.5
            }
        
        return answer_obj
    
    def get_embeddings(self, texts, model=None):
        return self.processor.get_embeddings(texts, model)
