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
from dbus_next import Variant


class DBusSignature:

    @staticmethod
    def get_dbus_signature(value):
        """获取D-Bus值的签名

        dbus-next使用Python原生类型表示D-Bus类型，这里基于值类型推断签名
        """
        if isinstance(value, bool):
            return 'b'  # boolean
        elif isinstance(value, int):
            # 根据值范围推断整数类型
            if value >= 0 and value <= 255:
                return 'y'  # byte
            elif value >= -32768 and value <= 32767:
                # 注意：先检查正值范围，确保非负整数被正确识别为uint16
                if value >= 0:
                    return 'q'  # uint16
                else:
                    return 'n'  # int16
            elif value >= 0 and value <= 65535:
                return 'q'  # uint16
            elif value >= -2147483648 and value <= 2147483647:
                if value >= 0:
                    return 'u'  # uint32
                else:
                    return 'i'  # int32
            elif value >= 0 and value <= 4294967295:
                return 'u'  # uint32
            elif value >= -9223372036854775808 and value <= 9223372036854775807:
                if value >= 0:
                    return 't'  # uint64
                else:
                    return 'x'  # int64
            elif value >= 0 and value <= 18446744073709551615:
                return 't'  # uint64
            else:
                raise ValueError(f"Integer value {value} out of range for DBus types")
        elif isinstance(value, float):
            return 'd'  # double
        elif isinstance(value, bytes):
            return 'ay'  # array of bytes
        elif isinstance(value, str):
            # 检查是否是对象路径
            if value.startswith('/') and '//' not in value:
                return 'o'  # object path
            # 暂时移除对签名的自动检测，避免普通字符串被错误识别为签名
            # 在实际应用中，我们应该只在明确是签名的情况下才返回'g'
            return 's'  # 默认为string类型
        elif isinstance(value, list):
            # 首先检查是否是混合类型列表，如果是则视为结构体
            if len(value) > 0:
                # 获取所有元素的类型
                types = set(type(item) for item in value)
                # 如果有多种类型，或者包含字符串和数字的混合，视为结构体
                if len(types) > 1 or (int in types and str in types):
                    inner_sig = ''.join([DBusSignature.get_dbus_signature(elem) for elem in value])
                    return f'({inner_sig})'  # struct

                # 特殊处理结构体：如果列表内容看起来像结构体（混合类型或含有复杂类型）
                if all(isinstance(item, (str, bytes)) for item in value) and \
                    any(isinstance(item, bytes) for item in value):
                    # 这看起来像一个结构体（包含字符串和字节数组）
                    inner_sig = ''.join([DBusSignature.get_dbus_signature(elem) for elem in value])
                    return f'({inner_sig})'  # struct
            # 普通数组处理
            if value:
                # 检查是否是整数列表
                if all(isinstance(item, int) for item in value):
                    # 整数列表应该被识别为整数数组(ai)，而不是字节数组(ay)
                    return 'ai'
                # 假设所有元素类型相同
                elem_sig = DBusSignature.get_dbus_signature(value[0])
                # 移除自动将整数列表转换为字节数组的逻辑，因为dbus-next要求字节数组必须是bytes类型
                # 只有当明确传入bytes类型时才返回ay（这在前面的代码中已经处理）
                return f'a{elem_sig}'
            return 'av'  # 默认为variant数组
        elif isinstance(value, dict):
            if value:
                key, val = next(iter(value.items()))
                key_sig = DBusSignature.get_dbus_signature(key)
                # 特殊处理variant值
                if isinstance(val, Variant):
                    val_sig = 'v'
                else:
                    val_sig = DBusSignature.get_dbus_signature(val)
                return f'a{{{key_sig}{val_sig}}}'
            return 'a{sv}'  # 默认为string:variant字典
        elif isinstance(value, tuple):
            # 结构体签名需要用括号包围
            inner_sig = ''.join([DBusSignature.get_dbus_signature(elem) for elem in value])
            return f'({inner_sig})'  # struct
        elif isinstance(value, Variant):
            return 'v'
        else:
            return 's'  # 默认视为字符串