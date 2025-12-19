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
import asyncio
import logging
import os
import sys
import uuid
from collections import defaultdict
from typing import DefaultDict
from dbus_next.aio import MessageBus
from dbus_next.message import Message, MessageType
from dbus_next.service import ServiceInterface, method
from dbus_mock_utils import DBusMockUtils, set_runtime_mock, clear_runtime_mock
from dbus_signature import DBusSignature
from dbus_response_handler import DBusResponseHandler
from common_config import CommonConfig

# 常量定义
"""
优化 DBus 入口服务，支持通过命令行指定 mock_data 路径。

使用示例:
    python dbus_gateway.py /opt/code/BMCITFramework/bmc_test_db/network_adapter_y/mock_data
"""
DBUS_BUS_ADDRESS = 'DBUS_SESSION_BUS_ADDRESS'

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 存储不同服务的DBusMockUtils实例
_mock_utils_instances = {}
_dbus_default_mock_path = None  # 全局mock数据路径
service_names = []
dependency_tracker = None
bus = None

MOCK_CONTROL_SERVICE = 'bmc.kepler.MockControl'
MOCK_CONTROL_OBJECT_PATH = '/bmc/kepler/MockControl'
MOCK_CONTROL_INTERFACE = 'bmc.kepler.MockControl'


class DependencyTracker:
    """记录被测组件访问依赖服务的次数

    测试端通过循环调用 get_dependency_count 来查询依赖调用次数，实现等待机制。
    不再使用异步等待，简化了实现并提高了可控性。
    """

    def __init__(self):
        self._counts: DefaultDict[str, int] = defaultdict(int)

    def get_count(self, lookup_key: str) -> int:
        """获取指定依赖的调用次数"""
        return self._counts.get(lookup_key, 0)

    async def record(self, lookup_key: str) -> None:
        """记录一次依赖调用"""
        self._counts[lookup_key] = self._counts.get(lookup_key, 0) + 1


class MockControlInterface(ServiceInterface):
    """D-Bus 接口：提供依赖调用次数查询和运行时 mock 设置功能

    测试端通过循环调用 get_dependency_count 来实现等待机制，不再使用 WaitForDependency。
    通过 set_mock_response 和 clear_mock 可以在运行时设置 mock 数据。
    """

    def __init__(self, tracker: DependencyTracker):
        super().__init__(MOCK_CONTROL_INTERFACE)
        self._tracker = tracker

    @method()
    async def get_dependency_count(self, lookup_key: 's') -> 'u':
        """获取指定依赖的调用次数

        Args:
            lookup_key: 依赖标识，格式：'service|path|interface|method'

        Returns:
            该依赖的调用次数
        """
        return self._tracker.get_count(lookup_key)

    @method()
    async def set_mock_response(
        self,
        service_name: 's',
        lookup_key: 's',
        response_json: 's',
        args_json: 's' = '',
        match_mode: 's' = 'exact'
    ) -> 'b':
        """设置运行时 mock 响应

        Args:
            service_name: 服务名称，如 'bmc.kepler.persistence'
            lookup_key: 方法键，格式：'service|path|interface|method'
            response_json: 响应数据的 JSON 字符串
            args_json: 请求参数的 JSON 字符串（可选，默认为空字符串表示匹配所有参数）
            match_mode: 匹配模式 'exact'（精确匹配）或 'any'（匹配任意参数）

        Returns:
            bool: 是否设置成功
        """
        try:
            import json
            response = json.loads(response_json)
            args = json.loads(args_json) if args_json else None
            set_runtime_mock(service_name, lookup_key, response, args, match_mode)
            logger.info(f"✅ 通过 D-Bus 接口设置 mock: {service_name} {lookup_key}")
            return True
        except Exception as e:
            logger.error(f"❌ 设置 mock 失败: {e}")
            return False

    @method()
    async def clear_mock(self, service_name: 's' = '', lookup_key: 's' = '') -> 'b':
        """清除运行时 mock 数据

        Args:
            service_name: 服务名称，如果为空字符串则清除所有服务的 mock
            lookup_key: 方法键，如果为空字符串则清除该服务的所有 mock

        Returns:
            bool: 是否清除成功
        """
        try:
            service_name = service_name if service_name else None
            lookup_key = lookup_key if lookup_key else None
            clear_runtime_mock(service_name, lookup_key)

            # 清除调用计数器（调用计数器的键格式是 "method_key|call_index"）
            if service_name is None:
                # 清除所有服务的调用计数器
                for svc_name in list(_mock_utils_instances.keys()):
                    if svc_name in _mock_utils_instances:
                        _mock_utils_instances[svc_name].clear_call_counters()
                logger.info("✅ 已清除所有服务的调用计数器")
            elif lookup_key is None:
                # 清除该服务的所有调用计数器
                # 如果实例不存在，先创建它（这样调用计数器就会被初始化为空）
                mock_utils = get_or_create_mock_utils(service_name)
                mock_utils.clear_call_counters()
                logger.info(f"✅ 已清除服务 {service_name} 的所有调用计数器")
            else:
                # 清除特定方法的调用计数器（counter_key 格式是 "method_key|call_index"）
                # 如果实例不存在，先创建它
                mock_utils = get_or_create_mock_utils(service_name)
                # 记录清除前的状态
                all_keys = mock_utils.get_call_counter_keys()
                logger.info(f"🔍 清除前，调用计数器中的所有键: {all_keys}")
                # 使用公共方法清除特定方法的调用计数器
                mock_utils.clear_call_counters(lookup_key)
                # 记录清除后的状态
                remaining_keys = mock_utils.get_call_counter_keys()
                cleared_count = len(all_keys) - len(remaining_keys)
                if cleared_count > 0:
                    logger.info(f"✅ 已清除方法 {lookup_key} 的调用计数器（共 {cleared_count} 个）")
                else:
                    logger.info(f"✅ 方法 {lookup_key} 的调用计数器已为空或不存在（当前计数器键: {all_keys}）")

            logger.info(f"✅ 通过 D-Bus 接口清除 mock: service_name={service_name}, lookup_key={lookup_key}")
            return True
        except Exception as e:
            logger.error(f"❌ 清除 mock 失败: {e}")
            return False


