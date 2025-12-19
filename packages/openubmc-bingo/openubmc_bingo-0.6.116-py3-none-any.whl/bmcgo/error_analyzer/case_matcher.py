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


class CaseMatcher:
    def __init__(self):
        self.rules = self.load_matching_rules()

    @staticmethod
    def fill_template(template, log_entry):
        """填充模板中的占位符"""
        import re

        def replace_placeholder(match):
            placeholder = match.group(1)
            if placeholder.startswith("log."):
                path = placeholder[4:].split(".")
                value = log_entry
                for key in path:
                    if isinstance(value, dict):
                        value = value.get(key, "")
                    else:
                        value = getattr(value, key, "")
                return str(value)
            return match.group(0)

        return re.sub(r"\{\{(\w+(?:\.\w+)*)\}\}", replace_placeholder, template)

    @staticmethod
    def load_matching_rules():
        """加载匹配规则（可扩展）"""
        return {}

    @staticmethod
    def check_single_rule(log_entry, rule):
        """检查单个匹配规则"""
        field = rule["field"]
        operator = rule["operator"]
        value = rule["value"]

        log_value = log_entry.get(field, "")

        if operator == "equals":
            return log_value == value
        elif operator == "contains":
            return value in str(log_value)
        elif operator == "regex":
            import re

            return bool(re.search(value, str(log_value)))

        return False

    def match_cases(self, log_entries, cases):
        """将日志条目与案例模板匹配"""
        matched_cases = []

        for log_entry in log_entries:
            case = self.find_matching_case(log_entry, cases)
            if case:
                matched_case = self.enrich_case_with_log(case, log_entry)
                matched_cases.append(matched_case)

        return matched_cases

    def find_matching_case(self, log_entry, cases):
        """根据规则找到匹配的案例模板"""
        for case in cases:
            if self.matches_rule(log_entry, case):
                return case
        return None

    def matches_rule(self, log_entry, case_template):
        """检查日志是否匹配案例规则"""
        rules = case_template.get("matching_rules", [])

        for rule in rules:
            if not self.check_single_rule(log_entry, rule):
                return False
        return True

    def enrich_case_with_log(self, case_template, log_entry):
        """用日志信息丰富案例内容"""
        enriched_case = case_template.copy()

        enriched_case["log_data"] = {
            "timestamp": log_entry["timestamp"],
            "parameters": log_entry["parameters"],
            "raw_log": log_entry["raw_line"],
            "line_number": log_entry["line_number"],
        }

        # 替换模板中的占位符
        if "description" in enriched_case:
            enriched_case["description"] = self.fill_template(
                enriched_case["description"], log_entry
            )

        if "steps" in enriched_case:
            enriched_case["steps"] = [
                self.fill_template(step, log_entry)
                for step in enriched_case["steps"]
            ]

        return enriched_case
