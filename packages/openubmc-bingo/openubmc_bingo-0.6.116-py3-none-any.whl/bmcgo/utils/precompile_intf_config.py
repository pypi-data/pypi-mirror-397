#!/usr/bin/env python
# coding=utf-8
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
import json
from bmcgo.tasks.task import Task
from bmcgo.component.package_info import InfoComp
from bmcgo import misc

permission_dict = {
    "redfish": {"rd": 550, "r": 440, "user": [104, 104]},
    "web_backend": {"rd": 550, "r": 440, "user": [104, 104]},
    "snmp": {"rd": 550, "r": 440, "user": [95, 95]},
    misc.CLI: {"rd": 555, "r": 444, "user": [0, 0]}
}


class PrecompileIntfConfig(Task):
    def __init__(self, config, work_name="", interface="", json_dir="", info: InfoComp = None):
        super(PrecompileIntfConfig, self).__init__(config, work_name=work_name)
        self.info: InfoComp = info
        self.intf = interface
        self.json_dir = json_dir
        return
        
    @staticmethod
    def get_relative_path_paths(json_dir, json_path):
        relative_path = os.path.relpath(json_path, json_dir)
        if os.sep == '\\':
            relative_path = relative_path.replace('\\', '/')
        return relative_path.split('/')

    @staticmethod
    def get_sorted_json_files(json_dir):
        json_files = []
        for root, _, files in os.walk(json_dir):
            for file in files:
                if file.endswith(".json") and not os.path.islink(file):
                    file_path = os.path.join(root, file)
                    json_files.append(file_path)
        # 按文件路径排序，确保处理顺序一致
        json_files.sort()
        return json_files
    
    @staticmethod
    def set_dict_value(keys, k, v, mapper):
        current_dict = mapper
        for key in keys:
            if key not in current_dict:
                current_dict[key] = {}
            current_dict = current_dict[key]
        current_dict[k] = v
        
    def run_command(self, command, ignore_error=False, sudo=False, **kwargs):
        """
        如果ignore_error为False，命令返回码非0时则打印堆栈和日志并触发异常，中断构建
        """
        uptrace = kwargs.get("uptrace", 1)
        kwargs["uptrace"] = uptrace
        return self.tools.run_command(command, ignore_error, sudo, **kwargs)
    
    def restore_permission(self, target_dir):
        p = {"rd": 550, "r": 440, "user": [0, 0]}
        for key, value in permission_dict.items():
            app = "opt/bmc/apps/" + key
            if app in target_dir:
                p = value

        self.pipe_command([f"sudo find {target_dir} -type d", f"sudo xargs -P 0 -i. chmod {p['rd']} ."])
        self.pipe_command([f"sudo find {target_dir} -type f", f"sudo xargs -P 0 -i. chmod {p['r']} ."])
        self.pipe_command([f"sudo find {target_dir} -type d",
                           f"sudo xargs -P 0 -i. chown {p['user'][0]}:{p['user'][1]} ."])
        self.pipe_command([f"sudo find {target_dir} -type f",
                           f"sudo xargs -P 0 -i. chown {p['user'][0]}:{p['user'][1]} ."])

    def compress_custom_json(self):
        custom_dir = os.path.join(os.path.dirname(self.json_dir), "customer")
        if not os.path.isdir(custom_dir):
            return
        # 给予权限方便对文件做变更
        ret = self.run_command(f"chmod -R 777 {custom_dir}", sudo=True)
        if ret.returncode != 0:
            self.info(f"变更{self.intf}接口配置文件目录权限失败: {custom_dir}")
            return
        for root, _, files in os.walk(custom_dir):
            for file in files:
                if file.endswith(".json") and not os.path.islink(file):
                    file_path = os.path.join(root, file)
                    with open(file_path, mode='r', encoding='utf-8') as fp:
                        data = json.load(fp)
                    compact_json = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
                    with open(file_path, mode='w', encoding='utf-8') as fp:
                        fp.write(compact_json)
        # 变更完成恢复权限
        self.restore_permission(custom_dir)

    def json_to_lua_table(self, data, indent=0):
        lua = ""
        if isinstance(data, dict):
            if not data:
                return "{}"
            lua += "{"
            for key, value in data.items():
                lua += f'["{key}"]={self.json_to_lua_table(value, indent + 1)},'
            lua += f'}}'
        elif isinstance(data, list):
            if not data:
                return "{}"
            lua += "{"
            for i, value in enumerate(data, start=1):
                lua += f'[{i}]={self.json_to_lua_table(value, indent + 1)},'
            lua += f'}}'
        elif isinstance(data, str):
            # 处理字符串中的特殊字符
            if data.startswith('"') and data.endswith('"'):
                data = data[1:-1]
            escaped_str = data.replace('&quot;', '"').replace('\\', '\\\\').replace('"', '\\"')
            escaped_str = escaped_str.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            lua += f'"{escaped_str}"'
        elif isinstance(data, bool):
            lua += "true" if data else "false"
        elif isinstance(data, (int, float)):
            lua += str(data)
        elif data is None:
            # 映射配置中读取到值为None时，转换为cjson.null，避免与lua nil混淆
            lua += "cjson.null"
        else:
            raise TypeError(f"Unsupported data type: {type(data)}")
        return lua
                        
    def json_to_lua(self, lua_file_path, lua_mapper_file_path, lua_route_tree_path):
        json_files = self.get_sorted_json_files(self.json_dir)
        lua_content = "Input.data="
        mapper_content = "Input.data="
        lua = {}
        mapper = {}
        if self.intf == misc.CLI:
            route_tree_content = "Input.data="
            route_tree = {}
        for json_file in json_files:
            with open(json_file, 'r') as f:
                data = json.load(f)
            relative_path_list = self.get_relative_path_paths(self.json_dir, json_file)
            
            for resource in data.get("Resources", []):
                uri = resource.get("Uri")
                if uri is None:
                    continue
                # redfish接口需要获取uri的IgnoreEtags配置，默认为空列表
                if self.intf == "redfish":
                    ignore_etags = resource.get("IgnoreEtags", [])
                    self.set_dict_value(relative_path_list + [uri], "IgnoreEtags", ignore_etags, mapper)
                for key, value in resource.items():
                    if key in ["Uri", "IgnoreEtags", "Interfaces"]:
                        continue
                    self.set_dict_value([uri], key, value, lua)
                for interface in resource.get("Interfaces", []):
                    method_type = interface.get("Type")
                    if method_type is None:
                        continue
                    method_type = method_type.lower()
                    self.set_dict_value(relative_path_list + [uri], method_type, True, mapper)
                    if self.intf == misc.CLI:
                        self.set_dict_value(uri.split('/')[1:] + ['#methods'], method_type, True, route_tree)
                    lock_down_allow = interface.get("LockDownAllow")
                    if lock_down_allow is not None and method_type == 'get':
                        lock_down_allow = True
                    if lock_down_allow is not None:
                        lua_str = self.json_to_lua_table(lock_down_allow, 4)
                        self.set_dict_value([uri, 'methods', method_type], 'LockDownAllow', lua_str, lua)
                    rsp_body = interface.get("RspBody")
                    # redfish接口响应体需要保序，转为字符串
                    if rsp_body is not None and self.intf == 'redfish':
                        self.set_dict_value([uri, 'methods', method_type], 'RspBody', json.dumps(rsp_body), lua)
                    elif rsp_body is not None:
                        self.set_dict_value([uri, 'methods', method_type], 'RspBody', rsp_body, lua)
                    req_body = interface.get("ReqBody")
                    if req_body is not None and self.intf == misc.CLI:
                        self.set_dict_value([uri, 'methods', method_type], 'ReqBody', json.dumps(req_body), lua)
                    elif req_body is not None:
                        self.set_dict_value([uri, 'methods', method_type], 'ReqBody', req_body, lua)
                    action_rsp_body = interface.get("ActionResponseBody")
                    if action_rsp_body is not None:
                        lua_str = self.json_to_lua_table(json.dumps(action_rsp_body), 4)
                        self.set_dict_value([uri, 'methods', method_type], 'ActionResponseBody', lua_str, lua)
                    processing_flow = interface.get("ProcessingFlow")
                    if processing_flow is not None:
                        for pf_item in processing_flow:
                            # 对象结构的CallIf有前后依赖关系，需要转为字符串
                            if "CallIf" in pf_item:
                                pf_item["CallIf"] = json.dumps(pf_item["CallIf"])
                    for key, value in interface.items():
                        if key in ["Type", "RspBody", "ReqBody", "ActionResponseBody", "LockDownAllow"]:
                            continue
                        self.set_dict_value([uri, 'methods', method_type], key, value, lua)
        mapper_content += f"{self.json_to_lua_table(mapper, 0)}"
        lua_content += f"{self.json_to_lua_table(lua, 0)}"
        if self.intf == misc.CLI:
            route_tree_content += f"{self.json_to_lua_table(route_tree, 0)}"
            directory = os.path.dirname(lua_route_tree_path)
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(lua_route_tree_path, 'w') as f:
                f.write(route_tree_content)
                self.info('{} package precompilation route tree file to {} successfully'\
                            .format(self.intf, lua_route_tree_path))
        directory = os.path.dirname(lua_file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(lua_file_path, 'w') as f:
            f.write(lua_content)
            self.info('{} package precompilation config file to {} successfully'.format(self.intf, lua_file_path))
        directory = os.path.dirname(lua_mapper_file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(lua_mapper_file_path, 'w') as f:
            f.write(mapper_content)
            self.info('{} package precompilation mapper file to {} successfully'\
                            .format(self.intf, lua_mapper_file_path))
            
    def run(self):
        if not os.path.isdir(self.json_dir):
            self.info(f"{self.intf}接口配置文件目录不存在: {self.json_dir}")
            return
    
        # 给予权限方便对文件做变更
        ret = self.run_command(f"chmod -R 777 {self.json_dir}", sudo=True)
        if ret.returncode != 0:
            self.info(f"变更{self.intf}接口配置文件目录权限失败: {self.json_dir}")
            return
        
        lua_file_path = os.path.join(self.json_dir, "config.lua")
        lua_mapper_file_path = os.path.join(self.json_dir, "mapper.lua")
        if self.intf == misc.CLI:
            lua_route_tree_path = os.path.join(self.json_dir, "route_tree.lua")
            self.json_to_lua(lua_file_path, lua_mapper_file_path, lua_route_tree_path)
        else:
            self.json_to_lua(lua_file_path, lua_mapper_file_path, None)
            
        # 变更完成恢复权限
        self.restore_permission(self.json_dir)