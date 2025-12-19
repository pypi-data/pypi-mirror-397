#!/usr/bin/env python3
# coding: utf-8
# Copyright (c) 2024 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
import re
import logging
from dbus_next import Variant
from bmcgo.component.fixture.dbus_signature import DBusSignature

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BusCtlTypeConverter:
    """
    BusCtl类型转换器,提供将BusCtl日志字符串转换为正确D-Bus类型的功能
    支持所有D-Bus标准数据类型，保持与DBusTypeConverter相同的对外接口
    """
    @staticmethod
    def dbus_string_to_type(type_value_str):
        """
        将BusCtl日志中的字符串转换为正确的D-Bus类型

        Args:
            type_value_str: BusCtl日志中的字符串,格式:类型 值

        Returns:
            转换后的Python原生类型或Variant
        """
        if type_value_str is None:
            return None
        # 去除首尾的引号和空格
        value_str = str(type_value_str).strip()
        # 首先尝试转换基本类型
        basic_result = BusCtlTypeConverter._convert_basic_type(value_str)
        if basic_result is not None:
            return basic_result
        # 处理对象路径类型
        if value_str.startswith('OBJECT_PATH '):
            try:
                value_str = BusCtlTypeConverter._trim_trailing_semicolon(value_str)
                path = value_str[13:].strip('"\'')
                return path  # dbus-next使用普通字符串表示对象路径
            except (IndexError, ValueError):
                pass
        # 处理签名类型
        if value_str.startswith('SIGNATURE '):
            try:
                value_str = BusCtlTypeConverter._trim_trailing_semicolon(value_str)
                sig = value_str[10:].strip('"\'')
                return sig  # dbus-next使用普通字符串表示签名
            except (IndexError, ValueError):
                pass
        # 处理复杂类型

        # 处理圆括号结构体类型 (ss) {STRING "A";STRING "B";}
        if re.match(r'^\([^)]+\)\s*\{', value_str):
            return BusCtlTypeConverter._convert_struct_with_no_quote(value_str)
        # 1. 字典/映射类型 - 优先处理，因为它是特殊的数组格式
        if value_str.startswith('ARRAY "{'):
            # 专门处理busctl格式: ARRAY "{ss}" {...}
            # 找到签名结束的引号位置
            first_quote = value_str.find('"')
            second_quote = value_str.find('"', first_quote + 1)
            if second_quote != -1:
                # 从签名结束引号之后查找数组内容的开始花括号
                content_start = value_str.find('{', second_quote + 1)
                if content_start != -1:
                    # 找到匹配的结束花括号
                    end_brace_pos = value_str.rfind('};')
                    if end_brace_pos != -1 and end_brace_pos > content_start:
                        # 提取完整的数组内容（包含花括号）
                        array_content = value_str[content_start:end_brace_pos + 2]
                        # 检查是否包含DICT_ENTRY
                        if 'DICT_ENTRY' in array_content:
                            # 调用字典转换函数
                            result = BusCtlTypeConverter._convert_dictionary_type(value_str)
                            # 如果结果是None（空字典），返回空字典而不是None
                            return result if result is not None else {}
                        else:
                            # 检查是否为空字典数组（去除空白后只有{}或{;}）
                            stripped_content = array_content.strip()
                            # 移除所有空白字符（包括换行、空格等）后检查
                            normalized = re.sub(r'\s+', '', stripped_content)
                            # 匹配各种可能的空数组格式：{}, {;}, { };, { };}, 等
                            flag_norma = normalized in ['{}', '{;}', '{;};', '{};']
                            flag_start_end = normalized.startswith('{') and normalized.endswith('}')
                            flag_length = len(normalized) <= 5
                            if flag_norma or (flag_start_end and flag_length):
                                # 空字典数组，返回空字典
                                return {}
        # 更精确地处理结构体数组格式: ARRAY "(ss)" { ... }
        if value_str.startswith('ARRAY "('):
            result = BusCtlTypeConverter._handle_struct_array(value_str)
            if isinstance(result, list) and len(result) == 0:
                logger.warning(f"结构体数组解析结果为空，输入字符串长度: {len(value_str)}")
            return result
        # 字节数组类型 - BusCtl格式可能与dbus-monitor不同
        if value_str.startswith('ARRAY "y" '):
            try:
                result = BusCtlTypeConverter._convert_array_of_bytes(value_str)
                if result is not None:
                    return result
            except Exception as e:
                logger.error(f"字节数组解析错误: {e}")
                pass
        #  普通数组类型放最后处理 - 支持嵌套结构
        if value_str.startswith('ARRAY '):
            try:
                result = BusCtlTypeConverter._convert_array_type(value_str)
                if result is not None:
                    return result
            except Exception as e:
                logger.error(f"数组解析错误: {e}")
                pass
        # 3. 结构体类型
        if value_str.startswith('STRUCT '):
            try:
                result = BusCtlTypeConverter._convert_struct_type(value_str)
                if result is not None:
                    return result
            except Exception as e:
                logger.error(f"结构体解析错误: {e}", exc_info=True)
                pass
        # 4. 变体类型
        if value_str.startswith('VARIANT '):
            explicit_sig = None
            try:
                # 先尝试直接从VARIANT描述中提取显式签名，例如：VARIANT "s" STRING "foo";
                match = re.match(r'^VARIANT\s+"([^"]+)"\s*(.*)$', value_str, re.DOTALL)
                variant_payload = None
                if match:
                    explicit_sig = match.group(1).strip()
                    variant_payload = match.group(2).strip()
                    # 处理特殊格式：VARIANT "v" <userdata>; 表示无法序列化的 Variant
                    if variant_payload.startswith('<userdata>'):
                        # 对于 <userdata>，创建一个 Variant("v", Variant("v", None))
                        # 或者创建一个 Variant("v", Variant("s", "<userdata>"))
                        # 这里我们使用一个字符串作为占位符
                        inner_variant = Variant("s", "<userdata>")
                        return Variant("v", inner_variant)
                    # 如果 payload 为空或仍然是 { ... } 包裹的内容，则回退到统一的内容提取逻辑
                    if (not variant_payload
                            or variant_payload.startswith('{')
                            or variant_payload.startswith('VARIANT ')):
                        variant_payload = BusCtlTypeConverter.extract_content_from_type(value_str, "VARIANT")
                else:
                    variant_payload = BusCtlTypeConverter.extract_content_from_type(value_str, "VARIANT")
                # 检查提取的内容是否仍然是 <userdata>
                if variant_payload and variant_payload.strip().startswith('<userdata>'):
                    inner_variant = Variant("s", "<userdata>")
                    return Variant(explicit_sig or "v", inner_variant)

                converted_value = BusCtlTypeConverter.dbus_string_to_type(variant_payload)
                signature = explicit_sig or DBusSignature.get_dbus_signature(converted_value)
                return Variant(signature, converted_value)
            except Exception as e:
                logger.error(f"变体解析错误: {e}")
                pass
        # 默认返回原始字符串
        return value_str

    @staticmethod
    def extract_content_from_type(value_str, type_name):
        """
        公共函数：提取指定类型数据结构中的内容部分，去除类型名称和可选的类型签名。
        支持两种格式：
        1. 带大括号的格式：'TYPE_NAME "signature" { content }'
        2. VARIANT特殊格式：'VARIANT "signature" content'

        Args:
            value_str: 包含数据结构内容的字符串
            type_name: 数据结构类型名称，如'STRUCT'、'ARRAY'、'DICT_ENTRY'、'VARIANT'等

        Returns:
            str: 提取出的内容字符串，如果无法提取则返回None
        """
        import re
        # 先尝试匹配带大括号的标准格式
        pattern = r'{}\s*(?:"[^"]*")?\s*\{{'.format(type_name)
        match = re.search(pattern, value_str)
        if match:
            # 处理带大括号的格式，使用括号平衡算法找到匹配的右花括号
            # match.end() 是匹配结束的位置（即 { 之后），所以 match.end() - 1 是 { 的位置
            start_brace = match.end() - 1
            if start_brace != -1:
                # 使用括号平衡算法找到匹配的右花括号
                brace_count = 1
                end_brace = start_brace + 1
                in_quotes = False
                quote_char = None
                while end_brace < len(value_str) and brace_count > 0:
                    char = value_str[end_brace]
                    # 处理引号
                    if char in ['"', "'"] and (end_brace == 0 or value_str[end_brace - 1] != '\\'):
                        if in_quotes and char == quote_char:
                            in_quotes = False
                            quote_char = None
                        elif not in_quotes:
                            in_quotes = True
                            quote_char = char
                    elif not in_quotes:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                    end_brace += 1
                if brace_count == 0:
                    # 找到了匹配的右花括号，提取内容（不包括花括号本身）
                    extracted = value_str[start_brace + 1:end_brace - 1].strip()
                    return extracted
                else:
                    logger.warning(f"extract_content_from_type: 括号不平衡，brace_count={ \
                        brace_count}, end_brace={end_brace}, value_str长度={len(value_str)}")
        elif type_name == "VARIANT":
            # 特殊处理VARIANT类型，没有大括号的格式
            # 匹配VARIANT后跟可选的签名，然后提取剩余内容
            variant_pattern = r'VARIANT\s*(?:"[^"]*")?\s*(.*?);?$'
            variant_match = re.search(variant_pattern, value_str)
            if variant_match:
                return variant_match.group(1).strip()
        else:
            logger.warning(f"extract_content_from_type: 正则匹配失败，pattern={pattern}, value_str前200字符={value_str[:200]}")
        return None

    @staticmethod
    def compare_dbus_objects(obj1, obj2):
        """
        比较两个 D-Bus 对象是否相等

        在dbus-next中，我们比较Python原生类型
        """
        # 对于变体类型特殊处理
        if isinstance(obj1, Variant) and isinstance(obj2, Variant):
            return BusCtlTypeConverter.compare_dbus_objects(obj1.value, obj2.value)
        elif isinstance(obj1, Variant):
            return BusCtlTypeConverter.compare_dbus_objects(obj1.value, obj2)
        elif isinstance(obj2, Variant):
            return BusCtlTypeConverter.compare_dbus_objects(obj1, obj2.value)

        # 检查类型是否匹配
        if type(obj1) != type(obj2):
            # 处理数值类型的兼容性（例如int和float）
            if isinstance(obj1, (int, float)) and isinstance(obj2, (int, float)):
                return abs(obj1 - obj2) < 1e-10  # 浮点数比较需要容差
            return False
        # 对于基本类型，直接比较
        if isinstance(obj1, (int, float, str, bool)):
            if isinstance(obj1, float) and isinstance(obj2, float):
                return abs(obj1 - obj2) < 1e-10  # 浮点数比较需要容差
            return obj1 == obj2
        # 对于列表/数组类型，递归比较每个元素
        elif isinstance(obj1, list):
            if len(obj1) != len(obj2):
                return False
            
            # 空列表直接返回 True
            if len(obj1) == 0:
                return True
            
            # 特殊处理：如果两个列表都只包含字符串，进行集合比较（忽略顺序）
            # 这对于字符串数组（as类型）很有用
            if (all(isinstance(x, str) for x in obj1) and
                all(isinstance(x, str) for x in obj2)):
                # 对于字符串数组，使用集合比较
                return set(obj1) == set(obj2)
            
            # 对于其他类型的列表，逐个比较元素（保持顺序）
            for i in range(len(obj1)):
                if not BusCtlTypeConverter.compare_dbus_objects(obj1[i], obj2[i]):
                    return False
            return True
        # 对于字典类型，递归比较每个键值对
        elif isinstance(obj1, dict):
            if len(obj1) != len(obj2):
                return False
            for key in obj1:
                if key not in obj2:
                    return False
                if not BusCtlTypeConverter.compare_dbus_objects(obj1[key], obj2[key]):
                    return False
            return True
        # 对于元组/结构体类型，递归比较每个元素
        elif isinstance(obj1, tuple):
            if len(obj1) != len(obj2):
                return False
            for i in range(len(obj1)):
                if not BusCtlTypeConverter.compare_dbus_objects(obj1[i], obj2[i]):
                    return False
            return True
        # 对于其他类型，尝试字符串比较
        else:
            return str(obj1) == str(obj2)

    @staticmethod
    def _get_value(value_str):
        """
        从字符串中提取值，通过空格分割，返回分割后的第二个部分,分割后去掉首尾空格

        Args:
            value_str: 包含值的字符串，格式：类型 值 比如'string "Requestor"'

        Returns:
            提取出的值，字符串类型
        """
        # 处理带引号的字符串
        parts = value_str.split(' ', 1)
        if len(parts) < 2:
            # 如果没有空格分隔，返回原字符串
            return value_str.strip()
        return parts[1].strip()  # 使用空格分割并去掉首尾空格

    @staticmethod
    def _convert_basic_type(type_value_str):
        """
        转换D-Bus基本类型

        Args:
            type_value_str: 要转换的基本类型字符串，格式：类型 值,比如STRING "Slot";

        Returns:
            转换后的Python原生类型，如果无法转换则返回None
        """
        # 先处理末尾分号
        type_value_str = type_value_str.strip()
        if type_value_str.endswith(';'):
            type_value_str = type_value_str[:-1].strip()
        value_str = BusCtlTypeConverter._get_value(type_value_str)
        # 1. 字节类型: "BYTE 1" -> 1 (Python int)
        if type_value_str.upper().startswith('BYTE '):
            try:
                # BusCtl中字节值可能是十六进制或十进制
                if value_str.startswith('0x'):
                    return int(value_str, 16)
                return int(value_str)
            except (IndexError, ValueError):
                pass
        # 2. 字符串类型处理
        if type_value_str.upper().startswith('STRING '):
            try:
                string_value = value_str
                flag_dpuble = string_value.startswith('"') and string_value.endswith('"')
                flag_single = string_value.startswith("'") and string_value.endswith("'")
                # 处理带引号的情况
                if flag_dpuble or flag_single:
                    string_value = string_value[1:-1]
                    # 处理转义字符
                    string_value = string_value.replace(r'\\n', '\n').replace(r'\\t', '\t').replace(r'\\\\', '\\')
                return string_value
            except (IndexError, ValueError):
                pass
        # 3. 布尔类型: "BOOLEAN true" -> True
        if type_value_str.upper().startswith('BOOLEAN '):
            bool_value = value_str.lower()
            return bool_value == 'true'
        elif type_value_str.lower() == 'true':
            return True
        elif type_value_str.lower() == 'false':
            return False
        # 4. 整数类型
        # 4.1 有符号16位整数
        if type_value_str.upper().startswith('INT16 '):
            try:
                # 处理十六进制表示
                if value_str.startswith('0x'):
                    return int(value_str, 16)
                return int(value_str)
            except (IndexError, ValueError):
                pass
        # 4.2 无符号16位整数
        elif type_value_str.upper().startswith('UINT16 '):
            try:
                # 处理十六进制表示
                if value_str.startswith('0x'):
                    return int(value_str, 16)
                return int(value_str)
            except (IndexError, ValueError):
                pass
        # 4.3 有符号32位整数
        elif type_value_str.upper().startswith('INT32 '):
            try:
                # 处理十六进制表示
                if value_str.startswith('0x'):
                    return int(value_str, 16)
                return int(value_str)
            except (IndexError, ValueError):
                pass
        # 4.4 无符号32位整数
        elif type_value_str.upper().startswith('UINT32 '):
            try:
                # 处理十六进制表示
                if value_str.startswith('0x'):
                    return int(value_str, 16)
                return int(value_str)
            except (IndexError, ValueError):
                pass
        # 4.5 有符号64位整数
        elif type_value_str.upper().startswith('INT64 '):
            try:
                # 处理十六进制表示
                if value_str.startswith('0x'):
                    return int(value_str, 16)
                return int(value_str)
            except (IndexError, ValueError):
                pass
        # 4.6 无符号64位整数
        elif type_value_str.upper().startswith('UINT64 '):
            try:
                # 处理十六进制表示
                if value_str.startswith('0x'):
                    return int(value_str, 16)
                return int(value_str)
            except (IndexError, ValueError):
                pass
        # 5. 浮点数类型
        # 5.1 double类型
        if type_value_str.upper().startswith('DOUBLE '):
            try:
                return float(value_str)
            except (IndexError, ValueError):
                pass
        # 5.2 float类型
        elif type_value_str.upper().startswith('FLOAT '):
            try:
                return float(value_str)
            except (IndexError, ValueError):
                pass
        # 无法识别为基本类型
        return None

    @staticmethod
    def _convert_struct_with_no_quote(value_str):
        """
        转换不带STRUCT关键字的结构体字符串为dbus-next可识别的格式，只是有圆括号
        例如: "(ss) {STRING "A";STRING "B";}" -> ["A", "B"]
        支持嵌套结构，如 "(ssayay) { STRING "A"; ARRAY "y" { BYTE 1; }; }"
        """
        import re
        # 找到第一个花括号的位置
        brace_start = value_str.find('{')
        if brace_start == -1:
            return value_str

        # 使用括号平衡算法提取完整的花括号内容
        brace_balance = 0
        in_quotes = False
        quote_char = None
        brace_end = -1
        for i in range(brace_start, len(value_str)):
            char = value_str[i]
            # 处理引号状态
            if char in ['"', "'"] and (i == 0 or value_str[i-1] != '\\'):
                if in_quotes and char == quote_char:
                    in_quotes = False
                    quote_char = None
                elif not in_quotes:
                    in_quotes = True
                    quote_char = char
                continue
            # 只在非引号内处理括号
            if not in_quotes:
                if char == '{':
                    brace_balance += 1
                elif char == '}':
                    brace_balance -= 1
                    if brace_balance == 0:
                        brace_end = i
                        break
        if brace_end == -1:
            return value_str
        # 提取花括号内的内容（不包括花括号本身）
        inner_content = value_str[brace_start + 1:brace_end].strip()
        if not inner_content:
            return []
        # 使用智能分割函数分割字段（考虑嵌套结构和引号）
        fields = BusCtlTypeConverter._split_elements_by_semicolon(inner_content)
        # 转换每个字段
        struct_fields = []
        for field in fields:
            field = field.strip()
            if field:
                converted_field = BusCtlTypeConverter.dbus_string_to_type(field)
                struct_fields.append(converted_field)
        return struct_fields

    @staticmethod
    def _split_elements_by_semicolon(content):
        """
        智能分割带分号的内容，考虑括号嵌套和引号状态

        Args:
            content: 需要分割的内容字符串

        Returns:
            分割后的元素列表
        """
        if not content:
            return []

        elements = []
        current_element = []
        brace_count = 0   # 花括号计数 {}
        paren_count = 0   # 圆括号计数 ()
        bracket_count = 0 # 方括号计数 []
        in_quotes = False
        for i, char in enumerate(content):
            # 处理引号状态
            if char == '"' and (i == 0 or content[i-1] != '\\'):
                in_quotes = not in_quotes
            # 只在非引号内处理括号计数
            if not in_quotes:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                elif char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                elif char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
            # 当遇到分号且所有括号已匹配且不在引号内时，分割元素
            if char == ';' and brace_count == 0 and paren_count == 0 and bracket_count == 0 and not in_quotes:
                # 不包含分号本身
                element = ''.join(current_element).strip()
                if element:
                    elements.append(element)
                current_element = []
            else:
                # 不是分隔符时才添加字符
                current_element.append(char)
        # 处理最后一个元素
        if current_element:
            element = ''.join(current_element).strip()
            if element:
                elements.append(element)
        return elements

    # 然后修复 _handle_struct_array 方法
    @staticmethod
    def _handle_struct_array(value_str):
        """
        value_str: 包含结构体数组内容的字符串，格式为 'ARRAY "(ss)" {...}'
        示例字符串："ARRAY \"(ss)\" { (ss) { STRING \"a\"; STRING \"b\"; }; (ss) { STRING \"c\"; STRING \"d\"; }; };"
        return_type: 转换后的dbus-next结构体数组
        """
        try:
            # 提取ARRAY大括号内的内容
            content = BusCtlTypeConverter.extract_content_from_type(value_str, 'ARRAY')
            if not content:
                logger.warning(f"无法从结构体数组中提取内容，输入前500字符: {value_str[:500]}")
                return []

            # 专门处理结构体数组：每个元素格式是 (signature) { ... };
            # 使用括号平衡算法找到每个结构体元素的边界
            elements = []
            i = 0
            struct_count = 0
            while i < len(content):
                # 跳过空白字符
                while i < len(content) and content[i].isspace():
                    i += 1
                if i >= len(content):
                    break

                # 查找结构体开始：应该是 (signature) {
                if content[i] == '(':
                    # 找到匹配的右括号
                    paren_end = i + 1
                    paren_count = 1
                    while paren_end < len(content) and paren_count > 0:
                        if content[paren_end] == '(':
                            paren_count += 1
                        elif content[paren_end] == ')':
                            paren_count -= 1
                        paren_end += 1

                    # 跳过空白字符，查找左花括号
                    brace_start = paren_end
                    while brace_start < len(content) and content[brace_start].isspace():
                        brace_start += 1
                    if brace_start < len(content) and content[brace_start] == '{':
                        # 找到匹配的右花括号
                        brace_end = brace_start + 1
                        brace_count = 1
                        in_quotes = False
                        quote_char = None
                        while brace_end < len(content) and brace_count > 0:
                            char = content[brace_end]

                            # 处理引号
                            if char in ['"', "'"] and (brace_end == 0 or content[brace_end-1] != '\\'):
                                if in_quotes and char == quote_char:
                                    in_quotes = False
                                    quote_char = None
                                elif not in_quotes:
                                    in_quotes = True
                                    quote_char = char
                            elif not in_quotes:
                                if char == '{':
                                    brace_count += 1
                                elif char == '}':
                                    brace_count -= 1

                            brace_end += 1

                        # 如果括号平衡没有归零，说明没有找到匹配的右花括号
                        if brace_count > 0:
                            logger.warning(f"结构体数组元素括号不平衡: brace_count={brace_count}, 位置={i}, brace_end={brace_end}")
                            break

                        # 查找分号：可能在 brace_end-1 之后（即 }; 的情况），也可能在跳过空白后
                        # 首先检查 brace_end-1 之后是否有分号（}; 的情况）
                        semicolon_pos = -1
                        if brace_end > 0 and brace_end <= len(content):
                            # 检查 brace_end-1 位置之后是否有分号
                            check_pos = brace_end - 1  # 这是 } 的位置
                            # 跳过 } 本身，检查之后是否有分号
                            next_pos = check_pos + 1
                            while next_pos < len(content) and content[next_pos].isspace():
                                next_pos += 1
                            if next_pos < len(content) and content[next_pos] == ';':
                                semicolon_pos = next_pos

                        # 如果没找到，尝试从 brace_end 开始查找
                        if semicolon_pos == -1:
                            semicolon_pos = brace_end
                            while semicolon_pos < len(content) and content[semicolon_pos].isspace():
                                semicolon_pos += 1
                            if semicolon_pos < len(content) and content[semicolon_pos] == ';':
                                pass  # 找到了
                            else:
                                semicolon_pos = -1

                        if semicolon_pos >= 0:
                            # 提取完整的结构体元素（包括分号）
                            struct_element = content[i:semicolon_pos + 1].strip()
                            if struct_element:
                                elements.append(struct_element)
                                struct_count += 1
                            i = semicolon_pos + 1
                        else:
                            # 没有找到分号，可能是最后一个元素，尝试提取结构体元素
                            if brace_count == 0:
                                struct_element = content[i:brace_end].strip()
                                if struct_element:
                                    elements.append(struct_element)
                                    struct_count += 1
                                    i = brace_end  # 继续处理，不要 break
                                else:
                                    break
                            else:
                                break
                    else:
                        # 没有找到左花括号，跳过这个字符
                        i += 1
                else:
                    # 不是结构体开始，跳过这个字符
                    i += 1

            if len(elements) == 0:
                logger.warning(f"结构体数组分割结果为空，content长度={len(content)}, 前500字符={content[:500]}")

            # 转换每个结构体元素
            converted_elements = []
            for idx, elem in enumerate(elements):
                elem = elem.strip()
                # 确保elem是完整的结构体格式
                if elem and '(' in elem and '{' in elem:
                    # 递归转换每个结构体
                    try:
                        converted_value = BusCtlTypeConverter.dbus_string_to_type(elem)
                        converted_elements.append(converted_value)
                    except Exception as e:
                        logger.error(f"转换第 {idx + 1} 个结构体元素时出错: {e}", exc_info=True)
                        # 对于单个元素的错误，跳过该元素继续处理

            # 确保始终返回列表类型
            return converted_elements

        except Exception as e:
            logger.error(f"处理结构体数组时出错: {e}", exc_info=True)

        # 错误情况下也返回空列表而不是原始字符串
        return []

    @staticmethod
    def _trim_trailing_semicolon(value_str):
        """
        移除字符串末尾的分号（如果存在）

        Args:
            value_str: 输入字符串

        Returns:
            移除分号后的字符串
        """
        if value_str.endswith(';'):
            return value_str[:-1].strip()
        return value_str

    @staticmethod
    def _convert_dictionary_type(value_str):
        """
        转换字典类型

        Args:
            value_str: 字典类型的字符串表示

        Returns:
            转换后的Python字典对象,如果无法转换则返回None
        """
        try:
            # 直接使用括号平衡算法提取DICT_ENTRY内容，因为正则表达式无法处理嵌套结构
            dict_entries = BusCtlTypeConverter._extract_dict_entries_with_bracket_balance(value_str)

            result_dict = {}
            for entry in dict_entries:
                # DICT_ENTRY格式: DICT_ENTRY "signature" { key; value; }
                # 需要跳过 DICT_ENTRY "signature" { 部分，提取key和value

                # 找到第一个不在引号内的大括号，这是内容开始的位置
                content_start = -1
                in_quotes = False
                quote_char = None

                for i, char in enumerate(entry):
                    # 处理引号状态
                    if char in ['"', "'"] and (i == 0 or entry[i-1] != '\\'):
                        if in_quotes and char == quote_char:
                            in_quotes = False
                            quote_char = None
                        elif not in_quotes:
                            in_quotes = True
                            quote_char = char
                        continue

                    # 只在非引号内查找大括号
                    if not in_quotes and char == '{':
                        content_start = i + 1
                        break

                if content_start == -1:
                    continue

                # 提取大括号内的内容（去掉最后的};或}）
                content_end = entry.rfind('}')
                if content_end == -1:
                    continue
                # 提取内容，去掉最后的};或}
                inner_content = entry[content_start:content_end].strip()
                # 使用智能分割函数分割key和value
                # 在字典中，key和value之间用分号分隔，但要注意嵌套结构
                brace_count = 0
                paren_count = 0
                bracket_count = 0
                in_quotes = False
                semicolon_pos = -1

                # 查找第一个不在括号内且不在引号内的分号作为key-value分隔符
                for i, char in enumerate(inner_content):
                    # 处理引号状态
                    if char in ['"', "'"] and (i == 0 or inner_content[i-1] != '\\'):
                        if in_quotes and char == quote_char:
                            in_quotes = False
                            quote_char = None
                        elif not in_quotes:
                            in_quotes = True
                            quote_char = char
                        continue

                    if not in_quotes:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                        elif char == '(':
                            paren_count += 1
                        elif char == ')':
                            paren_count -= 1
                        elif char == '[':
                            bracket_count += 1
                        elif char == ']':
                            bracket_count -= 1

                    # 找到有效的分隔符（第一个不在嵌套结构内的分号）
                    if char == ';' and brace_count == 0 and paren_count == 0 and bracket_count == 0 and not in_quotes:
                        semicolon_pos = i
                        break  # 找到第一个有效分号就停止

                if semicolon_pos == -1:
                    # 如果没有找到分号，尝试使用_split_elements_by_semicolon
                    elements = BusCtlTypeConverter._split_elements_by_semicolon(inner_content)
                    if len(elements) >= 2:
                        key_line = elements[0].strip()
                        value_content = '; '.join(elements[1:]).strip()
                    else:
                        continue
                else:
                    # 找到了有效的分号分隔符
                    key_line = inner_content[:semicolon_pos].strip()
                    value_content = inner_content[semicolon_pos + 1:].strip()

                # 处理key和value
                converted_key = BusCtlTypeConverter.dbus_string_to_type(key_line)
                converted_value = BusCtlTypeConverter.dbus_string_to_type(value_content)

                # 确保值不是原始字符串，除非它确实是字符串类型
                if isinstance(converted_value, str):
                    # 检查是否是嵌套的数组或字典格式
                    if converted_value.strip().startswith('ARRAY ') or converted_value.strip().startswith('DICT_ENTRY '):
                        # 尝试再次转换
                        converted_value = BusCtlTypeConverter.dbus_string_to_type(converted_value)

                # 如果转换后的值是空列表，但原始value_content是字典数组格式，应该转换为空字典
                if isinstance(converted_value, list) and len(converted_value) == 0:
                    if value_content.strip().startswith('ARRAY "{'):
                        # 这是空字典数组，应该返回空字典
                        converted_value = {}

                # 确保key不是None
                if converted_key is None:
                    logger.warning(f"无法转换字典key: {key_line}")
                    continue
                result_dict[converted_key] = converted_value

            return result_dict if result_dict else None
        except Exception as e:
            logger.error(f"busctl字典转换错误: {e}", exc_info=True)
            return None

    @staticmethod
    def _extract_dict_entries_with_bracket_balance(value_str):
        """
        提取所有的DICT_ENTRY条目，确保提取完整条目
        使用括号平衡算法处理嵌套结构，正确处理引号内的内容
        """
        result = []
        pos = 0
        while pos < len(value_str):
            # 查找下一个DICT_ENTRY
            dict_entry_start = value_str.find('DICT_ENTRY', pos)
            if dict_entry_start == -1:
                break
            # 从DICT_ENTRY开始查找第一个不在引号内的大括号
            brace_start = -1
            in_quotes = False
            quote_char = None
            for i in range(dict_entry_start, len(value_str)):
                char = value_str[i]
                # 处理引号状态
                if char in ['"', "'"] and (i == 0 or value_str[i - 1] != '\\'):
                    if in_quotes and char == quote_char:
                        in_quotes = False
                        quote_char = None
                    elif not in_quotes:
                        in_quotes = True
                        quote_char = char
                    continue
                # 只在非引号内查找大括号
                if not in_quotes and char == '{':
                    brace_start = i
                    break
            if brace_start == -1:
                pos = dict_entry_start + 10  # 跳过当前DICT_ENTRY，继续查找
                continue
            # 计算括号平衡，正确处理引号
            brace_count = 1
            end_brace_pos = brace_start + 1
            in_quotes = False
            quote_char = None
            while end_brace_pos < len(value_str):
                char = value_str[end_brace_pos]
                # 处理引号状态
                if char in ['"', "'"] and (end_brace_pos == 0 or value_str[end_brace_pos - 1] != '\\'):
                    if in_quotes and char == quote_char:
                        in_quotes = False
                        quote_char = None
                    elif not in_quotes:
                        in_quotes = True
                        quote_char = char
                    end_brace_pos += 1
                    continue
                # 只在非引号内处理大括号
                if not in_quotes:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        # 当括号平衡时，我们找到了匹配的结束大括号
                        if brace_count == 0:
                            break
                end_brace_pos += 1
            # 确保找到了匹配的结束大括号
            if brace_count == 0:
                # 提取完整的DICT_ENTRY条目（包含结束的};）
                # 查找是否还有分号和结束大括号
                if end_brace_pos + 1 < len(value_str) and value_str[end_brace_pos + 1] == ';':
                    dict_entry = value_str[dict_entry_start:end_brace_pos + 2]
                else:
                    dict_entry = value_str[dict_entry_start:end_brace_pos + 1]
                result.append(dict_entry)
                pos = end_brace_pos + 2  # 继续查找下一个DICT_ENTRY
            else:
                # 没有找到匹配的括号，跳过这个DICT_ENTRY
                pos = dict_entry_start + 10
        return result

    @staticmethod
    def _find_matching_brace(text, start_pos):
        """
        查找匹配的结束大括号，处理引号和嵌套括号
        """
        depth = 0
        in_quote = False
        quote_char = None
        for i in range(start_pos, len(text)):
            char = text[i]
            # 处理引号
            if char in ['"', "'"] and (i == 0 or text[i-1] != '\\'):
                if in_quote and char == quote_char:
                    in_quote = False
                elif not in_quote:
                    in_quote = True
                    quote_char = char
                continue
            # 在引号内，跳过括号处理
            if in_quote:
                continue
            # 处理括号
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    return i
        return -1  # 没有找到匹配的括号

    @staticmethod
    def _convert_array_type(value_str):
        """
        转换D-Bus数组类型,不包括字节数组

        Args:
            value_str: 包含数组内容的字符串

        Returns:
            转换后的Python列表对象,如果无法转换则返回None
        """
        # 对于简单的ARRAY格式，使用通用函数提取内容
        if value_str.startswith('ARRAY ') and '{' in value_str:
            elements = BusCtlTypeConverter._extract_and_split_content(value_str, 'ARRAY')
            if elements is None:
                return []
            # 转换每个元素
            converted_elements = []
            for elem in elements:
                converted_elements.append(BusCtlTypeConverter.dbus_string_to_type(elem))
            return converted_elements
        # 对于没有ARRAY关键字的简单花括号格式
        start_brace = value_str.find('{')
        end_brace = value_str.rfind('}')
        if start_brace == -1 or end_brace == -1 or start_brace >= end_brace:
            return []  # 格式不正确，返回空列表
        # 提取大括号内的内容并去除首尾空白
        content = value_str[start_brace + 1:end_brace].strip()
        if not content:
            return []  # 空数组
        # 使用分割函数
        elements = BusCtlTypeConverter._split_elements_by_semicolon(content)
        # 转换每个元素
        converted_elements = []
        for elem in elements:
            converted_elements.append(BusCtlTypeConverter.dbus_string_to_type(elem))
        return converted_elements

    @staticmethod
    def _convert_struct_type(value_str):
        """
        转换D-Bus结构体类型

        Args:
            value_str: 包含结构体内容的字符串，格式为 'STRUCT {...}' 或 'STRUCT "ysss" {...}'

        Returns:
            转换后的Python列表对象，如果无法转换则返回None
        """
        # 使用通用函数提取内容
        elements = BusCtlTypeConverter._extract_and_split_content(value_str, 'STRUCT')
        if elements is None:
            return None

        # 转换每个元素
        converted_elements = []
        for elem in elements:
            converted_elem = BusCtlTypeConverter.dbus_string_to_type(elem)
            if converted_elem is not None:
                converted_elements.append(converted_elem)
        # 返回列表，对应dbus-next中的结构体表示
        return converted_elements

    

    @staticmethod
    def _convert_array_of_bytes(value_str):
        """转换字节数组类型的值"""
        try:
            # 假设输入格式为 "ARRAY "y" { BYTE 1; BYTE 2; BYTE 3; };" 或类似格式
            # 直接提取大括号内的内容
            start_index = value_str.find('{')
            end_index = value_str.rfind('}')
            if start_index == -1 or end_index == -1 or start_index >= end_index:
                # 如果找不到有效格式，尝试处理空数组
                if '{ }' in value_str or '{}' in value_str:
                    return b''
                raise ValueError(f"Invalid byte array format: {value_str}")
            # 提取大括号内的内容，去掉前后空格
            content = value_str[start_index + 1:end_index].strip()
            # 如果内容为空，返回空字节数组
            if not content:
                return b''
            # 按分号分割元素
            elements = [elem.strip() for elem in content.split(';') if elem.strip()]
            # 提取每个BYTE值并转换为整数
            valid_values = []
            for elem in elements:
                # 简化逻辑：使用空格分割并取第二个元素（数字部分）
                parts = elem.split()
                if len(parts) >= 2 and parts[0].upper() == 'BYTE':
                    try:
                        # 直接取空格分割后的第二个部分作为数字
                        byte_value = int(parts[1])
                        # 确保值在有效范围内
                        if 0 <= byte_value <= 255:
                            valid_values.append(byte_value)
                        else:
                            logging.warning(f"Byte value {byte_value} out of range, clamping to 0-255")
                            valid_values.append(max(0, min(255, byte_value)))
                    except ValueError:
                        logging.warning(f"Invalid byte value format: {elem}")
                        valid_values.append(0)
                else:
                    logging.warning(f"Unexpected element format in byte array: {elem}")
                    valid_values.append(0)
            # 转换为bytes对象返回
            return bytes(valid_values)
        except Exception as e:
            logging.error(f"Error converting byte array: {str(e)}")
            return b''

    @staticmethod
    def _extract_and_split_content(value_str, type_name):
        """
        公共函数：提取并分割指定类型的数据结构内容，针对复杂类型（STRUCT、ARRAY），用最外层的;进行分割分割成独立的数据

        Args:
            value_str: 包含数据结构内容的字符串
            type_name: 数据结构类型名称，如'STRUCT'、'ARRAY'

        Returns:
            分割后的元素列表，如果无法提取则返回None
        """
        # 提取大括号内的内容
        content = BusCtlTypeConverter.extract_content_from_type(value_str, type_name)
        if not content:
            return []
        # 使用之前创建的元素分割函数
        return BusCtlTypeConverter._split_elements_by_semicolon(content)
