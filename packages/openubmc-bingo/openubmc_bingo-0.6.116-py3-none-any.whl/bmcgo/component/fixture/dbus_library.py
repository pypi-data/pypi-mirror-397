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
from dbus_next.aio import MessageBus
from dbus_next import Message, MessageType
from dbus_next.errors import DBusError
from bmcgo.component.fixture.dbus_signature import DBusSignature

logger = logging.getLogger(__name__)


class DBusLibrary:
    def __init__(self):
        """初始化DBus连接"""
        self.bus = None
        self._loop = None
        self._connect()

    def __del__(self):
        """析构函数，确保连接被关闭"""
        self.close()

    def list_names(self):
        """获取所有已注册的 D-Bus 服务名"""
        try:
            async def _list_names():
                # 直接使用 Message API 调用 ListNames 方法
                list_names_msg = Message(
                    message_type=MessageType.METHOD_CALL,
                    destination='org.freedesktop.DBus',
                    path='/org/freedesktop/DBus',
                    interface='org.freedesktop.DBus',
                    member='ListNames',
                    signature='',
                    body=[]
                )

                reply = await self.bus.call(list_names_msg)
                if reply.message_type == MessageType.ERROR:
                    error_name = reply.error_name or 'UnknownError'
                    error_msg = reply.body[0] if reply.body else 'Unknown error'
                    raise DBusError(error_name, error_msg)
                # ListNames 返回一个字符串数组
                return reply.body[0] if reply.body else []
            names = self._loop.run_until_complete(_list_names())
            return names
        except Exception as e:
            logger.warning(f"获取 D-Bus 服务列表失败: {e}")
            return []

    def service_ok(self, service_name, timeout=5):
        """检查 D-Bus 服务是否已注册"""
        try:
            async def _check_service():
                introspection = await self.bus.introspect('org.freedesktop.DBus', '/org/freedesktop/DBus')
                proxy = self.bus.get_proxy_object('org.freedesktop.DBus', '/org/freedesktop/DBus', introspection)
                dbus_interface = proxy.get_interface('org.freedesktop.DBus')
                has_owner = await dbus_interface.call_name_has_owner(service_name)
                return has_owner
            has_owner = self._loop.run_until_complete(_check_service())
            if not has_owner:
                raise AssertionError(f"Service '{service_name}' is not registered")
            return has_owner
        except Exception as e:
            raise AssertionError(f"DBUS check failed: {e}") from e

    def get_interfaces(self, service_name, object_path):
        """获取指定服务指定对象的接口"""
        try:
            async def _get_introspection():
                introspection = await self.bus.introspect(service_name, object_path)
                proxy = self.bus.get_proxy_object(service_name, object_path, introspection)
                introspectable = proxy.get_interface('org.freedesktop.DBus.Introspectable')
                xml_data = await introspectable.call_introspect()
                return xml_data
            xml_data = self._loop.run_until_complete(_get_introspection())
            return xml_data
        except Exception as e:
            raise AssertionError(f"获取接口失败: {e}") from e

    def call_dbus_method(self, service_name, object_path, interface_name, method_name, *args):
        """调用指定服务指定对象指定接口指定方法（直接调用，不需要 introspect）"""
        try:
            async def _call_method():
                # 转换参数
                converted_args = []
                signature_parts = []
                for arg in args:
                    logger.info(f"Arg {arg}, type: {type(arg)}")
                    if isinstance(arg, dict):
                        # 字典类型，dbus-next直接支持Python字典
                        logger.debug("trans arg to dict")
                        converted_args.append(arg)
                        signature_parts.append(DBusSignature.get_dbus_signature(arg))
                    elif isinstance(arg, str) and arg.isdigit():
                        # 字符串数字转为整数
                        logger.debug("trans arg to int")
                        intarg = int(arg)
                        converted_args.append(intarg)
                        signature_parts.append(DBusSignature.get_dbus_signature(intarg))
                    else:
                        converted_args.append(arg)
                        signature_parts.append(DBusSignature.get_dbus_signature(arg))
                # 生成方法签名
                signature = ''.join(signature_parts)
                logger.info(f"转换后的参数: {converted_args}, 签名: {signature}")
                # 直接使用 Message API 调用方法，不需要 introspect
                call_msg = Message(
                    message_type=MessageType.METHOD_CALL,
                    destination=service_name,
                    path=object_path,
                    interface=interface_name,
                    member=method_name,
                    signature=signature,
                    body=converted_args
                )
                # 发送消息并等待回复
                reply = await self.bus.call(call_msg)
                # 检查是否有错误
                if reply.message_type == MessageType.ERROR:
                    error_name = reply.error_name or 'UnknownError'
                    error_msg = reply.body[0] if reply.body else 'Unknown error'
                    raise DBusError(error_name, error_msg)
                # 返回结果
                # 如果只有一个返回值，直接返回；如果有多个，返回元组
                if len(reply.body) == 0:
                    return None
                elif len(reply.body) == 1:
                    return reply.body[0]
                else:
                    return tuple(reply.body)
            result = self._loop.run_until_complete(_call_method())
            return result
        except DBusError as e:
            raise AssertionError(f"DBus Error: {e}") from e
        except Exception as e:
            raise AssertionError(f"Error: {e}") from e

    def send_signal(self, object_path, interface_name, signal_name, *args):
        """发送D-Bus信号（自动生成签名）

        Args:
            object_path: 对象路径，例如 '/org/example/Object'
            interface_name: 接口名称，例如 'org.example.Interface'
            signal_name: 信号名称，例如 'SignalName'
            *args: 信号的参数

        Returns:
            None
        """
        signature = ''
        if args:
            signature = ''.join([DBusSignature.get_dbus_signature(arg) for arg in args])
        return self.send_signal_with_signature(object_path, interface_name, signal_name, signature, *args)

    def send_signal_with_signature(self, object_path, interface_name, signal_name, signature, *args):
        """发送D-Bus信号（使用指定的签名）

        Args:
            object_path: 对象路径，例如 '/org/example/Object'
            interface_name: 接口名称，例如 'org.example.Interface'
            signal_name: 信号名称，例如 'SignalName'
            signature: D-Bus签名字符串，例如 'sa{sv}as' 表示 (string, dict, array of string)
            *args: 信号的参数，必须与签名匹配

        Returns:
            None

        Example:
            # 发送一个包含字符串、字典和字符串数组的信号
            dbus_lib.send_signal_with_signature(
                '/org/example/Object',
                'org.example.Interface',
                'PropertiesChanged',
                'sa{sv}as',  # 签名：string, dict, array of string
                'interface_name',
                {'key': Variant('s', 'value')},
                ['item1', 'item2']
            )
        """
        try:
            async def _send_signal():
                # 创建信号消息，使用指定的签名
                signal = Message(
                    destination='harbor.bmc.kepler.network_adapter',
                    message_type=MessageType.SIGNAL,
                    path=object_path,
                    interface=interface_name,
                    member=signal_name,
                    signature=signature,
                    body=list(args)
                )

                # 发送信号
                await self.bus.send(signal)
                logger.info(f"✅ 信号已发送: {interface_name}.{signal_name} 到 {object_path}, 参数: {args}, 签名: {signature}")

            self._loop.run_until_complete(_send_signal())

        except Exception as e:
            raise AssertionError(f"发送信号失败: {e}") from e

    def close(self):
        """关闭DBus连接"""
        try:
            if self.bus:
                async def _disconnect():
                    self.bus.disconnect()

                if self._loop and not self._loop.is_closed():
                    self._loop.run_until_complete(_disconnect())
                logger.info("DBus连接已关闭")
        except Exception as e:
            logger.warning(f"关闭DBus连接时出错: {e}")

    def _connect(self):
        """连接到DBus总线"""
        try:
            # 设置环境变量
            dbus_session_bus_address = os.environ['DBUS_SESSION_BUS_ADDRESS']
            if not dbus_session_bus_address:
                raise AssertionError("DBus总线地址未设置")
            logger.info(f"DBus总线地址: {dbus_session_bus_address}")
            # 创建新的事件循环（如果当前线程没有）
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
            # 同步方式连接（使用run_until_complete）
            if self._loop.is_running():
                # 如果循环已经在运行，使用异步方式
                raise RuntimeError("Event loop is already running. Use async methods instead.")
            else:
                self.bus = self._loop.run_until_complete(MessageBus().connect())
                logger.info(f"成功连接到DBus总线: {dbus_session_bus_address}")
        except Exception as e:
            raise AssertionError(f"DBus连接失败: {e}") from e

