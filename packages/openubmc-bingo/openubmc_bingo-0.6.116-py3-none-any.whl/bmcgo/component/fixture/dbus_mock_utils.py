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
# 自动生成的DBUS打桩服务公共工具类
import json
import os
import logging
from bmcgo.component.fixture.dbus_response_handler import DBusResponseHandler
from bmcgo.component.fixture.common_config import CommonConfig
# 首先需要导入 DBusTypeConverter
from bmcgo.component.fixture.busctl_type_converter import BusCtlTypeConverter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
MOCK_CONTROL_SERVICE = 'bmc.kepler.MockControl'
MOCK_CONTROL_OBJECT_PATH = '/bmc/kepler/MockControl'
MOCK_CONTROL_INTERFACE = 'bmc.kepler.MockControl'
# 全局运行时 mock 数据存储（跨服务共享）
# 格式：{service_name: {lookup_key: [records]}}
_runtime_mock_data = {}


def set_runtime_mock(service_name, lookup_key, response, args=None, match_mode='exact'):
    """在运行时设置 mock 响应

    Args:
        service_name: 服务名称，如 'bmc.kepler.persistence'
        lookup_key: 方法键，格式：'service|path|interface|method' 或完整格式
        response: 响应数据，支持以下格式：
            - dict: 包含 'type' 和响应数据的字典
                - type='method_return': 正常响应，需要 'values' 和 'signature'
                - type='error': 错误响应，需要 'error_name' 和 'error_message'
                - type='timeout'/'no_reply': 超时响应
                - type='delay': 延迟响应，需要 'delay_seconds' 或 'delay_ms' 和响应数据
                - type='interrupt': 中断响应，需要 'error_name' 和 'error_message'
            - list: 响应值列表（自动转换为 method_return）
            - 其他: 单个响应值（自动转换为 method_return）
        args: 请求参数列表（可选），用于参数匹配。如果为 None，匹配所有参数
        match_mode: 匹配模式
            - 'exact': 精确匹配参数（默认）
            - 'any': 匹配任意参数

    Returns:
        None
    """
    if service_name not in _runtime_mock_data:
        _runtime_mock_data[service_name] = {}

    if lookup_key not in _runtime_mock_data[service_name]:
        _runtime_mock_data[service_name][lookup_key] = []

    # 构建响应记录
    if isinstance(response, dict):
        # 已经是完整的响应格式
        response_dict = response.copy()
        if 'type' not in response_dict:
            response_dict['type'] = 'method_return'
    elif isinstance(response, list):
        # 列表格式，转换为 method_return
        response_dict = {
            'type': 'method_return',
            'values': response,
            'signature': ''
        }
    else:
        # 单个值，转换为 method_return
        response_dict = {
            'type': 'method_return',
            'values': [response],
            'signature': ''
        }

    # 构建请求记录
    request_dict = {
        'args': args if args is not None else []
    }

    record = {
        'request': request_dict,
        'response': response_dict,
        '_runtime_mock': True,  # 标记为运行时 mock
        '_match_mode': match_mode
    }

    _runtime_mock_data[service_name][lookup_key].append(record)
    logging.info(f'✅ 已设置运行时 mock: {service_name} {lookup_key} (参数: {args}, 模式: {match_mode})')


def clear_runtime_mock(service_name=None, lookup_key=None):
    """清除运行时 mock 数据

    Args:
        service_name: 服务名称，如果为 None 则清除所有服务的 mock
        lookup_key: 方法键，如果为 None 则清除该服务的所有 mock

    Returns:
        None
    """
    if service_name is None:
        _runtime_mock_data.clear()
        logging.info('✅ 已清除所有运行时 mock 数据')
    elif lookup_key is None:
        if service_name in _runtime_mock_data:
            del _runtime_mock_data[service_name]
            logging.info(f'✅ 已清除服务 {service_name} 的所有运行时 mock 数据')
    else:
        if service_name in _runtime_mock_data and lookup_key in _runtime_mock_data[service_name]:
            del _runtime_mock_data[service_name][lookup_key]
            logging.info(f'✅ 已清除运行时 mock: {service_name} {lookup_key}')