def _convert_directory_to_service(dir_name):
    """
    将目录名转换为服务名，规则：
    bmc_kepler_xxx -> bmc.kepler.xxxx（仅转换前缀，下划线保持原样）
    """
    prefix = 'bmc_kepler_'
    if dir_name.startswith(prefix):
        return 'bmc.kepler.' + dir_name[len(prefix):]
    return dir_name


def load_service_names_from_path(mock_data_root):
    """
    根据mock_data目录下的子目录计算要注册的服务名
    """
    names = []
    if not mock_data_root:
        return names
    if not os.path.isdir(mock_data_root):
        logger.warning(f"指定的 mock_data 路径不存在: {mock_data_root}")
        return names

    for entry in os.listdir(mock_data_root):
        full_path = os.path.join(mock_data_root, entry)
        if os.path.isdir(full_path):
            service_name = _convert_directory_to_service(entry)
            names.append(service_name)
    return names


def get_or_create_mock_utils(service_name):
    """获取或创建DBusMockUtils实例"""
    if service_name not in _mock_utils_instances:
        _mock_utils_instances[service_name] = DBusMockUtils(service_name, _dbus_default_mock_path)
    return _mock_utils_instances[service_name]


def generate_signature(values):
    """自动生成D-Bus响应签名

    Args:
        values: 要生成签名的值列表

    Returns:
        生成的D-Bus签名字符串
    """
    if not values:
        return ''  # 空签名

    # 直接拼接所有值的签名，不添加括号
    return ''.join([DBusSignature.get_dbus_signature(v) for v in values])


def _handle_get_dependency_count(args, depen_tracker):
    """处理 get_dependency_count 方法
    
    Args:
        args: 方法参数列表
        depen_tracker: 依赖追踪器实例
        
    Returns:
        (signature, response_values) 或 None
    """
    if depen_tracker is None:
        logger.warning("MockControl 接口调用 get_dependency_count 但 depen_tracker 未初始化")
        return None
    
    if len(args) < 1:
        logger.error("get_dependency_count 缺少参数 lookup_key")
        return None
    
    lookup_key = args[0]
    count = depen_tracker.get_count(lookup_key)
    logger.info(f"查询依赖调用次数: {lookup_key} -> {count}")
    return ('u', [count])


