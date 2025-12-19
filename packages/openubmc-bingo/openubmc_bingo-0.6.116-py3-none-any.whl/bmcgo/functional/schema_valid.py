#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 描述：检查当前目录下, .yml/.yaml 文件是否符合配置的 schema 规范
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
import argparse
import re

import yaml
import jsonschema
from jsonschema import exceptions as jc

from bmcgo.logger import Logger
from bmcgo.bmcgo_config import BmcgoConfig
from bmcgo import misc
from bmcgo.errors import BmcGoException

log = Logger()
command_info: misc.CommandInfo = misc.CommandInfo(
    group=misc.GRP_MISC,
    name="schema_validate",
    description=["对指定目录下所有yaml/json文件或指定yaml/json文件进行 schema 规范检查"],
    hidden=True
)
JSON_TYPE = "json"
YML_TYPE = "yml"
SCHEMA_FILES_DIR_PATH = "/usr/share/bingo/schema"


def load_json_safely(check_file):
    try:
        with open(check_file, "r") as fp:
            check_data = json.load(fp)
        return check_data
    except json.JSONDecodeError as e:
        log.info(f"Failed to parse JSON file {check_file} : {e}")
        return None
    except FileNotFoundError:
        log.info(f"File not found: {check_file}")
        return None
    except Exception as e:
        log.info(f"Unexpected error reading {check_file} : {e}")
        return None


def if_available(_: BmcgoConfig):
    return True


class BmcgoCommand:
    def __init__(self, bconfig: BmcgoConfig, *args):
        """ yaml 文件根据 schema 文件进行规则检查

        Args:
            bconfig (BmcgoConfig): bmcgo 配置
        """
        self.bconfig = bconfig
        parser = argparse.ArgumentParser(prog=f"{misc.tool_name()} schema_valid", description="Validate yaml files",
                                         add_help=True, formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-t", "--target", help="目标文件夹或单个yaml文件，默认当前目录", default=".")
        parser.add_argument("-csr", "--csr", help="仅校验.sr文件", action=misc.STORE_TRUE, default=False)

        parsed_args = parser.parse_args(*args)
        self.target = os.path.realpath(parsed_args.target)
        self.csr_pattern = parsed_args.csr

    @staticmethod
    def get_schema_in_json(check_file: str):
        check_data = load_json_safely(check_file)
        if check_data:
            schema_file = check_data.get("$schema", "")
            if schema_file:
                return schema_file

        cwd = os.getcwd()
        os.chdir(os.path.dirname(check_file))
        bconfig = BmcgoConfig()
        os.chdir(cwd)
        if bconfig.component and (os.path.dirname(check_file) == os.path.join(bconfig.component.folder, "mds")
                                  or os.path.join(bconfig.component.folder, "mds", "debug")):
            check_file_name, _ = os.path.basename(check_file).rsplit(".", 1)
            schema_file = f"{SCHEMA_FILES_DIR_PATH}/mds.{check_file_name}.schema.v1.json"
            if os.path.isfile(schema_file):
                return schema_file
        if bconfig.component and "json/intf/mdb" in check_file:
            schema_file = f"{SCHEMA_FILES_DIR_PATH}/interface.schema.json"
            if os.path.isfile(schema_file):
                return schema_file
        if bconfig.component and "json/intf/mdb" in check_file:
            schema_file = f"{SCHEMA_FILES_DIR_PATH}/path.schema.json"
            if os.path.isfile(schema_file):
                return schema_file
        if bconfig.component and check_file.endswith(".sr"):
            schema_file = f"{SCHEMA_FILES_DIR_PATH}/csr.schema.json"
            if os.path.isfile(schema_file):
                return schema_file
        return None

    @staticmethod
    def get_decleared_schema_file(check_file: str, file_type=YML_TYPE):
        if file_type == JSON_TYPE:
            return BmcgoCommand.get_schema_in_json(check_file)
        return misc.get_decleared_schema_file(check_file)

    @staticmethod
    def schema_valid(check_file: str, file_type=YML_TYPE) -> bool:
        """ 有效性校验

        Args:
            check_file (str): 要校验的文件名称
        """
        schema_file = BmcgoCommand.get_decleared_schema_file(check_file, file_type)
        if not schema_file:
            log.warning(f"文件 {check_file} 没有配置 schema 检查")
            return True

        http_regex = r'^https?://.*'
        if re.match(http_regex, schema_file):
            log.warning(f"文件 {check_file} 配置的 {schema_file} 为外部schema, 跳过检查")
            return True

        schema_file_path = os.path.join(os.path.dirname(check_file), schema_file)
        if not os.path.isfile(schema_file_path):
            raise BmcGoException(f"schema校验文件 {schema_file_path} 不存在")

        log.debug("开始校验文件：%s", check_file)
        with open(schema_file, "rb") as fp:
            schema = json.load(fp)
        with open(check_file, "r") as fp:
            if file_type == JSON_TYPE:
                try:
                    check_data = json.load(fp)
                except Exception as e:
                    log.info(f"解析JSON文件失败：{check_file}, 错误：{e}")
                    return False
            else:
                check_data = yaml.safe_load(fp)

        try:
            jsonschema.validate(check_data, schema)
            log.debug("校验成功：%s", check_file)
            return True
        except (jc.ValidationError, jc.SchemaError) as e:
            if os.path.basename(check_file) != 'service.json':
                log.warning(f" >>>>>> {check_file} 校验失败 <<<<<<\n{e}")
                return True
            log.error(f" >>>>>> {check_file} 校验失败 <<<<<<\n{e}")
            return False

    @staticmethod
    def _is_yml_file(filename):
        if filename.endswith((".yml", ".yaml")):
            return True
        return False

    def run(self):
        """ 分析参数并启动校验
        """
        check_result = []

        if os.path.isfile(self.target):
            if str(self.target).endswith(".sr"):
                check_result.append(self.schema_valid(self.target, "json"))
            else:
                check_result.append(self.schema_valid(self.target))
            return 0
        check_result = self._validate_yml_files()

        if check_result and False in check_result:
            log.error("请仔细阅读报错日志, 日志中会提示哪些是必要属性, 或哪个属性配置错误")
            raise AttributeError(f"所有 .yml/.yaml 文件检查失败, 请仔细检查报错并解决问题项")
        if not check_result:
            if self.csr_pattern:
                log.warning("未找到csr文件")
            else:
                log.warning("未找到yml文件")
        return 0

    def _validate_yml_files(self):
        check_result = []
        if not os.path.exists(self.target):
            raise BmcGoException(f"文件或者目录{self.target}不存在")
        for root, _, files in os.walk(self.target):
            for filename in files:
                schema_file = os.path.join(root, filename)
                if "test" in schema_file.split(os.sep):
                    continue
                file_type = None
                if self._is_yml_file(filename) and not self.csr_pattern:
                    file_type = YML_TYPE
                elif filename.endswith(".json") and not self.csr_pattern:
                    file_type = JSON_TYPE
                elif filename.endswith(".sr") and self.csr_pattern:
                    file_type = JSON_TYPE
                else:
                    continue
                check_result.append(self.schema_valid(schema_file, file_type))
        return check_result
