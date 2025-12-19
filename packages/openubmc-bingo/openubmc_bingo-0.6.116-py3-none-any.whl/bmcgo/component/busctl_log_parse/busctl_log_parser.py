#!/usr/bin/python3
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
解析BMC录制的日志文件，提取 bmc.* 服务的内容，包括方法请求和响应，信号
并将其保存为 mock_data.json，用于 Mock 服务器。
"""
import sys
import re
import os
import shutil
import logging
from bmcgo.errors import BmcGoException
from bmcgo.component.busctl_log_parse.mock_data_save import MockDataSaver
from bmcgo.component.busctl_log_parse.test_data_save import TestDataSave

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# --- 配置 ---#
DEFAULT_SERVICE_PREFIX = "bmc."


class BusCtlLogParser:
    """
    DBus日志解析器，用于解析dbus-monitor日志中的方法调用、返回和错误。
    该类封装了所有解析逻辑，并为未来的信号处理留下了扩展点。
    """
    # 在类的初始化方法中添加 signal 相关的状态变量
    def __init__(self, test_service=None):
        self.service_prefix = DEFAULT_SERVICE_PREFIX
        # 保存mock数据，用于打桩
        self.mock_data = {}
        # 保存测试数据，用于生成用例
        self.test_data = []
        self.test_service = test_service
        # 中间辅助变量
        self.pending_calls = {}
        self.current_req_rsp_obj = None
        # Method Call 相关状态变量
        self.current_call = None
        self.current_args = []
        self.current_arg_lines = []
        self.in_arg_collection = False
        self.bracket_balance = 0
        self.expecting_empty_close = False  # 标记是否期望空消息的结束
        # Method Return 相关状态变量
        self.current_return_values = None
        self.current_return_lines = []
        self.in_return_collection = False
        self.return_bracket_balance = 0
        # Signal 相关状态变量
        self.signals = []
        self.current_signal = None
        self.current_signal_args = []
        self.current_signal_lines = []
        self.in_signal_collection = False
        self.signal_bracket_balance = 0

    @staticmethod
    def process_signal_line(line):
        """
        处理 signal 行，提取其中的信息

        :param line: 日志中的 signal 行
        :return: 解析后的 signal 信息字典
        """
        # 修改正则表达式，支持跨行匹配（允许换行和空格）
        # 将多行合并为单行进行匹配
        normalized_line = ' '.join(line.split())
        type_pattern = (
            r'Type=signal\s+Endian=\w\s+Flags=\d+\s+Version=\d+\s+'
            r'Cookie=(\d+)\s+'
            r'Timestamp="([^"]+)"\s+'
            r'Sender=([^\s]+)'
            r'(?:\s+Destination=[^\s]+)?\s+'
            r'Path=([^\s]+)\s+'
            r'Interface=([^\s]+)\s+'
            r'Member=([^\s]+)'
        )
        call_match = re.search(type_pattern, normalized_line)
        if not call_match:
            return None
        # 只提取需要的字段
        cookie, timestamp, sender, path, iface, member = call_match.groups()
        serial = int(cookie)
        # 创建 signal 对象
        signal_obj = {
            'type': 'signal',
            'timestamp': timestamp,
            'sender': sender,
            'path': path,
            'interface': iface,
            'member': member,
            'cookie': serial,
            'content': []
        }
        return signal_obj

    @staticmethod
    def needs_more_lines(line):
        """
        检查一行参数是否需要更多行来完成
        通过括号平衡来判断是否需要继续收集

        :param line: 当前行文本
        :return: True 如果需要更多行，False 否则
        """
        # 计算括号平衡
        bracket_balance = 0
        for char in line:
            if char in '{[(':  # 开括号
                bracket_balance += 1
            elif char in '}])':  # 闭括号
                bracket_balance -= 1
        # 如果括号不平衡，需要更多行
        if bracket_balance != 0:
            return True
        array_contain = line.split('array [')[1]
        dict_contain = line.split('dict entry(')[1]
        flag_array_contain = 'array [' in line and ']' not in array_contain
        flag_dict_contain = 'dict entry(' in line and ')' not in dict_contain
        # 检查是否是复杂结构的开始但还没结束
        if flag_array_contain or flag_dict_contain:
            return True
        return False

    @staticmethod
    def _process_indented_lines(stripped_line, current_lines, args_or_values, current_balance):
        """
        通用处理缩进文本行的函数，统一处理method call的参数和method return的返回值

        :param stripped_line: 去除缩进后的行文本
        :param current_lines: 当前收集的行列表
        :param args_or_values: 存储完成参数/返回值的列表
        :param current_balance: 当前括号平衡状态
        :return: 更新后的括号平衡状态
        """
        # 特殊处理XML字符串 - 检查是否已经在处理包含XML内容的参数
        is_handling_xml = (current_lines and
                         any(line.startswith('string "<!DOCTYPE') or
                             line.startswith('STRING "<!DOCTYPE') for line in current_lines))
        stripped_clean = stripped_line.strip()
        # 当括号平衡为0且遇到独立的 "};" 时，这通常是 REQ_MESSAGE 的闭合标记，不应作为参数内容保存
        if stripped_clean == '};' and current_balance == 0 and not is_handling_xml:
            return current_balance
        # 判断是否是新参数/返回值的开始：
        # 1. 当前参数已经加了一些行
        # 2. 当前括号平衡为0（表示上一个参数已经完整）
        # 3. 当前行看起来像是新参数的开始（以类型关键字开头）
        # 4. 不是XML内容
        # 5. 当前行不是单纯的 };（这可能是 REQ_MESSAGE 或 RSP_MESSAGE 的结束）
        is_new_param_start = (
            stripped_line and
            stripped_clean != '};' and  # 排除单纯的 };，这可能是消息的结束
            (stripped_line.startswith('ARRAY ') or
             stripped_line.startswith('STRING ') or
             stripped_line.startswith('INT32 ') or
             stripped_line.startswith('INT64 ') or
             stripped_line.startswith('UINT32 ') or
             stripped_line.startswith('UINT64 ') or
             stripped_line.startswith('DOUBLE ') or
             stripped_line.startswith('BOOLEAN ') or
             stripped_line.startswith('BYTE ') or
             stripped_line.startswith('VARIANT ') or
             stripped_line.startswith('DICT_ENTRY ') or
             stripped_line.startswith('STRUCT ') or
             stripped_line.startswith('OBJECT_PATH '))
        )
        flag_current_lines = current_lines and current_balance == 0
        if flag_current_lines and is_new_param_start and not is_handling_xml:
            # 如果是新参数/返回值且当前有未完成的，先保存
            args_or_values.append('\n'.join(current_lines))
            current_lines.clear()
        current_lines.append(stripped_line)
        # 更新括号平衡
        new_balance = current_balance
        for char in stripped_line:
            if char in '{[(':  # 开括号
                new_balance += 1
            elif char in '}])':  # 闭括号
                new_balance -= 1
        return new_balance

    @staticmethod
    def _extract_pattern(text, pattern):
        match = re.search(pattern, text)
        return match.group(1) if match else None

    @staticmethod
    def _detect_block_type(block_lines):
        """
        检测块类型：方法或信号
        优先检查 Type=signal，因为信号也可能包含 'method' 字符串
        """
        # 只检查前3行，因为 Type= 总是紧挨在 monitor_app: 的下一行
        for line in block_lines[:3]:
            if 'Type=signal' in line:
                return 'signal'
            if 'Type=method' in line:
                return 'method'
        return None

    @staticmethod
    def _collect_header_text(block_lines, terminators):
        header_parts = []
        for line in block_lines[1:]:
            stripped = line.strip()
            if any(stripped.startswith(term) for term in terminators):
                break
            if stripped:
                header_parts.append(stripped)
        return ' '.join(header_parts)

    @staticmethod
    def _collect_brace_block(lines, start_idx):
        """
        收集从 start_idx 行开始的 { ... } 块，包含起始与结束行。
        """
        collected = []
        brace_balance = 0
        started = False
        for idx in range(start_idx, len(lines)):
            line = lines[idx]
            collected.append(line)
            delta = BusCtlLogParser._brace_delta(line)
            brace_balance += delta
            if ('{' in line) and not started:
                started = True
            if started and brace_balance == 0:
                return collected, idx
        return collected, len(lines) - 1

    @staticmethod
    def _split_top_level_entries(inner_lines):
        entries = []
        current = []
        brace_balance = 0

        for line in inner_lines:
            if not line.strip() and not current:
                continue
            current.append(line)
            brace_balance += BusCtlLogParser._brace_delta(line)
            if brace_balance == 0:
                entry = '\n'.join(current).strip()
                if entry:
                    entries.append(entry)
                current = []
        if current:
            entry = '\n'.join(current).strip()
            if entry:
                entries.append(entry)
        return entries

    @staticmethod
    def _brace_delta(line):
        delta = 0
        in_quote = False
        quote_char = ''
        i = 0
        while i < len(line):
            ch = line[i]
            if ch in ("'", '"'):
                if not in_quote:
                    in_quote = True
                    quote_char = ch
                elif quote_char == ch:
                    in_quote = False
                    quote_char = ''
                i += 1
                continue
            if not in_quote:
                if ch == '{':
                    delta += 1
                elif ch == '}':
                    delta -= 1
            i += 1
        return delta

    def parse_method_calls_and_responses(self, log_file_path):
        """
        解析日志文件中的方法调用、响应与信号。
        采用块级解析方式：每个 monitor_app: 开头的块被视作一个独立的 Method 或 Signal。
        """
        self.mock_data = {}
        self.signals = []
        method_calls_count = 0
        signals_count = 0
        current_block = []
        total_blocks = 0
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for raw_line in f:
                line = raw_line.rstrip('\n')
                if line.startswith('monitor_app:'):
                    if current_block:
                        if self._process_block(current_block):
                            block_type = self._detect_block_type(current_block)
                            if block_type == 'method':
                                method_calls_count += 1
                            elif block_type == 'signal':
                                signals_count += 1
                            total_blocks += 1
                        current_block = []
                    current_block.append(line)
                else:
                    if current_block:
                        current_block.append(line)
            # 处理最后一个块
            if current_block:
                if self._process_block(current_block):
                    block_type = self._detect_block_type(current_block)
                    if block_type == 'method':
                        method_calls_count += 1
                    elif block_type == 'signal':
                        signals_count += 1
                    total_blocks += 1
        logging.info(
            f"✅ 解析完成: 块数={total_blocks} | 方法={method_calls_count} | 信号={signals_count} | "
            f"Mock条目={sum(len(v) for v in self.mock_data.values())}"
        )
        return self.mock_data

    def parse_dbus_log(self, log_file_path, output_dir_path):
        """
        解析标准 dbus-monitor 日志文件并生成 Mock 数据。

        :param log_file_path: dbus-monitor 日志文件路径
        :param output_dir_path: 输出目录路径
        """
        try:
            # 创建输出目录（如果不存在）
            os.makedirs(output_dir_path, exist_ok=True)
            # 清理 mock_data 和 test_data 目录（如果存在）
            mock_data_dir = os.path.join(output_dir_path, 'mock_data')
            test_data_dir = os.path.join(output_dir_path, 'test_data')
            if os.path.exists(mock_data_dir):
                shutil.rmtree(mock_data_dir)
            if os.path.exists(test_data_dir):
                shutil.rmtree(test_data_dir)
            # 获取目录中所有文件并排序
            log_files = []
            for root, _, files in os.walk(log_file_path):
                for file in files:
                    if file.endswith('.log'):  # 只处理.log文件
                        log_files.append(os.path.join(root, file))
            # 按文件名排序，确保按顺序处理
            log_files.sort()
            if not log_files:
                logging.warning(f"警告: 目录 {log_file_path} 中没有找到.log文件")
                return
            logging.info(f"  找到 {len(log_files)} 个日志文件")
            # 解析方法调用和响应
            logging.info("解析方法调用和响应...")
            # 重新创建目录（之前已清理）
            os.makedirs(test_data_dir, exist_ok=True)
            os.makedirs(mock_data_dir, exist_ok=True)
            for log_file in log_files:
                logging.info(f"处理文件: {log_file}")
                # 解析当前文件
                self.parse_method_calls_and_responses(log_file)
                if self.mock_data:
                    # 保存mock数据和signal数据,由于数据量可能比较大，分开批量处理
                    mock_data_saver = MockDataSaver(self.service_prefix)
                    mock_data_saver.save_mock_data(self.mock_data, mock_data_dir)
            # 保存测试数据，一次性保存
            if self.test_data:
                test_data_saver = TestDataSave(self.test_data, output_dir_path)
                test_data_saver.save()
        except FileNotFoundError:
            raise BmcGoException(f"错误: 找不到日志文件 {log_file_path}") from e
        except Exception as e:
            raise BmcGoException(f"解析日志时出错: {e}") from e

    def process_method_call(self, line):
        """
        处理方法调用行，提取调用信息。

        :param line: 日志中的方法调用行
        :return: 包含调用信息的字典，如果不是目标服务则返回None
        """
        type_pattern = (
            r'Type=method\s+'
            r'Endian=\w\s+'
            r'Flags=\d+\s+'
            r'Version=\d+\s+'
            r'Cookie=(\d+)\s+'
            r'Timestamp="([^"]+)"\s+'
            r'Sender=([^\s]+)\s+'
            r'Destination=([^\s]+)\s+'
            r'Path=([^\s]+)\s+'
            r'Interface=([^\s]+)\s+'
            r'Member=([^\s]+)'
        )
        call_match = re.search(type_pattern, line)
        if not call_match:
            return None
        cookie, timestamp, sender, dest, path, iface, member = call_match.groups()
        serial = int(cookie)
        # 检查 destination 是否是需要关注的服务
        is_target_service = False
        if dest.startswith(self.service_prefix):
            is_target_service = True
        if not is_target_service:
            # 不是我们关心的服务调用，跳过
            return None
        return {
            "type": "method_call",
            "timestamp": timestamp,
            "sender": sender,
            "destination": dest,
            "path": path,
            "interface": iface,
            "member": member,
            "cookie": serial,
            "args": []
        }

    def process_method_return(self, line):
        """
        处理方法返回行，将返回与调用匹配。

        :param line: 日志中的方法返回行
        :return: 响应值收集状态，如果需要收集响应值则返回(reply_serial, response_obj)，否则返回None
        """
        # 提取signatural到RESP_MESSAGE=之间的内容
        sig_match = re.search(r'RSP_MESSAGE\s+"([^"]*)"', line)
        signature = ''  # 初始化为空字符串
        if sig_match:
            signature = sig_match.group(1)
        original_call = self.current_call
        response_obj = {
            "request": original_call,
            "response": {
                "type": "method_return",
                "signature": signature,
                "values": []  # 用于存储响应值
            }
        }
        # 不立即添加到mock_data，等待收集响应值
        return response_obj

    def process_remaining_calls(self):
        """
        处理未匹配到返回的调用，视为超时或无响应。

        :return: None
        """
        for call_data in self.pending_calls.values():
            key_dest = call_data['destination']
            key = f"{key_dest}|{call_data['path']}|{call_data['interface']}|{call_data['member']}"
            if key not in self.mock_data:
                self.mock_data[key] = []
            self.mock_data[key].append({
                "request": call_data,
                "response": {"type": "no_reply"}
            })

    def _handle_signal_line(self, line):
        """
        处理 signal 行

        :param line: 日志中的 signal 行
        :return: signal 对象，如果解析成功则返回，否则返回 None
        """
        # 如果之前有未完成的 signal，先保存
        if self.current_signal:
            self._finalize_signal_collection()
        self.current_signal = BusCtlLogParser.process_signal_line(line)
        signal_result = self.current_signal  # 保存返回值用于统计
        if self.current_signal:
            self.current_signal_args = []
            self.current_signal_lines = []
            self.in_signal_collection = True
            self.signal_bracket_balance = 0
        else:
            self.current_signal = None
            self.in_signal_collection = False
        return signal_result  # 返回 signal 对象用于统计

    def _process_signal_arg_lines(self, stripped_line):
        """
        处理 signal 参数的后续行

        :param stripped_line: 去除缩进后的行文本
        """
        # 使用与调用参数相同的处理逻辑来解析缩进的文本行
        new_balance = BusCtlLogParser._process_indented_lines(
            stripped_line,
            self.current_signal_lines,
            self.current_signal_args,
            self.signal_bracket_balance
        )
        # 更新类中的括号平衡状态
        self.signal_bracket_balance = new_balance

    def _finalize_signal_collection(self):
        """
        当遇到非缩进行时，如果有未完成的参数收集，则完成 signal 收集
        只添加以service_prefix开头的信号
        """
        if not self.current_signal:
            return
        # 保存最后一个参数
        if self.current_signal_lines:
            self.current_signal_args.append('\n'.join(self.current_signal_lines))
        # 将收集的参数赋值给 content（保留完整内容，不删除任何结尾）
        self.current_signal['content'] = self.current_signal_args
        self.signals.append(self.current_signal)
        self.test_data.append(self.current_signal)
        # 重置状态 - 使用函数调用替代直接重置
        self._reset_signal_state()

    def _reset_signal_state(self):
        """
        重置signal相关的状态变量
        """
        self.current_signal = None
        self.current_signal_args = []
        self.current_signal_lines = []
        self.in_signal_collection = False
        self.signal_bracket_balance = 0

    def _process_block(self, block_lines):
        if not block_lines:
            return False
        block_type = self._detect_block_type(block_lines)
        if block_type == 'method':
            response_obj = self._process_method_block(block_lines)
            if response_obj:
                self._save_req_rsp_obj(response_obj)
                return True
        elif block_type == 'signal':
            signal_obj = self._process_signal_block(block_lines)
            if signal_obj:
                self.signals.append(signal_obj)
                self.test_data.append(signal_obj)
                return True
        return False

    def _process_method_block(self, block_lines):
        """
        处理方法块：提取方法调用的请求和响应
        注意：信号不应该有 REQ_MESSAGE 和 RSP_MESSAGE，只有 MESSAGE
        """
        # 再次确认这是方法块，不是信号块
        block_type = self._detect_block_type(block_lines)
        if block_type != 'method':
            return None
        header_text = self._collect_header_text(block_lines, terminators=('REQ_MESSAGE',))
        call_info = self._parse_method_header(header_text)
        if not call_info:
            return None
        req_signature, req_entries = self._extract_section_entries(block_lines, 'REQ_MESSAGE')
        rsp_signature, rsp_entries = self._extract_section_entries(block_lines, 'RSP_MESSAGE')
        call_info['signature'] = req_signature or ''
        call_info['args'] = req_entries
        response_obj = {
            'request': call_info,
            'response': {
                'type': 'method_return',
                'signature': rsp_signature or '',
                'values': rsp_entries
            }
        }
        return response_obj

    def _process_signal_block(self, block_lines):
        """
        处理信号块：提取信号的内容
        注意：信号只有 MESSAGE，没有 REQ_MESSAGE 和 RSP_MESSAGE
        """
        # 再次确认这是信号块，不是方法块
        block_type = self._detect_block_type(block_lines)
        if block_type != 'signal':
            return None
        header_text = self._collect_header_text(block_lines, terminators=('MESSAGE',))
        signal_info = self._parse_signal_header(header_text)
        if not signal_info:
            return None
        message_signature, message_entries = self._extract_section_entries(block_lines, 'MESSAGE')
        signal_info['signature'] = message_signature or ''
        signal_info['content'] = message_entries
        return signal_info

    def _parse_method_header(self, header_text):
        if not header_text:
            return None
        data = {
            'type': 'method_call',
            'timestamp': self._extract_pattern(header_text, r'Timestamp="([^"]+)"') or '',
            'sender': self._extract_pattern(header_text, r'Sender=([^\s]+)') or '',
            'destination': self._extract_pattern(header_text, r'Destination=([^\s]+)') or '',
            'path': self._extract_pattern(header_text, r'Path=([^\s]+)') or '',
            'interface': self._extract_pattern(header_text, r'Interface=([^\s]+)') or '',
            'member': self._extract_pattern(header_text, r'Member=([^\s]+)') or '',
            'cookie': int(self._extract_pattern(header_text, r'Cookie=(\d+)') or 0),
            'args': []
        }
        if not data['destination'].startswith(self.service_prefix):
            return None
        return data

    def _parse_signal_header(self, header_text):
        if not header_text:
            return None
        return {
            'type': 'signal',
            'timestamp': self._extract_pattern(header_text, r'Timestamp="([^"]+)"') or '',
            'sender': self._extract_pattern(header_text, r'Sender=([^\s]+)') or '',
            'path': self._extract_pattern(header_text, r'Path=([^\s]+)') or '',
            'interface': self._extract_pattern(header_text, r'Interface=([^\s]+)') or '',
            'member': self._extract_pattern(header_text, r'Member=([^\s]+)') or '',
            'cookie': int(self._extract_pattern(header_text, r'Cookie=(\d+)') or 0),
        }

    def _extract_section_entries(self, block_lines, section_keyword):
        """
        提取 REQ_MESSAGE / RSP_MESSAGE / MESSAGE 内容，并拆分为顶层条目列表。
        """
        signature = ''
        start_idx = None
        for idx, line in enumerate(block_lines):
            stripped = line.strip()
            if stripped.startswith(section_keyword):
                start_idx = idx
                signature = self._extract_pattern(stripped, fr'{section_keyword}\s+"([^"]*)"') or ''
                break
        if start_idx is None:
            return signature, []
        section_lines, end_idx = self._collect_brace_block(block_lines, start_idx)
        if not section_lines:
            return signature, []
        # 去掉起始行和最终的包裹行，仅保留内部内容
        inner_lines = section_lines[1:-1] if len(section_lines) >= 2 else []
        entries = self._split_top_level_entries(inner_lines)
        return signature, entries

    def _reset_return_state(self):
        """
        重置method return相关的状态变量
        """
        self.current_call = None
        self.current_return_values = None
        self.current_return_lines = []
        self.in_return_collection = False
        self.return_bracket_balance = 0
        self.current_req_rsp_obj = None

    def _process_return_value_lines(self, stripped_line):
        """
        处理响应值的后续行

        :param stripped_line: 去除缩进后的行文本
        """
        stripped_clean = stripped_line.strip()
        # 如果当前返回体已经结束（遇到RSP_MESSAGE的闭合标记），提前完成收集
        if stripped_clean == '};' and self.return_bracket_balance == 0:
            if self.in_return_collection:
                self._finalize_return_collection()
            return

        # 直接传递当前的括号平衡状态，接收返回的结果和新的平衡状态
        new_balance = BusCtlLogParser._process_indented_lines(
            stripped_line,
            self.current_return_lines,
            self.current_return_values,
            self.return_bracket_balance
        )
        # 更新类中的括号平衡状态
        self.return_bracket_balance = new_balance

    def _finalize_return_collection(self):
        """
        完成DBus方法返回值的收集和处理，将完整的请求-响应对保存到mock_data中。
        """
        # 处理可能剩余的返回值
        if self.current_return_lines:
            self.current_return_values.append('\n'.join(self.current_return_lines))
            self.current_return_lines = []
        response_obj = self.current_req_rsp_obj
        if response_obj:
            self._save_req_rsp_obj(response_obj)
        self._reset_return_state()

    def _save_req_rsp_obj(self, response_obj):
        """
        保存请求-响应对象到mock_data和test_data

        Args:
            response_obj: 请求-响应对象
        """
        if not response_obj:
            return
        key_dest = response_obj['request']['destination']
        key = (
            f"{key_dest}|{response_obj['request']['path']}|"
            f"{response_obj['request']['interface']}|"
            f"{response_obj['request']['member']}"
        )
        should_save_test_data = self.test_service and self.test_service == key_dest
        should_save_mock_data = not self.test_service or self.test_service != key_dest
        if should_save_mock_data:
            if key not in self.mock_data:
                self.mock_data[key] = []
            self.mock_data[key].append(response_obj)

        if should_save_test_data:
            self.test_data.append(response_obj)

    def _handle_method_return_line(self, line):
        """
        处理method return行

        :param line: 日志中的method return行
        """
        response_obj = self.process_method_return(line)
        if response_obj:
            self.current_req_rsp_obj = response_obj
            self.current_return_values = response_obj['response']['values']
            self.in_return_collection = True
            self.current_return_lines = []
            self.return_bracket_balance = 0

    def _reset_call_state(self):
        """
        重置method call相关的状态变量
        """
        self.current_args = []
        self.current_arg_lines = []
        self.in_arg_collection = False
        self.bracket_balance = 0
        self.expecting_empty_close = False

    def _process_call_arg_lines(self, stripped_line):
        """
        处理调用参数的后续行

        :param stripped_line: 去除缩进后的行文本
        """
        # 直接传递当前的括号平衡状态，接收返回的结果和新的平衡状态
        new_balance = BusCtlLogParser._process_indented_lines(
            stripped_line,
            self.current_arg_lines,
            self.current_args,
            self.bracket_balance
        )
        # 更新类中的括号平衡状态
        self.bracket_balance = new_balance

    def _finalize_call_collection(self):
        """
        当遇到非缩进行时，如果有未完成的参数收集，则完成调用
        确保所有参数行（包括最后的 };）都被完整保存
        """
        # 保存最后一个参数（包括所有行，不删除任何内容）
        if self.current_arg_lines:
            # 确保所有行都被保存，包括可能的空行和结尾的 };
            param_text = '\n'.join(self.current_arg_lines)
            if param_text.strip():  # 只有当参数不为空时才添加
                self.current_args.append(param_text)
        self.current_call["args"] = self.current_args
        self._reset_call_state()

    def _handle_method_call_line(self, line):
        """
        处理method call行

        :param line: 日志中的method call行
        """
        # 如果上一个 call 还没结束，则保存
        if self.current_call:
            if self.in_arg_collection and self.current_arg_lines:
                # 保存最后一个参数
                self.current_args.append('\n'.join(self.current_arg_lines))
                self.current_arg_lines = []
            self.current_call["args"] = self.current_args
            # 如果上一个调用没有响应，创建一个空的响应对象
            if self.in_arg_collection or not self.current_req_rsp_obj:
                # 创建一个只有请求没有响应的对象（可能日志中没有响应）
                response_obj = {
                    'request': self.current_call.copy(),
                    'response': {
                        'type': 'method_return',
                        'signature': self.current_call.get('signature', ''),
                        'values': []
                    }
                }
                self._save_req_rsp_obj(response_obj)
            # 重置状态
            self._reset_call_state()
        self.current_call = self.process_method_call(line)
        call_result = self.current_call  # 保存返回值用于统计
        if self.current_call:
            self.current_args = []
            self.current_arg_lines = []
            self.in_arg_collection = True
            self.bracket_balance = 0
        else:
            self.current_call = None
            self.in_arg_collection = False
        return call_result  # 返回 call 对象用于统计