def _handle_set_mock_response(args):
    """处理 set_mock_response 方法
    
    Args:
        args: 方法参数列表
        
    Returns:
        (signature, response_values)
    """
    if len(args) < 3:
        logger.error("set_mock_response 参数不足，需要至少 3 个参数")
        return None
    
    service_name = args[0]
    lookup_key = args[1]
    response_json = args[2]
    args_json = args[3] if len(args) > 3 else ''
    match_mode = args[4] if len(args) > 4 else 'exact'
    
    try:
        import json
        response = json.loads(response_json)
        args_list = json.loads(args_json) if args_json else None
        set_runtime_mock(service_name, lookup_key, response, args_list, match_mode)
        logger.info(f"✅ 通过 D-Bus 接口设置 mock: {service_name} {lookup_key}")
        return ('b', [True])
    except Exception as e:
        logger.error(f"❌ 设置 mock 失败: {e}")
        return ('b', [False])


def _clear_all_service_call_counters():
    """清除所有服务的调用计数器"""
    for svc_name in list(_mock_utils_instances.keys()):
        if svc_name in _mock_utils_instances:
            _mock_utils_instances[svc_name].clear_call_counters()
    logger.info("✅ 已清除所有服务的调用计数器")


def _clear_service_call_counters(service_name):
    """清除指定服务的所有调用计数器
    
    Args:
        service_name: 服务名称
    """
    mock_utils = get_or_create_mock_utils(service_name)
    mock_utils.clear_call_counters()
    logger.info(f"✅ 已清除服务 {service_name} 的所有调用计数器")


def _clear_method_call_counters(service_name, lookup_key):
    """清除特定方法的调用计数器
    
    Args:
        service_name: 服务名称
        lookup_key: 方法键
    """
    mock_utils = get_or_create_mock_utils(service_name)
    # 记录清除前的状态
    all_keys = mock_utils.get_call_counter_keys()
    logger.info(f"🔍 清除前，调用计数器中的所有键: {all_keys}")
    # 使用公共方法清除特定方法的调用计数器
    mock_utils.clear_call_counters(lookup_key)
    # 记录清除后的状态
    remaining_keys = mock_utils.get_call_counter_keys()
    cleared_count = len(all_keys) - len(remaining_keys)
    if cleared_count > 0:
        logger.info(f"✅ 已清除方法 {lookup_key} 的调用计数器（共 {cleared_count} 个）")
    else:
        logger.info(f"✅ 方法 {lookup_key} 的调用计数器已为空或不存在（当前计数器键: {all_keys}）")


def _handle_clear_mock(args):
    """处理 clear_mock 方法
    
    Args:
        args: 方法参数列表
        
    Returns:
        (signature, response_values)
    """
    service_name = args[0] if len(args) > 0 and args[0] else None
    lookup_key = args[1] if len(args) > 1 and args[1] else None
    
    try:
        clear_runtime_mock(service_name, lookup_key)
        
        # 清除调用计数器（调用计数器的键格式是 "method_key|call_index"）
        if service_name is None:
            _clear_all_service_call_counters()
        elif lookup_key is None:
            _clear_service_call_counters(service_name)
        else:
            _clear_method_call_counters(service_name, lookup_key)
        
        logger.info(f"✅ 通过 D-Bus 接口清除 mock: service_name={service_name}, lookup_key={lookup_key}")
        return ('b', [True])
    except Exception as e:
        logger.error(f"❌ 清除 mock 失败: {e}")
        import traceback
        logger.error(f"❌ 错误详情: {traceback.format_exc()}")
        return ('b', [False])


def _handle_mock_control_interface(method_name, args, depen_tracker):
    """处理 MockControl 接口方法
    
    Args:
        method_name: 方法名
        args: 方法参数列表
        depen_tracker: 依赖追踪器实例
        
    Returns:
        (signature, response_values) 或 None
    """
    if method_name == 'get_dependency_count':
        return _handle_get_dependency_count(args, depen_tracker)
    elif method_name == 'set_mock_response':
        return _handle_set_mock_response(args)
    elif method_name == 'clear_mock':
        return _handle_clear_mock(args)
    # 其他 MockControl 方法可以在这里添加
    return None


