#!/usr/bin/env python3
# encoding=utf-8
# 描述：HPM 文件重签名功能
# Copyright (c) 2025 Huawei Technologies Co., Ltd.
# openUBMC is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#         http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

import os
import struct
import subprocess
import shutil
import argparse
from pathlib import Path

from bmcgo import misc
from bmcgo.utils.tools import Tools
from bmcgo.bmcgo_config import BmcgoConfig

tools = Tools("HPMResigner")
logger = tools.log

#========== 可调默认项 ==========
CMD = "bingo"
# DEFAULT_CA_DIR = "/root/ca"                  # 证书目录默认值（可被 --ca-dir 覆盖）
DEFAULT_CA_DIR = str(Path.home() / "ca")  # 证书目录默认位于用户家目录下
DEFAULT_OUT_SUFFIX = "_signed.hpm"  # 输出文件名默认后缀（可按需改）
TMP_DIR_NAME = "hpm_tmp"                   # 源文件同目录下的临时目录名

command_info: misc.CommandInfo = misc.CommandInfo(
    group=misc.GRP_MISC,
    name="hpm_signer",
    description=["HPM 文件重签名"],
    hidden=False
)


def if_available(bconfig: BmcgoConfig):
    return True


def get_desc(cmd):
    return f"""
HPM 文件重签名工具:

>> {cmd} hpm_resign <HPM文件> [--ca-dir /path/to/ca] [--out new_name.hpm] [--keep-tmp] [--signer-pass <签名证书加密密码>]

说明:
  1) 请确保已安装 hpm_verify 和 hpm_signer 工具
  2) 证书目录默认位于用户家目录 ca 目录下 (可使用 --ca-dir 参数指定其他目录)
  3) 证书目录(--ca-dir)下需包含: rootca.der, rootca.crl, signer.pem, (可选) ts_signer.pem, tsa.cnf
  4) 如果签名证书已加密，需要使用 --signer-pass 参数提供密码
  5) 临时文件与输出文件默认位于源 HPM 文件同目录
"""


