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
根据 busctl 录制的 test_data.json 自动生成 Robot 测试用例。

当前版本采用"数据-用例分离"策略：
- 录制数据始终保留在 test_data.json 中；
- 生成的 Python 关键字只包含回放逻辑，执行时按 case 序号动态解析数据；
- Robot 用例仅串联关键字，便于维护与扩展。

使用方式：python auto_case_generator.py \
  --bmc-test-db-dir /opt/code/network_adapter/temp/opt/bmc/it_test/bmc_test_db \
  --test-db-name network_adapter_y \
  --fixture-dir /opt/code/network_adapter/temp/opt/bmc/it_test/fixture

生成的用例文件会输出到当前执行命令的目录（工作目录）。
"""
from __future__ import annotations
import argparse
import json
import re
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Sequence
from bmcgo.errors import BmcGoException

REPO_ROOT = Path(__file__).resolve().parents[2]
# 默认输出文件名（不含路径），实际路径在运行时基于当前工作目录计算
DEFAULT_PY_OUT_NAME = "generated_keywords.py"
DEFAULT_ROBOT_OUT_NAME = "generated_cases.robot"


@dataclass
class CaseSpec:
    index: int
    keyword_name: str
    robot_title: str
    request_member: str
    request_interface: str
    timestamp: str


@dataclass
class GeneratorConfig:
    input_path: Path
    py_out: Path
    robot_out: Path
    bmc_test_db_dir: Path
    test_db_name: str
    fixture_dir: Path
    repo_root: Path


def slugify(name: str) -> str:
    slug = re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_").lower()
    return slug or "call"


def build_cases(events: Sequence[dict]) -> List[CaseSpec]:
    cases: List[CaseSpec] = []
    counter = 1
    trailing_signals = 0
    for entry in events:
        if entry.get("type") == "signal":
            trailing_signals += 1
            continue
        if "request" not in entry:
            continue
        request_block = entry["request"]
        keyword_name = f"case_{counter:04d}_{slugify(request_block['member'])}"
        robot_title = f"Case {counter:04d} {request_block['member']}"
        cases.append(
            CaseSpec(
                index=counter,
                keyword_name=keyword_name,
                robot_title=robot_title,
                request_member=request_block["member"],
                request_interface=request_block["interface"],
                timestamp=request_block.get("timestamp", ""),
            )
        )
        trailing_signals = 0
        counter += 1
    if trailing_signals:
        logging.info(f"[INFO] 有 {trailing_signals} 条末尾 signal 未消费，已忽略。")
    return cases


def build_python_module(
    cases: Sequence[CaseSpec],
    bmc_test_db_dir: Path,
    test_db_name: str,
    fixture_dir: Path,
    repo_root: Path,
) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    meta = f'"""Auto-generated keywords @ {timestamp}."""'
    # fixture 路径
    fixture_path_expr = f"Path(r'{fixture_dir}')"
    header = "\n".join(
        [
            meta,
            "from __future__ import annotations",
            "",
            "import json",
            "import logging",
            "import sys",
            "import time",
            "from datetime import datetime",
            "from functools import lru_cache",
            "from pathlib import Path",
            "from typing import Any, Iterable, List",
            "",
            "THIS_DIR = Path(__file__).resolve().parent",
            f"DATA_PATH = THIS_DIR / 'test_data' / 'test_data.json'",
            f"FIXTURE_DIR = {fixture_path_expr}",
            "if str(FIXTURE_DIR) not in sys.path:",
            "    sys.path.insert(0, str(FIXTURE_DIR))",
            "",
            "from bmcgo.component.fixture.busctl_type_converter import BusCtlTypeConverter",
            "from dbus_next import Variant",
            "",
            "if str(THIS_DIR) not in sys.path:",
            "    sys.path.insert(0, str(THIS_DIR))",
            "",
            "from bmcgo.component.fixture.dbus_library import DBusLibrary",
            "from bmcgo.component.fixture.dbus_mock_utils import set_mock_response, clear_mock",
            "",
            "_DBUS = DBusLibrary()",
            "logger = logging.getLogger(__name__)",
            "",
            "DEPENDENCY_SERVICE = 'bmc.kepler.MockControl'",
            "DEPENDENCY_OBJECT_PATH = '/bmc/kepler/MockControl'",
            "DEPENDENCY_INTERFACE = 'bmc.kepler.MockControl'",
            "DEFAULT_DEPENDENCY_TIMEOUT_MS = 10000",
            "_TIMESTAMP_FORMATS = (\"%a %Y-%m-%d %H:%M:%S.%f %Z\", \"%a %Y-%m-%d %H:%M:%S %Z\")",
            "",
            "# 全局配置：是否按时间戳计算延迟（True=启用，False=禁用，但仍会执行 sleep_ms 和依赖等待）",
            "USE_TIMESTAMP_DELAY = True",
            "",
            "",
            "def _parse_busctl(text: str):",
            "    return BusCtlTypeConverter.dbus_string_to_type(text)",
            "",
            "",
            "@lru_cache(maxsize=1)",
            "def _load_events():",
            "    with DATA_PATH.open(encoding=\"utf-8\") as fh:",
            "        return json.load(fh)",
            "",
            "",
            "def _parse_timestamp_value(value: str):",
            "    if not value:",
            "        return None",
            "    for fmt in _TIMESTAMP_FORMATS:",
            "        try:",
            "            return datetime.strptime(value, fmt)",
            "        except ValueError:",
            "            continue",
            "    logger.debug(\"无法解析 timestamp: %s\", value)",
            "    return None",
            "",
            "",
            "def _prepare_signal_schedule(signal_specs: List[dict]):",
            "    prev_ts = None",
            "    for spec in signal_specs:",
            "        wait_cfg = dict(spec.get(\"wait\") or {})",
            "        delay_override = wait_cfg.get(\"delay_seconds\")",
            "        if delay_override is None and \"delay_ms\" in wait_cfg:",
            "            delay_override = wait_cfg.get(\"delay_ms\") / 1000.0",
            "        if delay_override is not None:",
            "            spec[\"delay_seconds\"] = max(float(delay_override), 0.0)",
            "            continue",
            "        if not USE_TIMESTAMP_DELAY:",
            "            spec[\"delay_seconds\"] = 0.0",
            "            continue",
            "        current_ts = _parse_timestamp_value(spec.get(\"timestamp\"))",
            "        if prev_ts and current_ts:",
            "            delta = max((current_ts - prev_ts).total_seconds(), 0.0)",
            "        else:",
            "            delta = 0.0",
            "        spec[\"delay_seconds\"] = delta",
            "        if current_ts:",
            "            prev_ts = current_ts",
            "",
            "",
            "def _convert_signal_entry(entry: dict):",
            "    wait_spec = entry.get(\"wait\")",
            "    if isinstance(wait_spec, dict):",
            "        wait_spec = dict(wait_spec)",
            "    else:",
            "        wait_spec = {}",
            "    sleep_ms = entry.get(\"sleep_ms\")",
            "    if sleep_ms is None and \"sleep_seconds\" in entry:",
            "        sleep_ms = float(entry.get(\"sleep_seconds\", 0)) * 1000",
            "    return {",
            "        \"path\": entry[\"path\"],",
            "        \"interface\": entry[\"interface\"],",
            "        \"member\": entry[\"member\"],",
            "        \"signature\": entry.get(\"signature\", \"\"),",
            "        \"args\": [_parse_busctl(item) for item in entry.get(\"content\", [])],",
            "        \"timestamp\": entry.get(\"timestamp\"),",
            "        \"wait\": wait_spec,",
            "        \"sleep_ms\": sleep_ms,",
            "    }",
            "",
            "",
            "def _convert_request_response(entry: dict):",
            "    request_block = entry[\"request\"]",
            "    response_block = entry.get(\"response\")",
            "    if response_block is None:",
            "        raise AssertionError(\"录制数据缺少 response 字段\")",
            "    request = {",
            "        \"destination\": request_block[\"destination\"],",
            "        \"path\": request_block[\"path\"],",
            "        \"interface\": request_block[\"interface\"],",
            "        \"member\": request_block[\"member\"],",
            "        \"args\": [_parse_busctl(arg) for arg in request_block.get(\"args\", [])],",
            "    }",
            "    expected = [_parse_busctl(value) for value in response_block.get(\"values\", [])]",
            "    return request, expected",
            "",
            "",
            "def _load_case_payload(case_index: int):",
            "    events = _load_events()",
            "    pending: List[dict] = []",
            "    counter = 1",
            "    for entry in events:",
            "        if entry.get(\"type\") == \"signal\":",
            "            pending.append(entry)",
            "            continue",
            "        if \"request\" in entry:",
            "            if counter == case_index:",
            "                signals = [_convert_signal_entry(sig) for sig in pending]",
            "                _prepare_signal_schedule(signals)",
            "                request, expected = _convert_request_response(entry)",
            "                return signals, request, expected",
            "            pending = []",
            "            counter += 1",
            "    raise AssertionError(f\"未在录制数据中找到序号为 {case_index} 的请求\")",
            "",
            "",
            "def _normalize(value: Any):",
            "    if isinstance(value, Variant):",
            "        return (\"variant\", value.signature, _normalize(value.value))",
            "    if isinstance(value, dict):",
            "        return {key: _normalize(val) for key, val in value.items()}",
            "    if isinstance(value, (list, tuple)):",
            "        return [_normalize(item) for item in value]",
            "    return value",
            "",
            "",
            "def _calculate_delay_seconds(spec: dict) -> float:",
            "    base = float(spec.get(\"delay_seconds\") or 0.0)",
            "    wait_cfg = spec.get(\"wait\") or {}",
            "    if \"extra_delay_ms\" in wait_cfg:",
            "        base += max(wait_cfg[\"extra_delay_ms\"], 0) / 1000.0",
            "    if \"post_delay_ms\" in wait_cfg:",
            "        base += max(wait_cfg[\"post_delay_ms\"], 0) / 1000.0",
            "    return max(base, 0.0)",
            "",
            "",
            "def _wait_for_dependency(spec: dict, idx: int):",
            "    wait_cfg = spec.get(\"wait\") or {}",
            "    dep_cfg = wait_cfg.get(\"dependency\")",
            "    if not dep_cfg:",
            "        return",
            "    lookup_key = dep_cfg.get(\"lookup_key\")",
            "    if not lookup_key:",
            "        raise AssertionError(f\"信号[{idx}] 缺少 dependency.lookup_key\")",
            "    target = int(dep_cfg.get(\"count\", 1))",
            "    timeout_ms = int(dep_cfg.get(\"timeout_ms\", DEFAULT_DEPENDENCY_TIMEOUT_MS))",
            "    timeout_seconds = timeout_ms / 1000.0",
            "    start_time = time.time()",
            "    check_interval = 0.1  # 每100ms查询一次",
            "    current_count = 0",
            "    ",
            "    while True:",
            "        try:",
            "            current_count = _DBUS.call_dbus_method(",
            "                DEPENDENCY_SERVICE,",
            "                DEPENDENCY_OBJECT_PATH,",
            "                DEPENDENCY_INTERFACE,",
            "                \"get_dependency_count\",",
            "                lookup_key,",
            "            )",
            "            if current_count >= target:",
            "                logger.info(",
            "                    f\"依赖 {lookup_key} 已满足：当前调用次数 {current_count} >= 目标 {target}\"",
            "                )",
            "                return",
            "        except Exception as exc:",
            "            logger.warning(",
            "                f\"查询依赖 {lookup_key} 调用次数失败: {exc}，继续等待\"",
            "            )",
            "        ",
            "        elapsed = time.time() - start_time",
            "        if elapsed >= timeout_seconds:",
            "            logger.warning(",
            "                f\"等待依赖 {lookup_key} 第 {target} 次调用超时 ({timeout_ms} ms)，当前调用次数: {current_count}，继续发送信号\"",
            "            )",
            "            return",
            "        ",
            "        time.sleep(check_interval)",
            "",
            "",
            "def _replay_signals(signal_specs: Iterable[dict]):",
            "    for idx, spec in enumerate(signal_specs, start=1):",
            "        _wait_for_dependency(spec, idx)",
            "        delay = _calculate_delay_seconds(spec)",
            "        if delay > 0:",
            "            time.sleep(delay)",
            "        path = spec[\"path\"]",
            "        interface = spec[\"interface\"]",
            "        member = spec[\"member\"]",
            "        signature = spec.get(\"signature\") or \"\"",
            "        args = spec.get(\"args\", [])",
            "        sleep_ms = spec.get(\"sleep_ms\")",
            "        if sleep_ms is not None and sleep_ms > 0:",
            "            time.sleep(sleep_ms / 1000.0)",
            "        try:",
            "            if signature:",
            "                _DBUS.send_signal_with_signature(",
            "                    path, interface, member, signature, *args",
            "                )",
            "            else:",
            "                _DBUS.send_signal(path, interface, member, *args)",
            "        except Exception as exc:",
            "            logger.warning(",
            "                f\"重放信号失败[{idx}] {interface}.{member} ({path}): {exc}\",",
            "                exc_info=True,",
            "            )",
            "",
            "",
            "def _call_and_assert(request: dict, expected_values: List[Any]):",
            "    raw = _DBUS.call_dbus_method(",
            "        request[\"destination\"],",
            "        request[\"path\"],",
            "        request[\"interface\"],",
            "        request[\"member\"],",
            "        *request[\"args\"],",
            "    )",
            "    if raw is None:",
            "        normalized_raw = []",
            "    elif isinstance(raw, tuple):",
            "        normalized_raw = [_normalize(item) for item in raw]",
            "    else:",
            "        normalized_raw = _normalize(raw)",
            "    normalized_expected = _normalize(",
            "        expected_values if len(expected_values) != 1 else expected_values[0]",
            "    )",
            "    if normalized_raw != normalized_expected:",
            "        raise AssertionError(",
            "            f\"期望 {normalized_expected!r}，实际 {normalized_raw!r}\"",
            "        )",
            "    return raw",
        ]
    )
    body_lines: List[str] = [header]
    runner_entries: List[str] = []
    for case in cases:
        body_lines.append(f"\n\ndef {case.keyword_name}():\n")
        doc = (
            f"\"\"\"{case.request_member} ({case.request_interface}) recorded at {case.timestamp}\"\"\""
        )
        body_lines.append(f"    {doc}\n")
        body_lines.append(f"    signals, request, expected = _load_case_payload({case.index})\n")
        body_lines.append("    _replay_signals(signals)\n")
        body_lines.append("    return _call_and_assert(request, expected)\n")
        runner_entries.append(f"    {case.index}: {case.keyword_name},")
    body_lines.append("\n\n_CASE_RUNNERS = {\n")
    body_lines.extend(line + "\n" for line in runner_entries)
    body_lines.append("}\n")
    body_lines.append(
        """

