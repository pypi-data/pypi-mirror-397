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
TEST_DATA_FILE = 'test_data.json'


class TestDataSave:
    def __init__(self, test_data, output_dir_path):
        """
        初始化测试数据保存器

        Args:
            test_data: 要保存的测试数据
            output_dir_path: 输出目录路径
        """
        self.test_data = test_data
        self.output_dir_path = output_dir_path

    def save(self):
        """
        保存测试数据到JSON文件
        """
        try:
            # 使用传入的输出目录路径，在其下创建 test_data 子目录
            test_data_dir = os.path.join(self.output_dir_path, 'test_data')
            # 确保目录存在
            os.makedirs(test_data_dir, exist_ok=True)
            # 构建文件路径
            file_path = os.path.join(test_data_dir, TEST_DATA_FILE)
            # 写入JSON文件
            with open(file_path, 'w') as f:
                json.dump(self.test_data, f, indent=4)
            logging.info(f"测试数据已成功保存到 {file_path}")
        except Exception as e:
            logging.error(f"保存测试数据到 {TEST_DATA_FILE} 时出错: {e}")