def _handle_dbus_peer_interface(method_name):
    """处理 org.freedesktop.DBus.Peer 接口方法
    
    Args:
        method_name: 方法名
        
    Returns:
        (signature, response_values) 或 None
    """
    if method_name == 'Ping':
        # Ping 方法：无参数，无返回值（空签名）
        return ('', [])
    elif method_name == 'GetMachineId':
        # GetMachineId 方法：无参数，返回机器ID字符串
        # 生成一个简单的机器ID（实际应该从 /etc/machine-id 读取）
        machine_id = str(uuid.uuid4()).replace('-', '')
        return ('s', [machine_id])
    return None


def handle_standard_dbus_method(interface, method_name, args, depen_tracker=None):
    """处理标准 D-Bus 接口方法和 MockControl 接口方法

    Args:
        interface: D-Bus 接口名
        method_name: 方法名
        args: 方法参数列表
        depen_tracker: 依赖追踪器实例（可选）

    Returns:
        (signature, response_values) 或 None（如果不是标准方法）
    """
    # MockControl 接口处理
    if interface == MOCK_CONTROL_INTERFACE:
        return _handle_mock_control_interface(method_name, args, depen_tracker)
    
    # org.freedesktop.DBus.Peer 接口处理
    if interface == 'org.freedesktop.DBus.Peer':
        return _handle_dbus_peer_interface(method_name)
    
    return None


