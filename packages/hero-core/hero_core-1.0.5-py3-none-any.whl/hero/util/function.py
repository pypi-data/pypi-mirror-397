from dataclasses import asdict
import json
import os
from datetime import datetime
import re
from string import printable
import xml.etree.ElementTree as ET

from typing import List

# TODO: 后期优化，在 Hero 中可以自定义这些参数
SPLIT_FILE_LIMIT = 50000
LINE_LIMIT = 100000
MAX_HISTORY_COUNT = 20
MAX_HISTORY_LIMIT = 40000

class DataclassEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, '__dataclass_fields__'):
            dict_obj = asdict(o)
            swap = ""
            if "reasoning" in dict_obj:
                swap = dict_obj["reasoning"]
                dict_obj["reasoning"] = dict_obj["pure_reasoning"]
                del dict_obj["pure_reasoning"]
                dict_obj["message"] = swap
            return dict_obj

        return super().default(o)

def parse_reason(content: str) -> tuple[str, List[dict], str]:
    # 如果没有以 </tool_call> 结尾，尝试添加 </tool_call>
    # 应对 kimi 和 deepseek 经常不出现最后一个 </tool_call> 标签的问题
    if "</tool_call>" not in content:
        content += "\n</tool_call>"
    think_pattern = re.compile(r'<think>\s*(.+?)\s*</think>', re.DOTALL)
    tool_call_pattern = re.compile(r'<tool_call>\s*(.+?)\s*</tool_call>', re.DOTALL)
    pure_reasoning = ""
    error = ""
    json_objects = []
    think_matches = think_pattern.findall(content)
    tool_call_matches = tool_call_pattern.findall(content)
    for think_str in think_matches:
        pure_reasoning += think_str
    for tool_call_str in tool_call_matches:
        try:
            # 解析 XML 格式的 tool_call
            # 格式: <tool_call><tool_name>name</tool_name><params><param name="key">value</param></params></tool_call>
            root = ET.fromstring(f"<tool_call>{tool_call_str}</tool_call>")
            
            # 提取 tool_name
            tool_name_elem = root.find('tool_name')
            if tool_name_elem is None:
                if not error:  # 只记录第一个错误
                    error = f"Missing tool_name in tool_call: {tool_call_str}"
                continue
            tool_name = tool_name_elem.text.strip() if tool_name_elem.text else ""
            
            if not tool_name:
                if not error:
                    error = f"Empty tool_name in tool_call: {tool_call_str}"
                continue
            
            # 提取 params
            params = {}
            params_elem = root.find('params')
            if params_elem is not None:
                for param_elem in params_elem.findall('param'):
                    param_name = param_elem.get('name')
                    if not param_name:
                        continue
                    
                    # 检查是否包含 <item> 标签（数组形式）
                    item_elems = param_elem.findall('item')
                    if item_elems:
                        # 数组形式：提取所有 <item> 的值
                        param_value = [item.text.strip() if item.text else "" for item in item_elems]
                        # 过滤掉空值
                        param_value = [v for v in param_value if v]
                    else:
                        # 普通字符串形式
                        param_value = param_elem.text.strip() if param_elem.text else ""
                    
                    params[param_name] = param_value
            
            # 构建字典对象，格式与原来的 JSON 格式保持一致
            json_obj = {
                "tool": tool_name,
                "params": params
            }
            json_objects.append(json_obj)
        except ET.ParseError as e:
            if not error:  # 只记录第一个错误
                error = f"Failed to parse tool call XML: {tool_call_str}, error: {e}"
        except Exception as e:
            if not error:  # 只记录第一个错误
                error = f"Failed to parse tool call: {tool_call_str}, error: {e}"
    
    # 如果有错误但没有成功解析任何 tool_call，才返回错误
    if error and not json_objects:
        return pure_reasoning, json_objects, error
    
    remaining_text = pure_reasoning.strip()
    return remaining_text, json_objects, ""

def write_file(dir, file_name, content):
    """
    写入文件
    """
    file_path = os.path.join(dir, file_name)
    if not os.path.exists(dir):
        os.makedirs(dir)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def read_file(dir, file_name):
    """
    读取文件
    """
    file_path = os.path.join(dir, file_name)
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def append_file(dir, file_name, content):
    file_path = os.path.join(dir, file_name)
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(content)

def timestamp():
    """
    获取当前时间戳
    """
    return str(int(datetime.now().timestamp()))

def timestamp_to_str(timestamp: str):
    """
    将时间戳转换为字符串
    """
    return datetime.fromtimestamp(int(timestamp)).strftime("%H:%M:%S")

def get_head_and_tail_n_chars(text: str, n: int = 1000) -> str:
    """
    获取文本的头部和尾部指定数量的字符
    """
    if not text:
        return ""
    if len(text) > n:
        half_n = n // 2
        return f"<!-- Original length: {len(text)} bytes, truncated to: head {half_n} bytes and tail {half_n} bytes -->\n{text[:half_n]}\n...\n{text[-half_n:]}"
    return text

def file_to_text_with_line_number(file_path: str) -> str:
    """
    将文件转换为带有行号的文本
    """
    text = ""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        text += "".join([f"{i+1}: {line}" for i, line in enumerate(lines)])
    return text

def clean_tqdm_output(output: str) -> str:
    """Clean tqdm progress bars from output."""
    if not output:
        return ""

    # Remove tqdm progress bars (they typically contain \r and %)
    lines = output.split("\n")
    cleaned_lines = []

    for line in lines:
        # Skip tqdm progress bars
        if "\r" in line and ("%" in line or "it/s" in line):
            continue
        # Skip lines that are just progress indicators
        if line.strip().endswith("%") or line.strip().endswith("it/s"):
            continue
        # Skip lines that are just progress bars
        if re.match(r"^\s*[\d.]+\%|\d+/\d+|\d+it/s", line.strip()):
            continue
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)