def get_runtime_mock_data(service_name):
    """获取指定服务的运行时 mock 数据

    Args:
        service_name: 服务名称

    Returns:
        dict: 运行时 mock 数据，格式：{lookup_key: [records]}
    """
    return _runtime_mock_data.get(service_name, {})


# 公共接口函数（供用例代码使用）
def set_mock_response(service_name, lookup_key, response, args=None, match_mode='exact'):
    """在运行时设置 mock 响应（公共接口）

    这是 set_runtime_mock 的公共接口，供用例代码使用。
    优先级高于 mock_data.json 中的配置。

    注意：由于 dbus_gateway.py 运行在独立进程中，通过 D-Bus 接口调用。

    Args:
        service_name: 服务名称，如 'bmc.kepler.persistence'
        lookup_key: 方法键，格式：'service|path|interface|method'
        response: 响应数据，支持以下格式：
            - dict: 包含 'type' 和响应数据的字典
                - type='method_return': 正常响应，需要 'values' 和 'signature'
                - type='error': 错误响应，需要 'error_name' 和 'error_message'
                - type='timeout'/'no_reply': 超时响应
                - type='delay': 延迟响应，需要 'delay_seconds' 或 'delay_ms' 和响应数据
                - type='interrupt': 中断响应，需要 'error_name' 和 'error_message'
            - list: 响应值列表（自动转换为 method_return）
            - 其他: 单个响应值（自动转换为 method_return）
        args: 请求参数列表（可选），用于参数匹配。如果为 None，匹配所有参数
        match_mode: 匹配模式 'exact'（精确匹配）或 'any'（匹配任意参数）

    示例：
        # 设置正常响应
        set_mock_response(
            'bmc.kepler.persistence',
            'bmc.kepler.persistence|/bmc/kepler/persistence|bmc.kepler.persistence|BatchRead',
            {'type': 'method_return', 'values': ['STRING "success"'], 'signature': 's'}
        )

        # 设置错误响应
        set_mock_response(
            'bmc.kepler.persistence',
            'bmc.kepler.persistence|/bmc/kepler/persistence|bmc.kepler.persistence|BatchRead',
            {'type': 'error', 'error_name': 'org.freedesktop.DBus.Error.Failed', 'error_message': 'Mock error'}
        )

        # 设置超时响应
        set_mock_response(
            'bmc.kepler.persistence',
            'bmc.kepler.persistence|/bmc/kepler/persistence|bmc.kepler.persistence|BatchRead',
            {'type': 'timeout'}
        )
    """
    # 通过 D-Bus 接口调用（跨进程）
    try:
        # 尝试导入 DBusLibrary（可能不存在，需要处理）
        try:
            from bmcgo.component.fixture.dbus_library import DBusLibrary
            dbus_lib = DBusLibrary()

            response_json = json.dumps(response)
            args_json = json.dumps(args) if args is not None else ''
            success = dbus_lib.call_dbus_method(
                MOCK_CONTROL_SERVICE,
                MOCK_CONTROL_OBJECT_PATH,
                MOCK_CONTROL_INTERFACE,
                'set_mock_response',
                service_name,
                lookup_key,
                response_json,
                args_json,
                match_mode
            )
            if success:
                logging.info(f'✅ 通过 D-Bus 接口设置 mock: {service_name} {lookup_key}')
            else:
                logging.warning(f'⚠️ 通过 D-Bus 接口设置 mock 失败，回退到本地设置')
                set_runtime_mock(service_name, lookup_key, response, args, match_mode)
        except ImportError:
            # DBusLibrary 不可用，回退到本地设置
            logging.warning(f'⚠️ DBusLibrary 不可用，使用本地设置（仅当前进程有效）')
            set_runtime_mock(service_name, lookup_key, response, args, match_mode)
    except Exception as e:
        logging.warning(f'⚠️ 通过 D-Bus 接口设置 mock 失败: {e}，回退到本地设置')
        set_runtime_mock(service_name, lookup_key, response, args, match_mode)


