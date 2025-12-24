from typing import Any, List, Dict, Optional
from dataclasses import dataclass


def _pytype_to_json_schema(py_type: Any) -> str:
    """Convert python type to a json schema"""
    if py_type in (int, float):
        return "number"
    if py_type is bool:
        return "boolean"
    if py_type is str:
        return "string"
    origin = getattr(py_type, "__origin__", None)
    if origin is not None:
        args = getattr(py_type, "__args__", ()) or ()
        if args:
            return _pytype_to_json_schema(args[0])
    return "string"


@dataclass
class BasePrompt:
    """Base prompt object with role, content."""

    role: str
    content: str

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


class SystemPrompt(BasePrompt):
    def __init__(self, content: str):
        super().__init__("system", content)


class UserPrompt(BasePrompt):
    def __init__(self, content: str):
        super().__init__("user", content)


class ModelPrompt(BasePrompt):
    """
    Model/assistant prompt. Default role is 'model' -Gemini API.
    You may use role='assistant' if you prefer the OpenAIAPI style.
    """

    def __init__(self, content: str, role: str = "model"):
        super().__init__(role, content)


def normalize_history(history: Optional[List[Any]]) -> List[BasePrompt]:
    """
    History normalizer.
    Takes in:
      - List[str] -> each list item becomes UserPrompt.
      - List[dict] with keys 'role' and 'content' or 'text'
      - List[tuple/list] length >= 2 -> first is role, second is content
      - List[BasePrompt]

    Returns: List[BasePrompt]
    """
    out: List[BasePrompt] = []
    if not history:
        return out

    for item in history:
        if isinstance(item, BasePrompt):
            out.append(item)
            continue

        if isinstance(item, dict):
            role = item.get("role") or item.get("name") or "user"
            content = item.get("content") or item.get("text") or ""
            role = str(role)
            if role == "system":
                out.append(SystemPrompt(content))
            elif role in ("model", "assistant"):
                out.append(ModelPrompt(content, role=role))
            else:
                out.append(UserPrompt(content))
            continue

        if isinstance(item, (list, tuple)) and len(item) >= 2:
            role = str(item[0])
            content = str(item[1])
            if role == "system":
                out.append(SystemPrompt(content))
            elif role in ("model", "assistant"):
                out.append(ModelPrompt(content, role=role))
            else:
                out.append(UserPrompt(content))
            continue

        try:
            s = str(item)
            out.append(UserPrompt(s))
        except Exception:
            out.append(UserPrompt(""))

    return out
