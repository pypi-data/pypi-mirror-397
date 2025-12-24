"""
A LLM framework thats tiny and fast.
"""

from __future__ import annotations
import json
import time
import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple
import urllib.request
import urllib.error
from .open_ai import ChatGPTModel
from . import open_ai
from .core import (
    _pytype_to_json_schema,
    BasePrompt,
    SystemPrompt,
    UserPrompt,
    ModelPrompt,
    normalize_history,
)

JSONSchema = Dict[str, Any]


class GeminiModel:
    """Gemini LLM yaka client with tool calling loop.
    How to use:
        gm = GeminiModel("gemini-2.5-flash", api_key="...")

        @gm.tool
        def add_numbers(a: float, b: float):
            '''Add two numbers a and b.''' #This Docstring is used as the description for the tool
            return {"result": a + b}

        text = gm.call([], prompt="Add 58027934 and 7902783")
    """

    def __init__(
        self,
        model: str,
        api_key: str,
        max_iterations: int = 6,
        sleep_between: float = 0.2,
    ):
        self.model = model
        self.api_key = api_key
        self.max_iterations = max_iterations
        self.sleep_between = sleep_between

        self._functions: Dict[str, Callable[..., Any]] = {}
        self._tools_declarations: List[Dict[str, Any]] = []

    def tool(
        self, fn: Optional[Callable] = None, *, name: Optional[str] = None
    ) -> Callable:
        """Decorator to register a function as a tool the model can call.

        Usage:
            @gm.tool
            def foo():
                '''Docstring used as the tool description'''
                ...

        The decorator registers the function under its __name__ by default, or
        under the provided `name` kwarg.
        """

        def _register(f: Callable) -> Callable:
            nonlocal name
            tool_name = name or f.__name__
            self._functions[tool_name] = f

            sig = inspect.signature(f)
            properties: Dict[str, Any] = {}
            required: List[str] = []
            for param_name, param in sig.parameters.items():
                ann = (
                    param.annotation if param.annotation is not inspect._empty else str
                )
                jtype = _pytype_to_json_schema(ann)
                properties[param_name] = {"type": jtype}
                if param.default is inspect._empty:
                    required.append(param_name)

            decl = {
                "name": tool_name,
                "description": (f.__doc__ or ""),
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            }
            self._rebuild_tools_declarations()
            return f

        if fn is None:
            return _register

        return _register(fn)

    def _rebuild_tools_declarations(self) -> None:
        """Rebuild self._tools_declarations from currently registered functions."""
        decls: List[Dict[str, Any]] = []
        for name, fn in self._functions.items():
            sig = inspect.signature(fn)
            properties: Dict[str, Any] = {}
            required: List[str] = []
            for param_name, param in sig.parameters.items():
                ann = (
                    param.annotation if param.annotation is not inspect._empty else str
                )
                jtype = _pytype_to_json_schema(ann)
                properties[param_name] = {"type": jtype}
                if param.default is inspect._empty:
                    required.append(param_name)

            decls.append(
                {
                    "name": name,
                    "description": (fn.__doc__ or ""),
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                }
            )
        self._tools_declarations = [{"function_declarations": decls}]

    def _gemini_call_text(self, user_text: str) -> Dict[str, Any]:
        """Send a text prompt (single string) to Gemini; return parsed JSON response."""
        payload = {
            "contents": [{"parts": [{"text": user_text}]}],
            "tools": self._tools_declarations,
        }
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            "{self.model}:generateContent?key={self.api_key}"
        )
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"HTTPError {e.code}: {e.reason}\n{body}")
        except Exception as e:
            raise RuntimeError(f"Network error: {e}")

    @staticmethod
    def _extract_function_call_from_part(
        part: Any,
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Return (name, args_dict) if this part includes a function call."""
        candidates = []
        if isinstance(part, dict):
            if "functionCall" in part:
                candidates.append(part["functionCall"])
            if "function_call" in part:
                candidates.append(part["function_call"])
            for v in part.values():
                if isinstance(v, dict) and ("name" in v and "args" in v):
                    candidates.append(v)
        for c in candidates:
            if not isinstance(c, dict):
                continue
            name = c.get("name")
            args_raw = c.get("args")
            args = {}
            if isinstance(args_raw, dict):
                args = args_raw
            elif isinstance(args_raw, str):
                try:
                    args = json.loads(args_raw)
                except Exception:
                    try:
                        args = eval(args_raw, {"__builtins__": {}})
                    except Exception:
                        args = {}
            else:
                args = {}
            return name, args
        return None, None

    @staticmethod
    def _extract_text_from_response(resp: Dict[str, Any]) -> Optional[str]:
        candidates = resp.get("candidates", []) or []
        texts: List[str] = []
        for cand in candidates:
            content = cand.get("content", {}) or {}
            parts = content.get("parts", []) or []
            for part in parts:
                if isinstance(part, dict):
                    if "text" in part:
                        texts.append(part["text"])
                    elif (
                        "content" in part
                        and isinstance(part["content"], dict)
                        and "text" in part["content"]
                    ):
                        texts.append(part["content"]["text"])
                    else:
                        if "functionCall" not in part and "function_call" not in part:
                            texts.append(json.dumps(part))
                elif isinstance(part, str):
                    texts.append(part)
        return "\n".join(texts) if texts else None

    @staticmethod
    def _convert_simple(v: Any) -> Any:
        if isinstance(v, str):
            try:
                if v.isdigit() or (v.startswith("-") and v[1:].isdigit()):
                    return int(v)
                if any(ch.isdigit() for ch in v) and "." in v:
                    return float(v)
            except Exception:
                pass
        return v

    @staticmethod
    def _normalize_args(fn: Callable, args: Any) -> Dict[str, Any]:
        sig = inspect.signature(fn)
        param_names = list(sig.parameters.keys())

        if args is None:
            return {}
        if isinstance(args, (list, tuple)):
            return {
                param_names[i]: args[i] for i in range(min(len(args), len(param_names)))
            }
        if isinstance(args, dict) and all(str(k).isdigit() for k in args.keys()):
            pairs = sorted(((int(k), v) for k, v in args.items()), key=lambda x: x[0])
            return {
                param_names[i]: GeminiModel._convert_simple(v)
                for i, (_, v) in enumerate(pairs)
                if i < len(param_names)
            }
        if isinstance(args, dict):
            out: Dict[str, Any] = {}
            for k, v in args.items():
                if isinstance(k, str) and k.isdigit():
                    idx = int(k)
                    if 0 <= idx < len(param_names):
                        out[param_names[idx]] = GeminiModel._convert_simple(v)
                    else:
                        out[k] = GeminiModel._convert_simple(v)
                else:
                    out[k] = GeminiModel._convert_simple(v)
            for i, name in enumerate(param_names):
                if name not in out and str(i) in args:
                    out[name] = GeminiModel._convert_simple(args[str(i)])
            return out
        return (
            {param_names[0]: GeminiModel._convert_simple(args)} if param_names else {}
        )

    def call(
        self, history: Optional[List[Any]], prompt: str, role: str = "user"
    ) -> Optional[str]:
        """Run the llm loop.

        Args:
            history: list of BasePrompt or backwards-compatible formats (List[str], List[dict], ...)
            prompt: the new message to send
            role: role name for the prompt (e.g. "user")
        """
        self._rebuild_tools_declarations()

        prompts = normalize_history(history)

        if role == "system":
            prompts.append(SystemPrompt(prompt))
        elif role in ("model", "assistant"):
            prompts.append(ModelPrompt(prompt, role=role))
        else:
            prompts.append(UserPrompt(prompt))

        conversation: List[Dict[str, Any]] = []
        for p in prompts:
            p_role = p.role
            if p_role == "assistant":
                p_role = "model"
            conversation.append({"role": p_role, "text": p.content})

        for _ in range(self.max_iterations):
            convo_text = ""
            for m in conversation:
                if m["role"] == "user":
                    convo_text += f"User: {m['text']}\n"
                elif m["role"] in ("assistant", "model"):
                    if m.get("function_call"):
                        fc = m["function_call"]
                        convo_text += (
                            f"Assistant (function_call):"
                            " {fc.get('name')} args={json.dumps(fc.get('args'))}\n"
                        )
                    else:
                        convo_text += f"Assistant: {m['text']}\n"
                elif m["role"] == "tool":
                    name = m.get("name", "tool")
                    convo_text += f"Tool {name} returned: {m['text']}\n"
                elif m["role"] == "system":
                    convo_text += f"System: {m['text']}\n"

            convo_text += (
                "\nInstruction: Continue the conversation above."
                "Use the available tools if needed and, if you call a tool," 
                " respond with a function call. Otherwise provide the final answer.\n"
            )

            resp = self._gemini_call_text(convo_text)

            candidates = resp.get("candidates", []) or []
            function_called = False
            for cand in candidates:
                content = cand.get("content", {}) or {}
                parts = content.get("parts", []) or []
                for part in parts:
                    name, args = self._extract_function_call_from_part(part)
                    if name:
                        function_called = True
                        conversation.append(
                            {
                                "role": "assistant",
                                "function_call": {"name": name, "args": args},
                            }
                        )
                        fn = self._functions.get(name)
                        if not fn:
                            tool_result = {
                                "error": f"function '{name}' not implemented locally."
                            }
                        else:
                            try:
                                clean_args = self._normalize_args(fn, args)
                                tool_result = fn(**clean_args)
                            except TypeError as e:
                                tool_result = {"error": f"argument mismatch: {e}"}
                        conversation.append(
                            {
                                "role": "tool",
                                "name": name,
                                "text": json.dumps(tool_result),
                            }
                        )
                        time.sleep(self.sleep_between)
                        break
                if function_called:
                    break

            if not function_called:
                final_text = self._extract_text_from_response(resp)
                if final_text:
                    conversation.append({"role": "assistant", "text": final_text})
                    return final_text
                else:
                    return None

        return None


__all__ = ["GeminiModel", "ChatGPTModel"]