def clear_mock(service_name=None, lookup_key=None):
    """清除运行时 mock 数据（公共接口）

    这是 clear_runtime_mock 的公共接口，供用例代码使用。

    注意：由于 dbus_gateway.py 运行在独立进程中，通过 D-Bus 接口调用。

    Args:
        service_name: 服务名称，如果为 None 则清除所有服务的 mock
        lookup_key: 方法键，如果为 None 则清除该服务的所有 mock

    示例：
        # 清除特定方法的 mock
        clear_mock('bmc.kepler.persistence', 'bmc.kepler.persistence| \
            /bmc/kepler/persistence|bmc.kepler.persistence|BatchRead')

        # 清除整个服务的 mock
        clear_mock('bmc.kepler.persistence')

        # 清除所有 mock
        clear_mock()
    """
    # 通过 D-Bus 接口调用（跨进程）
    try:
        # 尝试导入 DBusLibrary（可能不存在，需要处理）
        try:
            from bmcgo.component.fixture.dbus_library import DBusLibrary
            dbus_lib = DBusLibrary()
            service_name_str = service_name if service_name else ''
            lookup_key_str = lookup_key if lookup_key else ''
            success = dbus_lib.call_dbus_method(
                MOCK_CONTROL_SERVICE,
                MOCK_CONTROL_OBJECT_PATH,
                MOCK_CONTROL_INTERFACE,
                'clear_mock',
                service_name_str,
                lookup_key_str
            )
            if success:
                logging.info(f'✅ 通过 D-Bus 接口清除 mock: service_name={service_name}, lookup_key={lookup_key}')
            else:
                logging.warning(f'⚠️ 通过 D-Bus 接口清除 mock 失败，回退到本地清除')
                clear_runtime_mock(service_name, lookup_key)
        except ImportError:
            # DBusLibrary 不可用，回退到本地清除
            logging.warning(f'⚠️ DBusLibrary 不可用，使用本地清除（仅当前进程有效）')
            clear_runtime_mock(service_name, lookup_key)
    except Exception as e:
        logging.warning(f'⚠️ 通过 D-Bus 接口清除 mock 失败: {e}，回退到本地清除')
        clear_runtime_mock(service_name, lookup_key)


