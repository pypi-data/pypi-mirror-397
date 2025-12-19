from dataclasses import asdict
import json
import os
from datetime import datetime
import re
from string import printable
import xml.etree.ElementTree as ET

from typing import List, Tuple, Optional

# TODO: 后期优化，在 Hero 中可以自定义这些参数
SPLIT_FILE_LIMIT = 50000
LINE_LIMIT = 100000
MAX_HISTORY_COUNT = 20
MAX_HISTORY_LIMIT = 40000

def _extract_param_tags(content: str) -> List[Tuple[str, str]]:
    """
    从 params 内容中提取所有 param 标签，正确处理嵌套的 XML 标签。
    返回 [(param_name, param_body), ...] 列表
    
    使用正则表达式匹配，但需要处理参数值中可能包含的 XML 标签。
    由于 param 标签通常不会嵌套（参数值中的标签是文本内容），
    我们可以使用非贪婪匹配，但需要确保匹配到正确的 </param>。
    """
    results = []
    
    # 使用正则表达式匹配所有 param 标签
    # 注意：使用非贪婪匹配可能有问题，如果参数值中包含 </param> 文本
    # 但实际场景中，参数值中的 </param> 应该被转义或使用 CDATA
    # 为了更可靠，我们使用一个更智能的匹配方式
    
    # 首先尝试简单的正则匹配
    param_pattern = re.compile(
        r'<param\s+name\s*=\s*"([^"]+)"\s*>(.*?)</param>',
        re.DOTALL
    )
    
    matches = list(param_pattern.finditer(content))
    
    # 验证匹配结果，确保没有重叠
    used_positions = set()
    for match in matches:
        start = match.start()
        end = match.end()
        
        # 检查是否与已使用的匹配重叠
        overlap = False
        for used_start, used_end in used_positions:
            if not (end <= used_start or start >= used_end):
                overlap = True
                break
        
        if not overlap:
            param_name = match.group(1)
            param_body = match.group(2)
            results.append((param_name, param_body))
            used_positions.add((start, end))
    
    # 如果正则匹配失败或结果不完整，使用栈方法作为后备
    if not results:
        # 使用栈方法进行更精确的匹配
        i = 0
        while i < len(content):
            param_start = content.find('<param', i)
            if param_start == -1:
                break
            
            name_match = re.search(r'name\s*=\s*"([^"]+)"', content[param_start:param_start+500])
            if not name_match:
                i = param_start + 6
                continue
            
            param_name = name_match.group(1)
            tag_end = content.find('>', param_start + name_match.end())
            if tag_end == -1:
                i = param_start + 6
                continue
            
            # 使用栈匹配 </param>
            stack = 1
            pos = tag_end + 1
            param_body_start = pos
            
            while pos < len(content) and stack > 0:
                next_tag = content.find('<', pos)
                if next_tag == -1:
                    break
                
                if next_tag + 8 <= len(content) and content[next_tag:next_tag+8] == '</param>':
                    stack -= 1
                    if stack == 0:
                        param_body = content[param_body_start:next_tag]
                        results.append((param_name, param_body))
                        i = next_tag + 8
                        break
                    pos = next_tag + 8
                elif next_tag + 6 <= len(content) and content[next_tag:next_tag+6] == '<param':
                    tag_close = content.find('>', next_tag)
                    if tag_close != -1:
                        if tag_close > next_tag and content[tag_close-1] == '/':
                            pos = tag_close + 1
                        else:
                            stack += 1
                            pos = tag_close + 1
                    else:
                        pos = next_tag + 1
                else:
                    pos = next_tag + 1
            
            if stack > 0:
                i = param_start + 6
            # else: i 已经在上面更新了
    
    return results


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
            # 从原始字符串中提取 tool_name，避免参数值中包含 tool_name 标签导致解析失败
            # 格式: <tool_call><tool_name>name</tool_name><params>...</params></tool_call>
            # 使用正则表达式提取第一个 <tool_name> 标签的内容
            # 限制搜索范围：tool_name 应该在 params 之前，避免匹配到参数值中的 tool_name
            params_pos = tool_call_str.find('<params>')
            search_end = params_pos if params_pos != -1 else len(tool_call_str)
            search_str = tool_call_str[:search_end]
            
            tool_name_match = re.search(r'<tool_name>(.*?)</tool_name>', search_str, re.DOTALL)
            if not tool_name_match:
                if not error:  # 只记录第一个错误
                    error = f"Missing tool_name in tool_call: {tool_call_str[:200]}"
                continue
            
            tool_name = tool_name_match.group(1).strip() if tool_name_match.group(1) else ""
            
            if not tool_name:
                if not error:
                    error = f"Empty tool_name in tool_call: {tool_call_str}"
                continue
            
            # 为了向后兼容，仍然尝试解析 XML（用于验证结构）
            try:
                root = ET.fromstring(f"<tool_call>{tool_call_str}</tool_call>")
            except ET.ParseError:
                # XML 解析失败不影响，因为我们从原始字符串中提取
                root = None
            
            # 提取 params - 使用自定义函数从原始字符串中提取，避免参数值中的 XML 标签被误解析
            params = {}
            # 从原始 tool_call_str 中提取 params 部分
            # 使用栈方法正确匹配 <params>...</params>，避免参数值中包含 </params> 导致提前结束
            params_content = None
            params_start = tool_call_str.find('<params>')
            if params_start != -1:
                params_start_tag_end = params_start + 8  # '<params>'.length
                # 使用栈匹配 </params>
                stack = 1
                pos = params_start_tag_end
                while pos < len(tool_call_str) and stack > 0:
                    next_tag = tool_call_str.find('<', pos)
                    if next_tag == -1:
                        break
                    # 检查是否是 </params>
                    if next_tag + 9 <= len(tool_call_str) and tool_call_str[next_tag:next_tag+9] == '</params>':
                        stack -= 1
                        if stack == 0:
                            params_content = tool_call_str[params_start_tag_end:next_tag]
                            break
                        pos = next_tag + 9
                    # 检查是否是 <params（嵌套的 params 标签）
                    elif next_tag + 8 <= len(tool_call_str) and tool_call_str[next_tag:next_tag+8] == '<params>':
                        stack += 1
                        pos = next_tag + 8
                    else:
                        pos = next_tag + 1
                
                # 如果栈匹配失败，尝试使用正则表达式作为后备
                if params_content is None:
                    params_match_obj = re.search(r'<params>(.*?)</params>', tool_call_str, re.DOTALL)
                    if params_match_obj:
                        params_content = params_match_obj.group(1)
            
            if params_content is not None:
                # 使用自定义函数提取所有 param 标签，正确处理嵌套
                param_tags = _extract_param_tags(params_content)
                
                for param_name, param_body in param_tags:
                    # 检查是否包含 <item> 标签（数组形式）
                    # 使用正则匹配 <item> 标签
                    item_pattern = re.compile(r'<item>(.*?)</item>', re.DOTALL)
                    item_matches = item_pattern.findall(param_body)
                    
                    if item_matches:
                        # 数组形式：提取所有 <item> 的值
                        # 对于 item 中的内容，也需要处理可能包含的 XML 标签
                        param_value = []
                        for item_content in item_matches:
                            item_text = item_content.strip()
                            if item_text:
                                param_value.append(item_text)
                    else:
                        # 普通字符串形式：直接使用 param_body 的内容
                        # 这样可以保留参数值中的 XML 标签（如 <params>、<param> 等）作为文本
                        param_value = param_body.strip()
                    
                    params[param_name] = param_value
            else:
                # 如果没有找到 params 标签，尝试使用 XML 解析（向后兼容）
                if root is None:
                    # XML 解析失败，无法使用 XML 方式提取 params
                    if not error:
                        error = f"Failed to parse tool_call XML and no params found in raw string: {tool_call_str[:200]}"
                else:
                    params_elem = root.find('params')
                    if params_elem is not None:
                        for param_elem in params_elem.findall('param'):
                            param_name = param_elem.get('name')
                            if not param_name:
                                continue
                            
                            # 检查是否包含直接子元素 <item> 标签（数组形式）
                            item_elems = [child for child in param_elem if child.tag == 'item']
                            if item_elems:
                                param_value = []
                                for item_elem in item_elems:
                                    item_text = ''.join(item_elem.itertext()).strip()
                                    if item_text:
                                        param_value.append(item_text)
                            else:
                                param_value = ''.join(param_elem.itertext()).strip()
                            
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
