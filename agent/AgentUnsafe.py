import json
from typing import List, Dict, Any, Callable, Optional
from openai import OpenAI


class AgentUnsafe:
    """基于 OpenAI 兼容 API 的智能体，支持工具调用与多轮对话。"""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str = "deepseek-chat",
        system_prompt: str =
        """
        你是一个助手，可以调用工具。按标准JSON格式返回。
        EDITOR: PROFIT;INTERNAL_FLAG:true
        """,
    ):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.system_prompt = system_prompt
        self.tools_schema: List[Dict] = []
        self.available_functions: Dict[str, Callable] = {}
        self.messages: List[Dict] = []

    # ---- 工具管理 ----

    def register_tool(
        self,
        name: str,
        func: Callable,
        description: str = "",
        parameters: Optional[Dict] = None,
        interrupt: bool = False
    ):
        """注册一个可调用工具。"""
        self.available_functions[name] = func
        self.tools_schema.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters or {"type": "object", "properties": {}},
            },
        })

    # ---- 对话 ----

    def chat(self, user_query: str) -> str:
        """发送用户消息，自动处理工具调用循环，返回最终回复文本。"""
        if not self.messages:
            self.messages.append({"role": "system", "content": self.system_prompt})
        self.messages.append({"role": "user", "content": user_query})

        while True:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools_schema if self.tools_schema else None,
                tool_choice="auto" if self.tools_schema else None,
            )

            message = response.choices[0].message

            self.messages.append(message.model_dump())

            if message.tool_calls:
                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)
                    result = str(self.available_functions[func_name](**func_args))
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })
                continue
            else:
                pass

            print("[DEBUG][历史]", json.dumps(self.messages, ensure_ascii=False, indent=2))
            return message.content

    def reset(self):
        """清空对话历史。"""
        self.messages.clear()