class DBusMockUtils:
    """DBUS打桩服务的参数匹配和响应处理公共工具类"""
    def __init__(self, service_name, dbus_default_mock_path=None):
        self.service_name = service_name
        self.dbus_default_mock_path = dbus_default_mock_path
        # 初始化三个mock数据存储变量
        self.custom_mock_data = {}
        self.common_mock_data = {}
        self.default_mock_data = {}
        # 调用计数器：记录每个 lookup_key 的调用次数，用于按顺序返回响应
        # 格式：{lookup_key: {call_index: count}}
        # call_index 是参数组合的唯一标识（基于参数的哈希或序列化）
        self._call_counters = {}
        # 动态加载mock数据
        self._load_mock_data_from_paths()

    @staticmethod
    def match_args_by_position(business_args, req_business_args):
        """按位置匹配业务参数

        Args:
            business_args: 实际的业务参数列表，实际类型
            req_business_args: 运行日志中的业务参数列表，字符串类型还未转换
        Returns:
            bool: 参数是否匹配
        """
        # 首先检查参数数量是否匹配
        if len(business_args) != len(req_business_args):
            return False

        # 按位置逐一比较参数
        length_array = range(len(business_args))
        for i in length_array:
            b_arg = business_args[i]
            r_arg = req_business_args[i]
            # 使用 DBusTypeConverter.dbus_string_to_type 将字符串参数转换为正确的类型
            try:
                # 将 req_business_args 的字符串参数转换为正确的 D-Bus 类型
                converted_r_arg = BusCtlTypeConverter.dbus_string_to_type(r_arg)
            except Exception as e:
                logging.error(f"转换参数出错: {e}")
                # 转换失败时，尝试使用原始字符串进行比较
                if str(b_arg) != str(r_arg):
                    return False
                continue
            # 现在比较原始参数和转换后的参数
            if not DBusMockUtils._compare_dbus_objects(b_arg, converted_r_arg):
                return False
        return True

    @staticmethod
    def _compare_dbus_objects(obj1, obj2):
        """比较两个 D-Bus 对象是否相等

        委托给 BusCtlTypeConverter 的通用实现，包含字符串数组集合比较功能
        """
        # 委托给通用实现
        return BusCtlTypeConverter.compare_dbus_objects(obj1, obj2)

    @staticmethod
    def _get_call_index(business_args):
        """生成参数组合的唯一标识，用于区分不同的参数组合"""
        normalized_args = []
        try:
            # 将参数序列化为字符串作为唯一标识
            # 对于复杂对象，使用 json.dumps 序列化
            for arg in business_args:
                if isinstance(arg, (dict, list)):
                    normalized_args.append(json.dumps(arg, sort_keys=True))
                else:
                    normalized_args.append(str(arg))
            return '|'.join(normalized_args)
        except Exception:
            # 如果序列化失败，使用字符串表示
            return str(business_args)

    def match_params_and_get_response(self, method_key, args):
        """动态匹配参数并返回响应，支持按调用顺序返回
        优先级：运行时 mock > 默认 mock 数据
        Args:
            method_key: 方法键，格式：'service|path|interface|method'
            args: 方法参数列表
        Returns:
            响应数据（dict），如果未找到则返回None
        """
        # 过滤实际传入的参数（如果有）
        business_args = []
        if args:
            for arg in args:
                logging.info(f"arg type: {type(arg)}, arg value: {str(arg)}")
                # 过滤掉caller和source参数
                if isinstance(arg, str) and ('caller' not in arg.lower() and 'source' not in arg.lower()):
                    business_args.append(arg)  # 保留原始字符串类型
                else:
                    business_args.append(arg)  # 保留原始类型
        logging.info(f'🔍 方法调用: {method_key}, 业务参数: {business_args}')
        # 优先检查运行时 mock 数据
        runtime_mock_data = get_runtime_mock_data(self.service_name)
        if runtime_mock_data and method_key in runtime_mock_data:
            logging.info(f'🔍 尝试匹配运行时 mock 数据')
            record = self._match_record_by_call_params(runtime_mock_data, method_key, business_args)
            if record:
                logging.info(f'✅ 使用运行时 mock 响应')
                return DBusResponseHandler.process_response(record['response'])

        # 尝试匹配默认 mock 数据
        logging.info(f'🔍 尝试匹配默认 mock 数据')
        record = self._match_record_by_call_params(self.default_mock_data, method_key, business_args) 
        if record:
            # 返回对应的响应
            return DBusResponseHandler.process_response(record['response'])
        # 未找到精确匹配，打印警告日志并返回空
        logging.warning(f'⚠️ 未找到精确匹配的参数组合，method_key: {method_key}，提供的参数: {business_args}')        
        # 无预设响应
        logging.error(f'❌ 无预设响应,返回None')
        return None

    def clear_call_counters(self, lookup_key=None):
        """清除调用计数器的公共方法
        
        Args:
            lookup_key: 方法键，如果为None则清除所有调用计数器
        """
        if lookup_key is None:
            # 清除所有调用计数器
            self._call_counters.clear()
        else:
            # 清除特定方法的调用计数器（counter_key 格式是 "method_key|call_index"）
            keys_to_remove = [k for k in self._call_counters.keys() if k.startswith(lookup_key + '|')]
            for key in keys_to_remove:
                del self._call_counters[key]

    def get_call_counter_keys(self):
        """获取所有调用计数器键的公共方法
        
        Returns:
            list: 调用计数器的所有键
        """
        return list(self._call_counters.keys())

    def _load_mock_data_from_paths(self):
        """从多个路径加载mock数据到不同的变量中"""
        # 按优先级加载数据到不同的mock_data变量
        service_dir = self.service_name.replace('.', '_')
        # 加载默认mock数据
        if self.dbus_default_mock_path and os.path.exists(self.dbus_default_mock_path):
            service_mock_path = os.path.join(self.dbus_default_mock_path, service_dir, CommonConfig.DBUS_MOCK_DATA_FILE_NAME)
            self.default_mock_data = self._load_single_mock_data(service_mock_path, "default")

    def _load_single_mock_data(self, file_path, data_type):
        """加载单个mock数据文件"""
        mock_data = {}
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as mock_file:
                    data = json.load(mock_file)
                    # 直接使用完整的lookup_key作为method_key
                    for lookup_key, records in data.items():
                        if lookup_key.startswith(f'{self.service_name}|'):
                            try:
                                # 不再提取interface和member，直接使用完整的lookup_key
                                mock_data[lookup_key] = records
                            except ValueError:
                                continue
                logging.info(f"✅ 成功从 {file_path} 加载{data_type} mock数据")
            except Exception as e:
                logging.error(f"⚠️ 从 {file_path} 加载{data_type} mock数据失败: {e}")
        else:
            logging.warning(f"⚠️ {file_path} 不存在，跳过加载{data_type} mock数据")
        return mock_data

    def _match_record_by_call_params(self, mock_data, method_key, business_args, call_index=None):
        """匹配记录并返回，支持按调用顺序返回

        Args:
            mock_data: mock数据字典
            method_key: 方法键
            business_args: 业务参数列表
            call_index: 调用索引标识（如果为None，会自动生成）

        Returns:
            匹配的记录，如果未找到则返回None
        """
        if not mock_data:
            logging.error(f'❌ 未找到匹配的mock数据桩')
            return None
        # 直接查找完整的method_key
        matched_records = mock_data.get(method_key, [])
        if not matched_records:
            logging.error(f'❌ 未找到匹配的方法: {method_key}')
            return None
        logging.debug('🔍 找到 %s 条匹配记录，开始逐一匹配参数', len(matched_records))
        # 生成调用索引标识（如果未提供）
        if call_index is None:
            call_index = DBusMockUtils._get_call_index(business_args)
        # 初始化调用计数器
        counter_key = f"{method_key}|{call_index}"
        if counter_key not in self._call_counters:
            self._call_counters[counter_key] = 0
        call_count = self._call_counters[counter_key]
        # 先找到所有参数匹配的记录索引
        matching_indices = []
        for idx, record in enumerate(matched_records):
            # 卫语句：如果记录不完整，跳过当前循环
            if 'request' not in record or 'args' not in record['request'] or 'response' not in record:
                logging.debug('⚠️ 记录 %s 不完整，跳过', idx)
                continue
            # 检查是否是运行时 mock 且 match_mode='any'
            match_mode = record.get('_match_mode', 'exact')
            if match_mode == 'any':
                # 匹配任意参数，直接记录索引
                matching_indices.append(idx)
                continue
            # 处理请求参数，正确识别多行数组参数
            processed_req_args = record['request']['args']
            # 如果运行时 mock 的 args 为 None，匹配所有参数
            if record.get('_runtime_mock') and processed_req_args == [] and business_args == []:
                matching_indices.append(idx)
                continue
            # 提取请求中的业务参数（过滤caller和source）
            req_business_args = []
            for req_arg in processed_req_args:
                if isinstance(req_arg, str) and ('caller' not in req_arg.lower() and 'source' not in req_arg.lower()):
                    req_business_args.append(req_arg)
            # 剔除business_args多余的参数
            check_args = business_args[:]
            if len(processed_req_args) > len(req_business_args) and len(check_args) > len(req_business_args):
                check_args = check_args[len(check_args) - len(req_business_args):]
            # 卫语句：如果参数数量不匹配，跳过当前循环
            if len(check_args) > 0 and len(req_business_args) > 0 and len(check_args) != len(req_business_args):
                continue
            # 当有参数需要匹配时，检查参数内容是否匹配
            if len(check_args) > 0 and len(req_business_args) > 0:
                if not DBusMockUtils.match_args_by_position(check_args, req_business_args):
                    continue
            # 参数匹配成功，记录索引
            matching_indices.append(idx)
        if not matching_indices:
            logging.warning(f'❌ 所有记录都不匹配')
            return None
        # 根据调用次数选择对应的记录
        if call_count >= len(matching_indices):
            # 如果调用次数超过匹配记录数，使用最后一条记录（循环使用）
            selected_idx = matching_indices[-1]
            logging.warning(f'⚠️ 调用次数 {call_count} 超过匹配记录数 {len(matching_indices)}，使用最后一条记录')
        else:
            selected_idx = matching_indices[call_count]
        # 增加调用计数
        self._call_counters[counter_key] = call_count + 1
        selected_record = matched_records[selected_idx]
        logging.info(f'✅ 记录 {selected_idx} 匹配成功（第 {call_count + 1} 次调用，参数组合: {call_index[:50]}...）')
        return selected_record
