import json
from typing import Literal, List, Union, Dict

from duowen_agent.utils.core_utils import remove_think
from pydantic import BaseModel, Field

openai_params_list = {
    "messages",
    "model",
    "audio",
    "frequency_penalty",
    "function_call",
    "functions",
    "logit_bias",
    "logprobs",
    "max_completion_tokens",
    "max_tokens",
    "metadata",
    "modalities",
    "n",
    "parallel_tool_calls",
    "prediction",
    "presence_penalty",
    "response_format",
    "seed",
    "service_tier",
    "stop",
    "store",
    "stream",
    "stream_options",
    "temperature",
    "tool_choice",
    "tools",
    "top_logprobs",
    "top_p",
    "user",
}


class BaseContent(BaseModel):
    """内容基类"""


class TextContent(BaseContent):
    type: Literal["text"] = "text"
    text: str

    def to_dict(self):
        return {"type": self.type, "text": self.text}


class ImageURLContent(BaseContent):
    type: Literal["image_url"] = "image_url"
    image_url: Dict[str, str]

    def to_dict(self):
        return {"type": self.type, "image_url": self.image_url}


ContentUnion = Union[TextContent, ImageURLContent]


class Message(BaseModel):
    role: Literal["system", "user", "assistant"] = "user"
    content: Union[str, List[ContentUnion]]

    def __init__(
        self,
        content: Union[str, List[ContentUnion]],
        role: Literal["system", "user", "assistant"] = "user",
    ):
        super().__init__(content=content, role=role)

    def __getitem__(self, item):
        if item == "content":
            return self.content
        elif item == "role":
            return self.role
        else:
            raise KeyError(f"Message has no key {item}")

    def format_str(self) -> str:
        if isinstance(self.content, str):
            return (
                f"<{self.role}>\n"
                + "\n".join(["  " + j for j in self.content.split("\n")])
                + f"\n</{self.role}>"
            )
        else:
            return (
                f"<{self.role}>\n"
                + "\n".join([f"  {str(j)}" for j in self.content])
                + f"\n</{self.role}>"
            )

    def to_dict(self) -> dict:

        if isinstance(self.content, str):
            return {"role": self.role, "content": self.content}
        else:
            return {"role": self.role, "content": [i.to_dict() for i in self.content]}


class SystemMessage(Message):
    def __init__(self, content: Union[str, List[ContentUnion]]):
        super().__init__(content, "system")


class UserMessage(Message):
    def __init__(self, content: Union[str, List[ContentUnion]]):
        super().__init__(content, "user")


class AssistantMessage(Message):
    def __init__(self, content: Union[str, List[ContentUnion]]):
        super().__init__(content, "assistant")