class BmcgoCommand:
    def __init__(self, bconfig: BmcgoConfig, *args):
        self.bconfig = bconfig
        parser = argparse.ArgumentParser(
            prog=f"{CMD} HPM重签名",
            description=get_desc(CMD),
            add_help=True,
            formatter_class=argparse.RawTextHelpFormatter
        )
        parser.add_argument(
            "hpm_file",
            type=Path,
            help="HPM文件路径"
        )
        parser.add_argument(
            "--keep-tmp",
            action="store_true",
            help="保留临时文件"
        )
        parser.add_argument(
            "--ca-dir",
            type=Path,
            default=Path(DEFAULT_CA_DIR),
            help=f"证书目录(默认: {DEFAULT_CA_DIR})"
        )
        parser.add_argument(
            "--out",
            type=str,
            default=None,
            help=f"输出文件名(默认: <源名>{DEFAULT_OUT_SUFFIX})"
        )
        parser.add_argument(  
            "--signer-pass",
            type=str,
            default=None,
            help="签名证书的加密密码（如果证书已加密）"
        )

        self.args, self.kwargs = parser.parse_known_args(*args)
        self.logger = tools.log

        # 运行期路径属性（在 run/main 中初始化）
        self.base_dir: Path = None
        self.tmp_dir: Path = None

    @staticmethod
    def write_ascii_hex(fp, value: int):
        """按 8 位 0 补齐十六进制，写入 ASCII 字符串"""
        fp.write(f"{value:08x}".encode())

    def run(self):
        hpm_file = self.args.hpm_file
        if not hpm_file.exists():
            self.logger.error(f"ERROR: 文件 {hpm_file} 不存在")
            return 1

        # 源文件同目录
        self.base_dir = hpm_file.parent.resolve()
        # 临时目录放在源文件同目录
        self.tmp_dir = (self.base_dir / TMP_DIR_NAME).resolve()

        try:
            # 在主要操作前进行权限检查
            if not self.check_permissions(hpm_file):
                self.logger.error("权限检查失败，程序退出")
                return 1
                
            self.main(hpm_file)
            return 0
        except Exception as e:
            self.logger.error(f"处理过程中发生错误: {str(e)}")
            import traceback
            self.logger.debug(f"详细堆栈: {traceback.format_exc()}")
            return 1
        finally:
            if not self.args.keep_tmp:
                self.clear_temp()

    def check_permissions(self, hpm_file: Path) -> bool:
        """检查必要的文件和目录权限"""
        self.logger.info(">>> 开始权限检查...")
        
        # 检查源文件读取权限
        if not os.access(hpm_file, os.R_OK):
            self.logger.error(f"ERROR: 无读取权限: {hpm_file}")
            return False
        self.logger.info(f"SUCCESS: 源文件可读: {hpm_file}")

        # 检查源文件所在目录的写入权限（用于创建临时目录和输出文件）
        if not os.access(self.base_dir, os.W_OK):
            self.logger.error(f"ERROR: 无写入权限: {self.base_dir}")
            return False
        self.logger.info(f"SUCCESS: 目录可写: {self.base_dir}")

        # 检查证书目录权限
        ca_dir = self.args.ca_dir.resolve()
        if not ca_dir.exists():
            self.logger.error(f"ERROR: 证书目录不存在: {ca_dir}")
            return False
            
        if not os.access(ca_dir, os.R_OK):
            self.logger.error(f"ERROR: 无读取权限: {ca_dir}")
            return False
        self.logger.info(f"SUCCESS: 证书目录可读: {ca_dir}")

        # 检查必要的证书文件
        required_ca_files = [
            ("rootca.der", "根证书"),
            ("rootca.crl", "CRL文件"), 
            ("signer.pem", "签名证书")
        ]
        
        for filename, desc in required_ca_files:
            file_path = ca_dir / filename
            if not file_path.exists():
                self.logger.error(f"ERROR: {desc}不存在: {file_path}")
                return False
            if not os.access(file_path, os.R_OK):
                self.logger.error(f"ERROR: 无读取权限: {file_path}")
                return False
            self.logger.info(f"SUCCESS: {desc}可读: {filename}")

        # 检查可选的时间戳证书文件
        optional_files = [
            ("ts_signer.pem", "时间戳证书"),
            ("tsa.cnf", "时间戳配置")
        ]
        
        for filename, desc in optional_files:
            file_path = ca_dir / filename
            if file_path.exists():
                if not os.access(file_path, os.R_OK):
                    self.logger.warning(f"WARNING: 无读取权限(可选): {file_path}")
                else:
                    self.logger.info(f"SUCCESS: {desc}可读: {filename}")
            else:
                self.logger.warning(f"WARNING: {desc}不存在(可选): {filename}")

        # 检查输出文件权限（如果文件已存在）
        out_name = self.args.out if self.args.out else f"{hpm_file.stem}{DEFAULT_OUT_SUFFIX}"
        new_hpm = self.base_dir / out_name
        if new_hpm.exists():
            if not os.access(new_hpm, os.W_OK):
                self.logger.error(f"ERROR: 输出文件已存在且无写入权限: {new_hpm}")
                return False
            self.logger.info(f"SUCCESS: 输出文件可覆盖: {new_hpm}")

        self.logger.info(">>> 权限检查通过!")
        return True

    def main(self, hpm_file: Path):
        # 创建必要目录（源目录下）
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

        base_name = hpm_file.stem
        self.logger.info(f"源文件: {hpm_file}")

        # 计算默认输出文件路径（同目录）
        out_name = self.args.out if self.args.out else f"{base_name}{DEFAULT_OUT_SUFFIX}"
        new_hpm = (self.base_dir / out_name).resolve()

        # 1. 解析HPM文件头
        self.logger.info("\n>>> 开始解析HPM文件...")
        with open(hpm_file, 'rb') as f:
            header_data = f.read(56)
            if len(header_data) != 56:
                self.logger.error(f"ERROR: 文件太小 ({len(header_data)}字节)，无法解析头部信息！")
                return

            try:
                header_bin = bytes.fromhex(header_data.decode('ascii'))
            except Exception as e:
                raise RuntimeError("头部数据不是合法的 ASCII Hex") from e

            if len(header_bin) != 28:
                raise RuntimeError(f"头部数据长度不合法 {len(header_bin)}，期望 56")

            header_ints = struct.unpack('>7I', header_bin)
            magic, section_count, filelist_len, _, cms_len, _, crl_len = header_ints

            skip1 = 56
            skip2 = skip1 + filelist_len
            skip3 = skip2 + cms_len
            skip4 = skip3 + crl_len

            self.logger.info(f"\n>>> 开始计算偏移量...")

        # 2. 提取各部分（放到源目录的 tmp 下）
        self.logger.info(f"\n>>> 开始提取文件...")

        filelist_path = self.tmp_dir / f"{base_name}.filelist"
        cms_path = self.tmp_dir / f"{base_name}.cms"
        crl_path = self.tmp_dir / f"{base_name}.crl"
        bin_path = self.tmp_dir / f"{base_name}.bin"

        if self.extract_part(hpm_file, skip1, filelist_len, filelist_path):
            self.logger.info(f"SUCCESS: 成功提取filelist到 {filelist_path}")
        if self.extract_part(hpm_file, skip2, cms_len, cms_path):
            self.logger.info(f"SUCCESS: 成功提取cms到 {cms_path}")
        if self.extract_part(hpm_file, skip3, crl_len, crl_path):
            self.logger.info(f"SUCCESS: 成功提取crl到 {crl_path}")
        if self.extract_to_end(hpm_file, skip4, bin_path):
            self.logger.info(f"SUCCESS: 成功提取bin到 {bin_path}")

        required_files = [filelist_path, cms_path, crl_path, bin_path]
        if not self.all_files_exist(required_files):
            self.logger.error(f"ERROR: 部分文件提取失败！")
            return

        # --- 执行 openssl 证书和 CRL 转换（来自 --ca-dir）---
        ca_dir: Path = self.args.ca_dir.resolve()
        der_cert = ca_dir / "rootca.der"
        der_crl = ca_dir / "rootca.crl"
        pem_cert = self.tmp_dir / "rootca.pem"
        pem_crl = self.tmp_dir / "cms.crl.pem"

        # 转换 rootca.der 为 rootca.pem
        if der_cert.exists():
            cmd_cert = [
                "openssl", "x509",
                "-in", str(der_cert),
                "-inform", "der",
                "-outform", "pem",
                "-out", str(pem_cert)
            ]
            self.logger.info("\n>>> " + " ".join(cmd_cert))
            try:
                subprocess.run(cmd_cert, check=True)
                self.logger.info(f"SUCCESS: 生成 PEM 证书 {pem_cert}")
            except Exception as e:
                self.logger.error(f"ERROR: 证书转换失败: {e}")
        else:
            self.logger.error(f"ERROR: 未找到 DER 证书文件 {der_cert}")

        # 转换 rootca.crl 为 cms.crl.pem
        if der_crl.exists():
            cmd_crl = [
                "openssl", "crl",
                "-in", str(der_crl),
                "-inform", "der",
                "-outform", "pem",
                "-out", str(pem_crl)
            ]
            self.logger.info(">>> " + " ".join(cmd_crl))
            try:
                subprocess.run(cmd_crl, check=True)
                self.logger.info(f"SUCCESS: 生成 PEM CRL {pem_crl}")
            except Exception as e:
                self.logger.error(f"ERROR: CRL转换失败: {e}")
        else:
            self.logger.error(f"ERROR: 未找到 DER CRL 文件 {der_crl}")

        # 3. 重新签名filelist
        self.logger.info(f"\n>>> 开始重新签名...")
        signer_pem = ca_dir / "signer.pem"
        ts_signer_pem = ca_dir / "ts_signer.pem"
        tsa_cnf = ca_dir / "tsa.cnf"
        cms1_path = self.tmp_dir / f"{base_name}.cms1"

        if not signer_pem.exists():
            self.logger.error(f"ERROR: 签名证书 {signer_pem} 不存在")
            return

        # 构建签名命令 - 只在时间戳证书存在时添加时间戳参数
        cmd = [
            "hpm_signer",
            "-s", str(signer_pem),
            "-i", str(filelist_path),
            "-o", str(cms1_path)
        ]
        
        # 只有在时间戳证书和配置文件都存在时才添加时间戳参数
        if ts_signer_pem.exists() and tsa_cnf.exists():
            cmd.extend(["-t", str(ts_signer_pem), "-T", str(tsa_cnf)])
            self.logger.info(">>> 使用时间戳签名")
        else:
            self.logger.info(">>> 使用基础签名（无时间戳）")
        
        # 添加密码参数（如果提供了密码）
        if self.args.signer_pass:
            cmd.extend(["-p", self.args.signer_pass])
            self.logger.info(">>> 使用加密签名证书")
            
        self.logger.info(">>> " + " ".join(cmd))

        try:
            subprocess.run(cmd, check=True)
            self.logger.info(f">>> SUCCESS: 重新签名成功!")
            # --- 签名成功后自动验证 ---
            self.logger.info(f"\n>>> 开始验证签名...")
            verify_cmd = [
                "hpm_verify",
                "-r", str(pem_cert),
                "-C", str(pem_crl),
                "-c", str(filelist_path),
                "-s", str(cms1_path)
            ]
            self.logger.info(">>> " + " ".join(verify_cmd))
            try:
                subprocess.run(verify_cmd, check=True)
                self.logger.info(f">>> SUCCESS: 签名验证通过!")
            except subprocess.CalledProcessError:
                self.logger.error(f">>> ERROR: 签名验证失败!")
            except FileNotFoundError:
                self.logger.error(f">>> ERROR: hpm_verify 命令未找到")
        except subprocess.CalledProcessError:
            self.logger.error(f">>> ERROR: 重新签名失败!")
            return
        except FileNotFoundError:
            self.logger.error(f">>> ERROR: hpm_signer 命令未找到")
            return

        # 4. 重新打包HPM文件（输出到源目录）
        self.logger.info(f"\n>>> 开始重新打包HPM文件...")
        rootca_crl = der_crl
        filelist_size = filelist_path.stat().st_size
        cms1_size = cms1_path.stat().st_size
        crl_size = rootca_crl.stat().st_size
        bin_size = bin_path.stat().st_size

        # 检查输出文件写入权限
        try:
            with open(new_hpm, "wb") as out_f:
                # 写入头部 (ASCII hex)
                out_f.write(b"00000003")  # magic
                out_f.write(b"00000001")  # section_count
                self.write_ascii_hex(out_f, filelist_size)  # filelist长度
                out_f.write(b"00000002")
                self.write_ascii_hex(out_f, cms1_size)      # cms长度
                out_f.write(b"00000003")
                self.write_ascii_hex(out_f, crl_size)       # crl长度

                # 依次写入各部分内容
                for part in [filelist_path, cms1_path, rootca_crl, bin_path]:
                    with open(part, "rb") as pf:
                        shutil.copyfileobj(pf, out_f)

            self.logger.info(f">>> SUCCESS: 成功打包HPM文件到: {new_hpm}")
        except PermissionError as e:
            self.logger.error(f">>> ERROR: 无权限写入输出文件: {new_hpm}")
            raise
        except Exception as e:
            self.logger.error(f">>> ERROR: 写入输出文件失败: {e}")
            raise


    def clear_temp(self):
        """清理临时目录（源目录下的 tmp）"""
        if self.tmp_dir and self.tmp_dir.exists():
            self.logger.info(f"\n>>> 清理临时文件和目录 {self.tmp_dir} 及同目录序列文件(serial)...")
            try:
                # 检查临时目录删除权限
                if os.access(self.tmp_dir, os.W_OK):
                    shutil.rmtree(self.tmp_dir)
                    self.logger.info(f"SUCCESS: 已删除 {self.tmp_dir} 及其所有文件")
                else:
                    self.logger.warning(f"WARNING: 无权限删除临时目录: {self.tmp_dir}")
                    
                serial_file = (self.base_dir / "serial")
                if serial_file.exists() and serial_file.is_file():
                    if os.access(serial_file, os.W_OK):
                        serial_file.unlink()
                        self.logger.info(f"SUCCESS: 已删除序列文件: {serial_file}")
                    else:
                        self.logger.warning(f"WARNING: 无权限删除序列文件: {serial_file}")
            except Exception as e:
                self.logger.error(f"ERROR: 删除临时目录和文件失败: {e}")
        else:
            self.logger.info("INFO: 临时目录不存在，无需清理")

    def extract_part(self, source: Path, skip: int, count: int, dest: Path):
        """提取文件的指定部分"""
        self.logger.info(f"提取文件: {dest} (skip={skip}, count={count})")
        cmd = ["dd", f"if={str(source)}", f"of={str(dest)}", "bs=1",
               f"skip={skip}", f"count={count}", "status=none"]
        try:
            subprocess.run(cmd, check=True)
            actual_size = dest.stat().st_size
            if actual_size == count:
                return True
            else:
                self.logger.error(f"ERROR:文件大小不匹配 ({actual_size} != {count})，文件名: {dest}")
                return False
        except subprocess.CalledProcessError:
            self.logger.error(f"ERROR: 提取文件失败，文件名: {dest}")
            return False
        except Exception as e:
            self.logger.error(f"ERROR: 提取文件异常，文件名: {dest}，原因: {str(e)}")
            return False

    def extract_to_end(self, source: Path, skip: int, dest: Path):
        """提取文件从指定位置到末尾"""
        self.logger.info(f"提取文件: {dest}")
        total_size = source.stat().st_size
        count = total_size - skip
        cmd = ["dd", f"if={str(source)}", f"of={str(dest)}", "bs=1",
               f"skip={skip}", f"count={count}", "status=none"]
        try:
            subprocess.run(cmd, check=True)
            actual_size = dest.stat().st_size
            if actual_size == count:
                return True
            else:
                self.logger.warning(f"WARNING: 文件大小不匹配 ({actual_size} != {count})，文件名: {dest}")
                return True
        except subprocess.CalledProcessError:
            self.logger.error(f"ERROR: 提取文件失败，文件名: {dest}")
            return False
        except Exception as e:
            self.logger.error(f"ERROR: 提取文件异常，文件名: {dest}，原因: {str(e)}")
            return False

    def all_files_exist(self, file_list):
        """检查所有文件是否存在"""
        missing = [f for f in file_list if not Path(f).exists()]
        if missing:
            self.logger.error("\nERROR: 以下文件缺失:")
            for f in missing:
                self.logger.error(f"  - {f}")
            return False
        self.logger.info("\nSUCCESS: 所有文件提取成功！")

        return True