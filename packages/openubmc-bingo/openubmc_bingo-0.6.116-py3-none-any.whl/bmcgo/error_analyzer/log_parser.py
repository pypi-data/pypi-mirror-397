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

import logging


class LogParser:
    @staticmethod
    def extract_timestamp(log_line):
        """提取时间戳"""
        import re

        # 匹配常见的时间戳格式
        patterns = [
            r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
            r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}",
        ]
        for pattern in patterns:
            match = re.search(pattern, log_line)
            if match:
                return match.group()
        return "未知时间"

    @staticmethod
    def extract_log_level(log_line):
        """提取日志级别"""

        levels = ["ERROR", "WARN", "WARNING", "INFO", "DEBUG", "FATAL", "Exception"]
        for level in levels:
            if level in log_line.upper():
                return level
        return "UNKNOWN"

    @staticmethod
    def extract_module(log_line):
        """提取模块名"""
        import re

        # 匹配 [ModuleName] 格式
        pattern = r"\[([^\]]+)\]"
        match = re.search(pattern, log_line)
        return match.group(1) if match else "未知模块"

    @staticmethod
    def extract_message(log_line):
        """提取主要消息"""
        return log_line.strip()

    @staticmethod
    def extract_error_code(log_line):
        """提取错误代码"""
        import re

        pattern = r"[A-Z]+_\d{3,}"
        match = re.search(pattern, log_line)
        return match.group() if match else "UNKNOWN"

    @staticmethod
    def extract_parameters(log_line):
        """提取日志中的参数"""
        parameters = {}
        import re

        pattern = r"(\w+)=([^,\s]+)"
        matches = re.findall(pattern, log_line)
        for key, value in matches:
            parameters[key] = value
        return parameters

    def parse_logs(self, file_path):
        """解析错误日志文件"""
        log_entries = []
        seen_logs = set()  # 用于去重的集合

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    entry = self.parse_log_entry(line, line_num)
                    if entry:
                        # 去除颜色码并标准化日志内容
                        import re

                        ansi_escape = re.compile(
                            r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])"
                        )
                        clean_log = ansi_escape.sub("", entry["raw_line"]).strip()

                        # 检查是否已经处理过相同的日志
                        if clean_log not in seen_logs:
                            seen_logs.add(clean_log)
                            log_entries.append(entry)
        except FileNotFoundError:
            logging.warning(f"❌ 日志文件不存在: {file_path}")
        except Exception as e:
            logging.error(f"❌ 读取日志文件失败: {e}")

        return log_entries

    def parse_log_entry(self, log_line, line_num):
        """解析单条日志记录"""
        try:
            # 跳过空行
            if not log_line.strip():
                return None

            entry = {
                "timestamp": self.extract_timestamp(log_line),
                "level": self.extract_log_level(log_line),
                "module": self.extract_module(log_line),
                "message": self.extract_message(log_line),
                "error_code": self.extract_error_code(log_line),
                "parameters": self.extract_parameters(log_line),
                "raw_line": log_line.strip(),
                "line_number": line_num,
            }
            return entry
        except Exception as e:
            logging.error(f"⚠️  解析日志行 {line_num} 失败: {e}")
            return None