def run_case(case_index: int):
    try:
        func = _CASE_RUNNERS[case_index]
    except KeyError as exc:
        raise KeyError(f"未知 case 序号 {case_index}") from exc
    return func()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="运行录制用例")
    parser.add_argument("case", type=int, help="case 序号（从 1 开始）")
    args = parser.parse_args()
    run_case(args.case)
"""
    )
    return "".join(body_lines).rstrip() + "\n"


def build_robot_suite(cases: Sequence[CaseSpec], keywords_file: str) -> str:
    lines = [
        "*** Settings ***",
        f"Library    {keywords_file}",
        "",
        "*** Test Cases ***",
    ]
    for case in cases:
        lines.append(f"{case.robot_title}")
        lines.append(f"    {case.keyword_name}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def generate(config: GeneratorConfig) -> None:
    input_path = config.input_path
    py_out = config.py_out
    robot_out = config.robot_out
    bmc_test_db_dir = config.bmc_test_db_dir
    test_db_name = config.test_db_name
    fixture_dir = config.fixture_dir
    repo_root = config.repo_root
    with input_path.open(encoding="utf-8") as fh:
        events = json.load(fh)
    cases = build_cases(events)
    if not cases:
        raise BmcGoException("未在录制数据中找到 request/response 对。")
    py_out.write_text(
        build_python_module(cases, bmc_test_db_dir, test_db_name, fixture_dir, repo_root),
        encoding="utf-8",
    )
    keywords_file = py_out.name
    robot_out.write_text(build_robot_suite(cases, keywords_file), encoding="utf-8")
    logging.info(
        f"[OK] 生成 {len(cases)} 个用例。Python: {py_out} Robot: {robot_out}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="根据录制数据生成 Robot 用例")
    parser.add_argument(
        "--bmc-test-db-dir",
        required=True,
        help="bmc_test_db 目录路径（例如：/opt/code/network_adapter/temp/opt/bmc/it_test/bmc_test_db）",
    )
    parser.add_argument(
        "--test-db-name",
        required=True,
        help="测试数据库名称，即 bmc_test_db 下的第一层文件夹名（例如：network_adapter_y）",
    )
    parser.add_argument(
        "--fixture-dir",
        required=True,
        help="fixture 目录路径（例如：/opt/code/network_adapter/temp/opt/bmc/it_test/fixture）",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    # 不 resolve，直接使用传入路径，避免符号链接解析问题
    bmc_test_db_dir = Path(args.bmc_test_db_dir)
    if not bmc_test_db_dir.is_absolute():
        bmc_test_db_dir = bmc_test_db_dir.resolve()
    fixture_dir = Path(args.fixture_dir)
    if not fixture_dir.is_absolute():
        fixture_dir = fixture_dir.resolve()
    test_db_name = args.test_db_name
    # 自动构建 test_data.json 路径：bmc_test_db_dir / test_db_name / test_data / test_data.json
    input_path = bmc_test_db_dir / test_db_name / "test_data" / "test_data.json"
    if not input_path.exists():
        raise SystemExit(f"错误：找不到 test_data.json 文件: {input_path}")
    py_out = bmc_test_db_dir / test_db_name / f"{test_db_name}_keywords.py"
    robot_out = bmc_test_db_dir / test_db_name / f"{test_db_name}_cases.robot"
    repo_root = REPO_ROOT.resolve()
    config = GeneratorConfig(input_path, py_out, robot_out, bmc_test_db_dir, test_db_name, fixture_dir, repo_root)
    generate(config)


if __name__ == "__main__":
    main()
