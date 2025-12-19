# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#          http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
import os
import json
import stat

from conan import ConanFile
from conan.tools.files import copy, load


class BingoCasesConan(ConanFile):
    name = "bingo_cases"
    user = "openubmc"
    channel = "stable"
    settings = None
    exports_sources = ["cases.yml", "cases_template_valid.json"]

    def set_version(self):
        import jsonschema

        cases_data = self._load_cases_data()
        # 验证cases模板
        valid_content = load(self, "cases_template_valid.json")
        valid_data = json.loads(valid_content)
        jsonschema.validate(cases_data, valid_data)

        self.version = cases_data["version"]

    def build(self):
        import yaml

        cases_data = self._load_cases_data()
        with os.fdopen(
            os.open(
                "cases.yml",
                os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                stat.S_IWUSR | stat.S_IRUSR,
            ),
            "w",
        ) as file_handler:
            yaml.dump(cases_data, file_handler, encoding="utf-8", allow_unicode=True)

    def package(self):
        copy(self, "cases.yml", self.build_folder, self.package_folder)

    def _load_cases_data(self):
        import yaml

        # 从 case.yml 文件读取
        cases_content = load(self, "cases.yml")
        return yaml.safe_load(cases_content)