async def process_method_call(message_bus, message):
    """处理方法调用请求"""
    try:
        service_name = message.destination
        object_path = message.path
        interface = message.interface
        method_name = message.member
        args = message.body
        logger.info(f"📨 请求: {service_name} {object_path} {interface} {method_name} {args}")
        # 首先检查是否是标准 D-Bus 接口方法或 MockControl 接口方法
        standard_response = handle_standard_dbus_method(interface, method_name, args, dependency_tracker)
        if standard_response is not None:
            signature, response_values = standard_response
            reply = Message.new_method_return(
                message,
                signature,
                response_values
            )
            await message_bus.send(reply)
            logger.info(f"✅ 标准方法响应: {interface}.{method_name} -> {response_values}")
            return
        # 构建lookup_key
        lookup_key = f"{service_name}|{object_path}|{interface}|{method_name}"
        # 获取响应
        mock_utils = get_or_create_mock_utils(service_name)
        response = mock_utils.match_params_and_get_response(lookup_key, args)
        if response is not None:
            response_type = response.get('type')
            # 处理 no_reply 或 timeout 类型（不发送响应，模拟超时）
            if response_type in ('no_reply', 'timeout'):
                logger.info(f"🔇 模拟超时，不发送响应: {lookup_key}")
                # 不发送响应，让调用端超时
                return
            # 处理 delay 类型（延迟响应）
            if response_type == 'delay':
                delay_seconds = response.get('delay_seconds', 0)
                if delay_seconds > 0:
                    logger.info(f"⏳ 延迟响应 {delay_seconds} 秒: {lookup_key}")
                    await asyncio.sleep(delay_seconds)
                # 继续处理延迟后的响应（如果有 values）
            # 处理 error 或 interrupt 类型（发送错误响应）
            if response_type in ('error', 'interrupt'):
                error_name = response.get('error_name', 'org.freedesktop.DBus.Error.Failed')
                error_message = response.get('error_message', 'Mock error response' if response_type == 'error' else 'Connection interrupted')
                log_level = logger.warning if response_type == 'interrupt' else logger.error
                log_level(f"{'⚠️ 模拟中断' if response_type == 'interrupt' else '❌ 发送错误响应'}: {error_name} - {error_message}")
                try:
                    error_reply = Message(
                        destination=message.sender,
                        path=message.path,
                        interface=message.interface,
                        message_type=MessageType.ERROR,
                        error_name=error_name,
                        reply_serial=message.serial,
                        signature='s',
                        body=[error_message]
                    )
                    await message_bus.send(error_reply)
                    if response_type == 'interrupt':
                        logger.warning(f"⚠️ 已发送错误响应，模拟中断连接（注意：实际中断连接需要更复杂的处理）")
                except Exception as e:
                    logger.error(f"⚠️ 发送错误回复时出错: {str(e)}")
                return
            # 处理正常的 method_return 类型响应
            if dependency_tracker is not None:
                await dependency_tracker.record(lookup_key)
            
            # 使用 DBusResponseHandler 处理响应，确保 D-Bus 格式字符串被正确转换
            processed_response = DBusResponseHandler.process_response(response)
            
            if isinstance(processed_response, dict) and 'values' in processed_response:
                response_values = processed_response['values']
                response_signature = processed_response.get('signature')
            else:
                response_values = processed_response
                response_signature = None
            # 确保 response_values 是正确的类型
            # 如果 response_values 是列表，确保列表中的元素类型正确
            logger.info(f"🔍 处理响应值: response_values类型={type(response_values)}, response_values={response_values}")
            if isinstance(response_values, list) and len(response_values) > 0:
                # 检查列表中的每个元素
                for idx, value in enumerate(response_values):
                    logger.debug("🔍 响应值[%s]: 类型=%s, 值=%s", idx, type(value), value)
                    if isinstance(value, dict):
                        # 检查字典中的值，确保嵌套的字典也是正确的类型
                        for key, val in value.items():
                            logger.debug("  🔍 字典键 '%s': 类型=%s, 值=%s", key, type(val), val)
                            if isinstance(val, str) and val.startswith('{'):
                                # 可能是 JSON 字符串，尝试解析
                                try:
                                    import json
                                    parsed = json.loads(val)
                                    value[key] = parsed
                                    logger.info(f"✅ 成功将字典值 '{key}' 从字符串解析为 JSON: {type(parsed)}")
                                except Exception as e:
                                    logger.warning(f"⚠️ 无法将字典值 '{key}' 解析为 JSON，保持原值")
                    elif isinstance(value, str):
                        # 如果第一个值是字符串，可能是 JSON 序列化的问题
                        logger.warning(f"⚠️ 响应值[{idx}] 是字符串类型: {type(value)}, 值: {value[:100] if len(str(value)) > 100 else value}")
                        # 尝试解析为 JSON
                        try:
                            import json
                            parsed = json.loads(value)
                            response_values[idx] = parsed
                            logger.info(f"✅ 成功将响应值[{idx}] 从字符串解析为 JSON: {type(parsed)}")
                        except Exception as e:
                            logger.error(f"❌ 无法将响应值[{idx}] 解析为 JSON，保持原值")
            if response_signature is None:
                response_signature = generate_signature(response_values)
            logger.debug("📤 准备发送响应: signature=%s, values类型=%s, values=%s", response_signature, type(response_values), response_values)
            # 创建并发送回复 - 使用dbus-next的Message类
            reply = Message.new_method_return(
              message,
              response_signature,
              response_values
            )
            await message_bus.send(reply)
            logger.info(f"✅ 响应: {response_values}")
        else:
            # 发送一个默认的错误回复
            logger.warning(f"❌ 未找到响应: {lookup_key}")
            try:
                error_reply = Message(
                    destination=message.sender,
                    path=message.path,
                    interface=message.interface,
                    message_type=MessageType.ERROR,  # 移除member参数
                    error_name='org.freedesktop.DBus.Error.UnknownMethod',
                    reply_serial=message.serial,
                    signature='s',  # 添加签名
                    body=[f'Method {method_name} not found or no response data available']
                )
                await message_bus.send(error_reply)
            except Exception as e:
                logger.error(f"⚠️ 发送错误回复时出错: {str(e)}")
    except Exception as e:
        import traceback
        logger.error(f"⚠️ 处理请求时出错: {str(e)}")
        logger.error(f"📋 错误详情:\n{traceback.format_exc()}")
        try:
            # 尝试发送错误响应
            error_reply = Message(
                destination=message.sender,
                path=message.path,
                interface=message.interface,
                message_type=MessageType.ERROR,  # 移除member参数
                error_name='org.freedesktop.DBus.Error.Failed',
                reply_serial=message.serial,
                signature='s',  # 添加签名
                body=[str(e)]
            )
            await message_bus.send(error_reply)
        except Exception as exce:
            logger.info(f"发送错误响应时出错: {str(exce)}")


