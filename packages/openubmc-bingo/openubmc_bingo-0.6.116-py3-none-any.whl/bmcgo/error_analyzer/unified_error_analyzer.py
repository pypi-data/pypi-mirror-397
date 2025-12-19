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

import os
import glob
import logging

from .log_parser import LogParser
from .case_matcher import CaseMatcher


class UnifiedErrorAnalyzer:
    """统一的错误分析器 - 结合命令失败和日志分析"""

    def __init__(self, cases):
        self.log_parser = LogParser()
        self.case_matcher = CaseMatcher()
        self.cases = cases

    @staticmethod
    def _find_log_files_in_directory(directory, recursive=True):
        """
        在目录中查找日志文件

        Args:
            directory: 目录路径
            recursive: 是否递归查找子目录
        """
        log_files = []

        if recursive:
            # 递归查找所有 .log 文件
            pattern = os.path.join(directory, "**", "*.log")
            log_files = glob.glob(pattern, recursive=True)
        else:
            # 只查找当前目录下的 .log 文件
            pattern = os.path.join(directory, "*.log")
            log_files = glob.glob(pattern)

        # 也可以查找其他常见的日志文件扩展名
        additional_patterns = [
            os.path.join(directory, "**", "*.log.*"),  # 滚动日志文件
            os.path.join(directory, "**", "*.txt"),  # 文本日志文件
            os.path.join(directory, "**", "*.err"),  # 错误日志文件
        ]

        for pattern in additional_patterns:
            log_files.extend(glob.glob(pattern, recursive=True))

        # 去重并返回
        return list(set(log_files))

    @staticmethod
    def _extract_error_code_from_failure(failure):
        """从失败信息中提取错误代码"""
        error = failure.get("error", "")
        error_type = failure.get("error_type", "")

        # 根据错误类型和内容生成错误代码
        if "TimeoutExpired" in error_type:
            return "COMMAND_TIMEOUT"
        elif "CalledProcessError" in error_type:
            return "COMMAND_FAILED"
        elif "FileNotFoundError" in error_type:
            return "COMMAND_NOT_FOUND"
        elif "PermissionError" in error_type:
            return "PERMISSION_DENIED"
        else:
            return "COMMAND_ERROR"

    @staticmethod
    def _format_failure_log(failure):
        """格式化失败日志"""
        parts = []

        if failure.get("command_key"):
            parts.append(f"[{failure['command_key']}]")

        parts.append(failure["command_str"])
        parts.append("[FAILED]")

        exec_time = failure.get("execution_time", 0)
        parts.append(f"[{exec_time:.2f}s]")

        if "error" in failure:
            parts.append(f"[ERROR: {failure['error']}]")

        return " ".join(parts)

    @staticmethod
    def _deduplicate_cases(cases):
        """案例去重"""
        seen_signatures = set()
        unique_cases = []

        for case in cases:
            # 创建更严格的案例签名
            title = case.get("title", "")

            # 使用原始日志内容（去除ANSI颜色码）进行去重
            raw_log = case["log_data"].get("raw_log", "")

            # 去除ANSI颜色码
            import re

            ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
            clean_log = ansi_escape.sub("", raw_log).strip()

            # 创建基于标题和清理后日志内容的签名
            signature = f"{title}_{hash(clean_log)}"

            if signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_cases.append(case)

        return unique_cases

    @staticmethod
    def _output_unified_case(case, case_number):
        """输出统一格式的案例"""
        source = case["log_data"].get("source", "unknown")
        if source == "log_file":
            source_icon = "📁"
            source_text = "日志文件"
            file_path = case["log_data"].get("file_path", "unknown")
            file_name = file_path
        else:
            source_icon = "🔧"
            source_text = "命令执行"
            file_name = None

        logging.info(
            f"{source_icon} 案例 {case_number}: {case.get('title', '未命名案例')}"
        )
        logging.info("─" * 50)

        logging.info(f"   🕐 发生时间: {case['log_data']['timestamp']}")
        logging.info(f"   📍 来源: {source_text}")

        if file_name:
            logging.info(f"   📄 文件: {file_path}")

        logging.info(f"   📝 问题描述: {case.get('description', '')}")

        if case.get("steps"):
            logging.info("   👣 重现步骤:")
            for j, step in enumerate(case.get("steps", []), 1):
                logging.info(f"      {j}. {step}")

        logging.info("   📄 相关输出:")
        logging.info(f"      {case['log_data']['raw_log']}")

        # 如果是命令失败案例，显示额外信息
        if source == "command_failure" and "command_data" in case:
            cmd_data = case["command_data"]
            logging.info("   🔧 命令详情:")
            logging.info(f"      命令: {cmd_data['command_str']}")
            logging.info(f"      执行时间: {cmd_data['execution_time']:.2f}秒")
            logging.info(f"      错误类型: {cmd_data.get('error_type', 'Unknown')}")

        if case.get("solution"):
            logging.info(f"   💡 解决方案: {case['solution']}")

        logging.info("─" * 50)

    def analyze_errors(self, log_sources, command_failures=None):
        """
        统一分析错误：支持多种日志源

        Args:
            log_sources: 可以是以下类型：
                        - 单个文件路径 (str)
                        - 文件路径列表 (list)
                        - 文件夹路径 (str) - 会分析该文件夹下所有 .log 文件
            command_failures: 命令失败信息列表
        """
        logging.info("\n" + "=" * 60)
        logging.info("🔍 开始统一错误分析")
        logging.info("=" * 60)

        # 解析日志源
        log_files = self._resolve_log_sources(log_sources)

        if not log_files:
            logging.warning("❌ 未找到任何日志文件")
            return []

        all_cases = []
        all_log_entries = []

        # 1. 分析所有日志文件
        for log_file in log_files:
            file_cases, file_entries = self._analyze_single_log_file(log_file)
            all_cases.extend(file_cases)
            all_log_entries.extend(file_entries)

        # 2. 分析命令失败信息
        if command_failures:
            command_cases = self._analyze_command_failures(command_failures)
            all_cases.extend(command_cases)

        # 3. 合并和去重
        unique_cases = self._deduplicate_cases(all_cases)

        # 4. 输出分析结果
        self._output_unified_analysis(
            unique_cases, log_files, command_failures, all_log_entries
        )

        return unique_cases

    def _resolve_log_sources(self, log_sources):
        """
        解析日志源，返回文件路径列表

        Args:
            log_sources: 单个文件路径、文件列表或文件夹路径
        """
        if isinstance(log_sources, str):
            # 单个路径
            if os.path.isfile(log_sources):
                # 单个文件
                return [log_sources]
            elif os.path.isdir(log_sources):
                # 文件夹 - 查找所有 .log 文件
                return self._find_log_files_in_directory(log_sources)
            else:
                # 可能是通配符模式
                return glob.glob(log_sources)

        elif isinstance(log_sources, list):
            # 文件列表
            all_files = []
            for source in log_sources:
                if os.path.isfile(source):
                    all_files.append(source)
                elif os.path.isdir(source):
                    all_files.extend(self._find_log_files_in_directory(source))
                else:
                    # 通配符模式
                    all_files.extend(glob.glob(source))
            return all_files

        else:
            return []

    def _analyze_single_log_file(self, log_file_path):
        """分析单个日志文件"""
        try:
            log_entries = self.log_parser.parse_logs(log_file_path)
            cases = self.cases
            matched_cases = self.case_matcher.match_cases(log_entries, cases)

            # 标记来源文件
            for case in matched_cases:
                case["log_data"]["source"] = "log_file"
                case["log_data"]["file_path"] = log_file_path

            return matched_cases, log_entries

        except Exception as e:
            logging.error(f"  ❌ 分析文件失败 {log_file_path}: {e}")
            return [], []

    def _analyze_command_failures(self, command_failures):
        """分析命令失败信息"""
        cases = self.cases
        matched_cases = []

        for failure in command_failures:
            # 将命令失败信息转换为日志格式进行分析
            log_entry = self._convert_failure_to_log_entry(failure)

            # 匹配案例
            case = self.case_matcher.find_matching_case(log_entry, cases)
            if case:
                enriched_case = self.case_matcher.enrich_case_with_log(case, log_entry)
                enriched_case["command_data"] = failure  # 保留原始命令数据
                matched_cases.append(enriched_case)

        return matched_cases

    def _convert_failure_to_log_entry(self, failure):
        """将命令失败信息转换为日志条目格式"""
        return {
            "timestamp": failure["timestamp"],
            "level": "ERROR",
            "module": "CommandExecutor",
            "message": f"Command failed: {failure['command_str']} - {failure['error']}",
            "error_code": self._extract_error_code_from_failure(failure),
            "parameters": {
                "command": failure["command_str"],
                "execution_time": failure["execution_time"],
                "error_type": failure["error_type"],
            },
            "raw_line": self._format_failure_log(failure),
            "source": "command_failure",
        }

    def _load_cases(self):
        """加载案例模板"""
        import yaml

        try:
            with open(self.case_file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data.get("cases", [])
        except Exception as e:
            logging.error(f"❌ 加载案例文件失败: {e}")
            return []

    def _output_unified_analysis(
        self, cases, log_files, command_failures, all_log_entries
    ):
        """输出统一分析结果"""
        if not cases:
            logging.warning("\n✅ 没有发现匹配的错误案例")
            return

        # 统计信息
        log_cases = [c for c in cases if c["log_data"].get("source") == "log_file"]
        command_cases = [
            c
            for c in cases
            if c["log_data"].get("source") == "command_failure"
        ]

        # 按文件统计
        file_stats = {}
        for case in log_cases:
            file_path = case["log_data"].get("file_path", "unknown")
            file_stats[file_path] = file_stats.get(file_path, 0) + 1

        logging.info(f"   📊 统一分析完成!")
        logging.info(f"   分析文件数量: {len(log_files)} 个")
        logging.info(f"   日志条目总数: {len(all_log_entries)} 条")
        logging.info(f"   日志文件案例: {len(log_cases)} 个")
        logging.info(f"   命令失败案例: {len(command_cases)} 个")
        logging.info(f"   总案例: {len(cases)} 个")

        if command_failures:
            logging.info(f"   分析的命令失败: {len(command_failures)} 个")

        # 输出所有案例
        logging.info("\n" + "=" * 60)
        logging.info("📋 详细错误分析")
        logging.info("=" * 60)

        for i, case in enumerate(cases, 1):
            self._output_unified_case(case, i)