class MessagesSet(BaseModel):
    message_list: List[Message] = []

    def __init__(self, message_list: List[dict] | List[Message] = None):
        if message_list:
            if isinstance(message_list[0], dict):
                message_list = [Message(**i) for i in message_list]
            elif isinstance(message_list[0], Message):
                pass
            else:
                raise ValueError("MessagesSet init message_list type error")
            super().__init__(message_list=message_list)
        else:
            super().__init__()

    def remove_assistant_think(self):
        """推理模型需要剔除think部分"""
        for message in self.message_list:
            if message.role == "assistant":
                message.content = remove_think(message.content)
        return self

    def init_message_list(self, message: List[Dict[str, str]]):
        for i in message:
            if i["role"] == "assistant":
                self.add_assistant(i["content"])
            elif i["role"] == "system":
                self.add_system(i["content"])
            elif i["role"] == "user":
                self.add_user(i["content"])
        return self

    def add_user(self, content: Union[str, ContentUnion, List[ContentUnion]]):
        self.message_list.append(UserMessage(content))
        return self

    def add_assistant(self, content: Union[str, ContentUnion, List[ContentUnion]]):
        self.message_list.append(AssistantMessage(content))
        return self

    def add_system(self, content: Union[str, ContentUnion, List[ContentUnion]]):
        self.message_list.append(SystemMessage(content))
        return self

    def append_messages(
        self, messages_set: Union["MessagesSet", List[UserMessage | AssistantMessage]]
    ):
        """追加消息集合到当前集合"""
        if type(messages_set) is MessagesSet:
            self.message_list = self.message_list + messages_set.message_list
        else:
            for message in messages_set:
                if type(message) is Message:
                    self.message_list.append(message)
                else:
                    raise ValueError("MessagesSet append_messages type error")
        return self

    def append(self, message: Message):
        """追加单个消息"""
        if not isinstance(message, Message):
            raise TypeError("Only Message objects can be appended to MessagesSet")
        self.message_list.append(message)
        return self

    def pop(self, index: int = -1):
        """移除并返回指定位置的消息"""
        return self.message_list.pop(index)

    def index(self, message: Message, start: int = 0, end: int = None):
        """查找消息的位置"""
        if end is None:
            end = len(self.message_list)
        return self.message_list.index(message, start, end)

    def count(self, message: Message):
        """统计消息出现的次数"""
        return self.message_list.count(message)

    def copy_message(self):
        """创建消息集合的浅拷贝"""
        return MessagesSet(self.message_list.copy())

    def filter_by_role(self, role: Literal["system", "user", "assistant"]):
        """根据角色过滤消息"""
        filtered = [msg for msg in self.message_list if msg.role == role]
        return MessagesSet(filtered)

    def get_first_message(self):
        """获取第一条消息"""
        return self.message_list[0] if self.message_list else None

    def get_last_message(self):
        """获取最后一条消息"""
        return self.message_list[-1] if self.message_list else None

    def remove_first_message(self):
        """移除第一条消息"""
        if self.message_list:
            self.message_list.pop(0)
        return self

    def remove_last_message(self):
        """移除最后一条消息"""
        if self.message_list:
            self.message_list.pop()
        return self

    def is_empty(self):
        """检查是否为空"""
        return len(self.message_list) == 0

    def __contains__(self, message: Message):
        """支持 in 操作符"""
        return message in self.message_list

    def get_messages(self):
        return [i.to_dict() for i in self.message_list]

    def get_format_messages(self):
        _data = []

        for i in self.message_list:
            _data.append(i.format_str())

        return "\n\n".join(_data)

    def pretty_print(self):
        print(self.get_format_messages())

    def __add__(self, other: "MessagesSet") -> "MessagesSet":
        if not isinstance(other, MessagesSet):
            raise TypeError("Can only add MessagesSet to MessagesSet")
        return MessagesSet(self.message_list + other.message_list)

    def __iadd__(self, other: "MessagesSet") -> "MessagesSet":
        if not isinstance(other, MessagesSet):
            raise TypeError("Can only add MessagesSet to MessagesSet")
        return MessagesSet(self.message_list + other.message_list)

    def __getitem__(self, item):
        """支持索引访问和切片操作"""
        if isinstance(item, slice):
            # 切片操作
            return MessagesSet(self.message_list[item])
        return self.message_list[item]

    def __setitem__(self, index, value):
        """支持通过索引设置消息"""
        if not isinstance(value, Message):
            raise TypeError("Only Message objects can be assigned to MessagesSet")
        self.message_list[index] = value

    def __delitem__(self, index):
        """支持通过索引删除消息"""
        del self.message_list[index]

    def insert(self, index, value):
        """在指定位置插入消息"""
        if not isinstance(value, Message):
            raise TypeError("Only Message objects can be inserted into MessagesSet")
        self.message_list.insert(index, value)
        return self

    def extend(self, messages):
        """扩展消息列表"""
        if isinstance(messages, MessagesSet):
            self.message_list.extend(messages.message_list)
        elif isinstance(messages, list):
            for msg in messages:
                if not isinstance(msg, Message):
                    raise TypeError("All items in the list must be Message objects")
            self.message_list.extend(messages)
        else:
            raise TypeError(
                "Can only extend with MessagesSet or list of Message objects"
            )
        return self

    def reverse(self):
        """反转消息顺序"""
        self.message_list.reverse()
        return self

    def clear(self):
        """清空所有消息"""
        self.message_list.clear()
        return self

    def __len__(self):
        return len(self.message_list)

    def __bool__(self):
        return bool(self.message_list)

    def __iter__(self):
        for item in self.message_list:
            yield item

    def __repr__(self):
        return f"MessagesSet({self.message_list})"

    def __str__(self):
        return f"MessagesSet({str(self.message_list)[:200]})"


class Tool(BaseModel):
    name: str
    arguments: Dict = Field(default_factory=dict)
    think: str = None

    def __str__(self):
        return json.dumps(
            {"name": self.name, "arguments": self.arguments, "think": self.think},
            ensure_ascii=False,
        )


class ToolsCall(BaseModel):
    think: str = None
    tools: List[Tool] = Field(default_factory=list)

    def __str__(self):
        return json.dumps(
            {"think": self.think, "tools": [i.model_dump() for i in self.tools]},
            ensure_ascii=False,
        )
