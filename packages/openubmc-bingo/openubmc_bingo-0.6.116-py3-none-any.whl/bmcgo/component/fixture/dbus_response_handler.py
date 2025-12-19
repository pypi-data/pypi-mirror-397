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
"""
DBus响应处理器 - 专门用于处理DBus响应的工具模块
支持D-Bus中所有基本类型和复杂类型的正确解析和转换
"""
import logging
from copy import deepcopy
from typing import Any, Dict

from bmcgo.component.fixture.busctl_type_converter import BusCtlTypeConverter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



class DBusResponseHandler:
    """
    DBus响应处理器类，提供响应处理和值转换的功能
    支持所有D-Bus标准数据类型
    """
    @staticmethod
    def process_response(response):
        """处理响应并返回适当的结果

        支持的响应类型：
        - method_return: 正常方法返回
        - error: D-Bus 错误响应
        - no_reply: 不发送响应（用于模拟超时）
        - timeout: 模拟超时（等同于 no_reply）
        - interrupt: 模拟中断（发送错误后中断连接）
        - delay: 延迟响应（需要在调用端处理延迟）

        Returns:
            dict: 处理后的响应字典，包含 type、values、signature 等字段
            None: 对于 no_reply、timeout 等不需要响应的类型
        """
        response_type = response.get('type')
        # 处理no_reply类型响应（不发送响应，模拟超时）
        if response_type == 'no_reply':
            logging.info(f'🔇 no_reply: 不发送响应（模拟超时）')
            return {'type': 'no_reply'}
        # 处理timeout类型响应（等同于no_reply）
        if response_type == 'timeout':
            logging.info(f'⏱️ timeout: 模拟超时，不发送响应')
            return {'type': 'timeout'}
        # 处理error类型响应
        if response_type == 'error':
            error_name = response.get('error_name', 'org.freedesktop.DBus.Error.Failed')
            error_message = response.get('error_message', 'Mock error response')
            logging.error(f'❌ 错误响应: {error_name}')
            logging.error(f'   错误详情: {error_message}')
            return {
                'type': 'error',
                'error_name': error_name,
                'error_message': error_message
            }
        # 处理interrupt类型响应（模拟中断）
        if response_type == 'interrupt':
            logging.warning(f'⚠️ interrupt: 模拟中断，发送错误后中断连接')
            return {
                'type': 'interrupt',
                'error_name': response.get('error_name', 'org.freedesktop.DBus.Error.Failed'),
                'error_message': response.get('error_message', 'Connection interrupted')
            }
        # 处理delay类型响应（延迟响应）
        if response_type == 'delay':
            delay_ms = response.get('delay_ms', 0)
            delay_seconds = response.get('delay_seconds', 0)
            actual_delay = delay_seconds if delay_seconds > 0 else (delay_ms / 1000.0 if delay_ms > 0 else 0)
            logging.info(f'⏳ delay: 延迟响应 {actual_delay} 秒')
            # 返回延迟配置和原始响应
            processed = deepcopy(response)
            processed['delay_seconds'] = actual_delay
            return processed
        # 处理method_return类型响应或包含values的响应（兼容没有type字段的情况）
        elif (response.get('type') == 'method_return' or response.get('type') is None) and 'values' in response:
            response_values = response['values']
            logging.info(f'✅ 匹配成功，原始响应值: {response_values}, 类型: {type(response_values)}')
            # 转换响应值为正确的类型
            # mock_data中的values是busctl格式的字符串，需要使用BusCtlTypeConverter
            # 运行时mock中的values可能是Python类型，直接使用
            converted_values = []
            for idx, value in enumerate(response_values):
                logging.info(f'处理响应值[{idx}]: 类型={type(value)}, 值={ \
                    str(value)[:200] if isinstance(value, str) and len(str(value)) > 200 else value}')
                # 如果已经是Python类型（不是字符串，或者是字符串但不是busctl格式），直接使用
                if not isinstance(value, str):
                    # 已经是Python类型（dict, list, int, bool等），直接使用
                    converted_values.append(value)
                    logging.info(f'✅ 值[{idx}] 是Python类型，直接使用: {type(value)}')
                elif isinstance(value, str) and (value.strip().startswith(('STRING ', 'ARRAY ', 'DICT_ENTRY ', \
                        'STRUCT ', 'VARIANT ', 'BYTE ', 'INT16 ', 'UINT16 ', 'INT32 ', 'UINT32 ',\
                        'INT64 ', 'UINT64 ', 'DOUBLE ', 'FLOAT ', 'BOOLEAN ', 'OBJECT_PATH ', 'SIGNATURE ')) \
                        or ('ARRAY "' in value and '{' in value) or ('DICT_ENTRY "' in value and '{' in value) \
                        or ('STRUCT "' in value and '{' in value) or ('VARIANT "' in value)):
                    # busctl格式字符串，需要转换
                    try:
                        converted_value = BusCtlTypeConverter.dbus_string_to_type(value)
                        converted_values.append(converted_value)
                        logging.info(f'✅ 值[{idx}] 是busctl格式，已转换: {type(converted_value)}')
                    except Exception as e:
                        logging.warning(f"使用BusCtlTypeConverter转换失败: {e}，尝试直接使用原始值")
                        converted_values.append(value)
                else:
                    # 普通字符串，检查是否需要JSON解析
                    # 只有明显的JSON格式（以{或[开头）才尝试解析
                    if value.strip().startswith(('{', '[')):
                        try:
                            import json
                            parsed = json.loads(value)
                            converted_values.append(parsed)
                            logging.info(f"✅ 值[{idx}] 是JSON格式，已解析: {type(parsed)}")
                        except Exception as e:
                            # JSON解析失败，直接使用原始字符串
                            logging.info(f"ℹ️ 值[{idx}] JSON解析失败，使用原始字符串: {value[:50]}")
                            converted_values.append(value)
                    else:
                        # 普通字符串（如ID、名称等），直接使用，不需要警告
                        logging.info(f"✅ 值[{idx}] 是普通字符串，直接使用: {value[:50]}")
                        converted_values.append(value)
            logging.info(f'✅ 转换后响应值: {converted_values}, 类型: {[type(v) for v in converted_values]}')
            processed_response: Dict[str, Any] = deepcopy(response)
            processed_response['values'] = converted_values
            return processed_response
        # 其他类型响应
        else:
            logging.info(f'ℹ️ 未处理的响应类型: {response.get("type")}')
            return None
