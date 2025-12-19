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
import os
import json

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
DBUS_MOCK_DATA_FILE_NAME = 'mock_data.json'


class MockDataSaver:
    """
    用于保存mock数据和信号数据的类
    """
    def __init__(self, service_prefix):
        # 不再需要name_to_service参数
        self.service_prefix = service_prefix
        # 服务名集合将在处理过程中动态收集
        self.service_names = set()

    @staticmethod
    def _save_service_data(mock_data, service_name, output_dir_path):
        """
        保存单个服务的数据

        :param mock_data: 该服务的mock数据
        :param signals: 该服务的信号数据
        :param service_name: 服务名
        :param output_dir_path: 输出目录路径
        """
        # 创建服务目录
        service_dir = os.path.join(output_dir_path, service_name.replace('.', '_'))
        os.makedirs(service_dir, exist_ok=True)

        # 分别保存mock数据和信号数据
        MockDataSaver._save_mock_data(mock_data, service_name, service_dir)

    @staticmethod
    def _save_mock_data(mock_data, service_name, service_dir):
        """
        保存单个服务的mock数据

        :param mock_data: 该服务的mock数据
        :param service_name: 服务名
        :param service_dir: 服务目录路径
        """
        # 当mock_data为空时，直接返回不保存文件
        if not mock_data:
            logging.info(f"  服务 {service_name} 没有mock数据，跳过保存")
            return

        # 保存mock数据
        mock_file_path = os.path.join(service_dir, DBUS_MOCK_DATA_FILE_NAME)
        # 读取现有mock数据（如果存在）
        existing_mock_data = {}
        if os.path.exists(mock_file_path):
            try:
                with open(mock_file_path, 'r', encoding='utf-8') as in_f:
                    existing_mock_data = json.load(in_f)
            except (json.JSONDecodeError, IOError) as e:
                logging.warning(f"  警告: 读取现有mock数据文件时出错 {e}，将覆盖文件")

        # 合并新数据与现有数据
        for key, calls in mock_data.items():
            if key in existing_mock_data:
                # 如果键已存在，将新调用追加到现有调用列表
                existing_mock_data[key].extend(calls)
            else:
                # 如果键不存在，直接添加
                existing_mock_data[key] = calls

        # 保存合并后的mock数据
        with open(mock_file_path, 'w', encoding='utf-8') as out_f:
            json.dump(existing_mock_data, out_f, indent=4, ensure_ascii=False)
        logging.info(f"  已保存 {service_name} 的mock数据到 {mock_file_path}")

    def save_mock_data(self, mock_data, output_dir_path):
        # 从mock_data的key中收集服务名
        for key in mock_data.keys():
            parts = key.split('|')
            if len(parts) >= 1:
                service_name = parts[0]
                if service_name.startswith(self.service_prefix):
                    self.service_names.add(service_name)

        # 初始化各服务的数据存储
        service_mock_data = {service: {} for service in self.service_names}

        # 分类数据到各服务
        self._categorize_data_by_service(
            mock_data,
            service_mock_data
        )

        # 保存各服务的数据
        for service_name in self.service_names:
            MockDataSaver._save_service_data(
                service_mock_data[service_name],
                service_name,
                output_dir_path
            )

    def _categorize_data_by_service(self, mock_data, service_mock_data):
        """
        将数据按服务名分类存储

        :param mock_data: mock数据
        :param signals: 信号数据
        :param service_mock_data: 各服务的mock数据存储
        :param service_signals: 各服务的信号数据存储
        """
        # 分类mock数据 - 直接从key中提取服务名
        for key, calls in mock_data.items():
            # 从key中提取服务名（第一部分）
            parts = key.split('|')
            if len(parts) >= 1:
                service_name = parts[0]

                # 检查服务名是否以service_prefix开头并且已在service_mock_data中
                if service_name.startswith(self.service_prefix) and service_name in service_mock_data:
                    if key not in service_mock_data[service_name]:
                        service_mock_data[service_name][key] = []
                    service_mock_data[service_name][key].extend(calls)

    def _save_data_by_service(self, mock_data, output_dir_path):
        """
        按服务名分别存储数据

        :param mock_data: mock数据
        :param signals: 信号数据
        :param output_dir_path: 输出目录路径
        """
        # 直接从mock_data的key中收集服务名
        service_names = set()

        # 从mock数据中收集服务名
        for key in mock_data.keys():
            parts = key.split('|')
            if len(parts) >= 1:
                service_name = parts[0]
                if service_name.startswith(self.service_prefix):
                    service_names.add(service_name)

        # 为每个服务创建数据存储
        service_mock_data = {service: {} for service in service_names}

        # 分类mock数据
        for key, calls in mock_data.items():
            parts = key.split('|')
            if len(parts) >= 1:
                service_name = parts[0]
                if service_name.startswith(self.service_prefix) and service_name in service_mock_data:
                    service_mock_data[service_name][key] = calls
        # 保存各服务的数据
        for service_name in service_names:
            MockDataSaver._save_service_data(
                service_mock_data[service_name],
                service_name,
                output_dir_path
            )