async def main():
    """主函数"""
    global bus, service_names, dependency_tracker

    if len(sys.argv) < 5:
        logger.error("请提供所有必需参数: python dbus_gateway.py <test_db_name> <project_path> <bmc_test_db_path> <dbus_address>")
        return

    test_db_name = sys.argv[1]
    project_path = sys.argv[2]
    bmc_test_db_path = sys.argv[3]
    dbus_address_arg = sys.argv[4]
    
    # 根据 bmc_test_db_path 和 test_db_name 计算 mock_data_root
    mock_data_root = os.path.join(bmc_test_db_path, test_db_name, 'mock_data')
    
    # 计算dbus_default_mock_path（用于传递给DBusMockUtils）
    dbus_default_mock_path = mock_data_root
    
    # 保存全局配置，供get_or_create_mock_utils使用
    global _dbus_default_mock_path
    _dbus_default_mock_path = dbus_default_mock_path
    
    service_names = load_service_names_from_path(mock_data_root)
    if not service_names:
        logger.warning(f"在 {mock_data_root} 下未找到任何 mock 服务目录，将不会注册业务服务名")

    # 指定DBus地址，从环境变量获取或使用传入的值
    dbus_address = os.environ.get(DBUS_BUS_ADDRESS, dbus_address_arg)
    logger.info(f"使用DBus地址 ({DBUS_BUS_ADDRESS}): {dbus_address}")

    # 修改连接方式，先设置环境变量再连接
    old_address = os.environ.get(DBUS_BUS_ADDRESS)
    os.environ[DBUS_BUS_ADDRESS] = dbus_address
    # 创建并连接到DBus总线
    bus = await MessageBus().connect()
    logger.info(f"成功连接到DBus总线 ({DBUS_BUS_ADDRESS}): {dbus_address}")

    # 关键修改：打印出当前进程的环境变量信息，帮助调试
    logger.info(f"当前进程 {DBUS_BUS_ADDRESS}: {os.environ.get(DBUS_BUS_ADDRESS)}")
    dependency_tracker = DependencyTracker()
    # 导出 MockControl 接口（备用，实际处理在 handle_standard_dbus_method 中统一处理）
    control_interface = MockControlInterface(dependency_tracker)
    bus.export(MOCK_CONTROL_OBJECT_PATH, control_interface)
    try:
        await bus.request_name(MOCK_CONTROL_SERVICE)
        logger.info(f"已注册依赖控制接口: {MOCK_CONTROL_SERVICE}")
    except Exception as exc:
        logger.error(f"注册依赖控制接口失败: {exc}")

    def handler_wrapper(message):
        if message.message_type == MessageType.METHOD_CALL:
            logger.debug("拦截到方法调用: %s %s %s %s", message.destination, message.path, message.interface, message.member)
            asyncio.create_task(process_method_call(bus, message))
            return True  # 返回True表示已处理消息,阻止消息继续传播
        return False  # 返回False允许消息继续传播

    # 注册消息处理器
    bus.add_message_handler(handler_wrapper)
    logger.info("已注册消息处理器")

    # 尝试注册多个服务名

    for name in service_names:
        try:
            result = await bus.request_name(name)
            logger.info(f"成功注册服务名: {name}")
        except Exception as e:
            logger.warning(f"无法注册服务名 {name}: {e}")

    # 测试：列出当前注册的所有名称
    try:
        introspection = await bus.introspect('org.freedesktop.DBus', '/org/freedesktop/DBus')
        proxy = bus.get_proxy_object('org.freedesktop.DBus', '/org/freedesktop/DBus', introspection)
        dbus_interface = proxy.get_interface('org.freedesktop.DBus')
        names = await dbus_interface.call_list_names()
        logger.info(f"当前已注册的服务名列表: {names}")
    except Exception as e:
        logger.error(f"无法获取服务名列表: {e}")

    logger.info("🟢 公共DBUS入口服务已启动")
    logger.info("🟢 请在其他终端使用以下命令连接到此DBus会话：")
    logger.info(f"🟢 export {DBUS_BUS_ADDRESS}={dbus_address}")

    # 保持运行
    await asyncio.get_event_loop().create_future()


if __name__ == "__main__":
    asyncio.run(main())