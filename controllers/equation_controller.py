import pandas as pd
from datetime import datetime
from models.mapping_manager import MappingManager
from processors.excel_processor import ExcelProcessor
from typing import Tuple, List, Dict, Any
import os
import json


class EquationController:
    def __init__(self):
        self.mapping_manager = MappingManager()

        # Biến lưu trữ dữ liệu
        self.so_an = 2
        self.phien_ban = "fx799"
        self.he_so = []
        self.ket_qua_ma_hoa = []

        # Load equation prefixes (tập trung tại equation_prefixes.json)
        self.equation_prefixes_data = self._load_equation_prefixes()

    def _load_equation_prefixes(self, file_path: str = "config/equation_prefixes.json") -> dict:
        """Load tiền tố phương trình từ JSON với cấu trúc mới hỗ trợ nhiều phiên bản"""
        try:
            if not os.path.exists(file_path):
                return self._get_default_equation_prefixes()

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate cấu trúc file
            if "versions" not in data or "global_defaults" not in data:
                print(f"File {file_path} không có cấu trúc mong đợi, sử dụng mặc định")
                return self._get_default_equation_prefixes()

            return data

        except Exception as e:
            print(f"Lỗi khi đọc file equation_prefixes.json: {e}")
            return self._get_default_equation_prefixes()

    def _get_default_equation_prefixes(self) -> dict:
        """Trả về cấu hình mặc định nếu file không tồn tại hoặc lỗi"""
        return {
            "global_defaults": {
                "2": "w912",
                "3": "w913",
                "4": "w914"
            },
            "versions": {
                "fx799": {
                    "base_prefix": "wj",
                    "equation": {
                        "2": "wj912",
                        "3": "wj913",
                        "4": "wj914"
                    }
                },
                "fx880": {
                    "base_prefix": "kj",
                    "equation": {
                        "2": "kj912",
                        "3": "kj913",
                        "4": "kj914"
                    }
                },
                "fx801": {
                    "base_prefix": "yl",
                    "equation": {
                        "2": "yl912",
                        "3": "yl913",
                        "4": "yl914"
                    }
                },
                "fx802": {
                    "base_prefix": "zm",
                    "equation": {
                        "2": "zm912",
                        "3": "zm913",
                        "4": "zm914"
                    }
                },
                "fx803": {
                    "base_prefix": "an",
                    "equation": {
                        "2": "an912",
                        "3": "an913",
                        "4": "an914"
                    }
                }
            },
            "metadata": {
                "version": "2.0",
                "description": "Prefix Equation theo phiên bản máy và số ẩn"
            }
        }

    def get_equation_prefix(self, so_an: int) -> str:
        """Lấy tiền tố cho phiên bản máy và số ẩn cụ thể"""
        try:
            version = self.phien_ban
            so_an_str = str(so_an)

            # Lấy cấu hình phiên bản
            versions_config = self.equation_prefixes_data.get("versions", {})
            global_defaults = self.equation_prefixes_data.get("global_defaults", {})

            # Ưu tiên 1: Prefix chi tiết theo phiên bản và số ẩn
            if version in versions_config:
                version_config = versions_config[version]

                # Kiểm tra có equation config chi tiết không
                if "equation" in version_config and so_an_str in version_config["equation"]:
                    return version_config["equation"][so_an_str]

                # Ưu tiên 2: Tự sinh từ base_prefix + số ẩn
                base_prefix = version_config.get("base_prefix")
                if base_prefix and so_an_str in global_defaults:
                    # Lấy 3 số cuối từ global default (912, 913, 914)
                    global_suffix = global_defaults[so_an_str][-3:]
                    return f"{base_prefix}{global_suffix}"

            # Ưu tiên 3: Fallback về global defaults
            if so_an_str in global_defaults:
                return global_defaults[so_an_str]

            # Ưu tiên 4: Fallback cuối cùng (tương thích ngược)
            legacy_prefixes = self.equation_prefixes_data.get("prefixes", {})
            if so_an_str in legacy_prefixes:
                return legacy_prefixes[so_an_str]

            # Mặc định cuối cùng
            return "w912" if so_an == 2 else f"w91{so_an + 1}"

        except Exception as e:
            print(f"Lỗi khi lấy equation prefix: {e}")
            return f"w91{so_an + 1}"

    def get_version_info(self) -> dict:
        """Lấy thông tin chi tiết về phiên bản hiện tại"""
        try:
            versions_config = self.equation_prefixes_data.get("versions", {})

            if self.phien_ban in versions_config:
                version_config = versions_config[self.phien_ban]
                return {
                    "version": self.phien_ban,
                    "base_prefix": version_config.get("base_prefix", ""),
                    "equation_prefixes": version_config.get("equation", {}),
                    "description": version_config.get("description", f"Phiên bản {self.phien_ban}")
                }
            else:
                return {
                    "version": self.phien_ban,
                    "base_prefix": "",
                    "equation_prefixes": {},
                    "description": f"Phiên bản {self.phien_ban} (chưa cấu hình)"
                }

        except Exception as e:
            print(f"Lỗi khi lấy thông tin phiên bản: {e}")
            return {
                "version": self.phien_ban,
                "base_prefix": "",
                "equation_prefixes": {},
                "description": "Lỗi cấu hình"
            }

    def get_all_supported_versions(self) -> List[str]:
        """Lấy danh sách tất cả phiên bản được hỗ trợ"""
        try:
            versions_config = self.equation_prefixes_data.get("versions", {})
            return list(versions_config.keys())
        except Exception as e:
            print(f"Lỗi khi lấy danh sách phiên bản: {e}")
            return ["fx799", "fx880", "fx801", "fx802", "fx803"]

    def set_so_an(self, so_an):
        """Thiết lập số ẩn"""
        self.so_an = int(so_an)

    def set_phien_ban(self, phien_ban):
        """Thiết lập phiên bản máy tính"""
        self.phien_ban = phien_ban

    def set_he_so(self, danh_sach_he_so):
        """Thiết lập danh sách hệ số"""
        self.he_so = danh_sach_he_so

    def xu_ly_ma_hoa(self):
        """Xử lý mã hóa các hệ số"""
        try:
            self.ket_qua_ma_hoa = []

            for he_so in self.he_so:
                if he_so.strip():
                    ket_qua = self.mapping_manager.encode_string(he_so)
                    self.ket_qua_ma_hoa.append(ket_qua)
                else:
                    self.ket_qua_ma_hoa.append("")

            return self.ket_qua_ma_hoa

        except Exception as e:
            print(f"Lỗi khi mã hóa: {e}")
            return []

    def generate_final_equation_code(self) -> str:
        """Tạo mã hoàn chỉnh cho máy tính với prefix phiên bản"""
        try:
            if not self.ket_qua_ma_hoa:
                return "Chưa có kết quả mã hóa"

            # Lấy prefix theo phiên bản và số ẩn
            prefix = self.get_equation_prefix(self.so_an)

            # Nối các hệ số đã mã hóa
            encoded_coeffs = "".join(self.ket_qua_ma_hoa)

            # Kết hợp prefix + hệ số
            final_code = f"{prefix}{encoded_coeffs}"

            return final_code


        except Exception as e:
            print(f"Lỗi khi tạo mã cuối cùng: {e}")
            return f"Lỗi: {str(e)}"

    def get_export_info(self):
        """Lấy thông tin cho export"""
        version_info = self.get_version_info()
        final_code = self.generate_final_equation_code()

        return {
            "so_an": self.so_an,
            "phien_ban": self.phien_ban,
            "base_prefix": version_info["base_prefix"],
            "equation_prefix": self.get_equation_prefix(self.so_an),
            "he_so": self.he_so,
            "ket_qua_ma_hoa": self.ket_qua_ma_hoa,
            "final_code": final_code,
            "has_data": len(self.he_so) > 0,
            "version_description": version_info["description"]
        }

    def validate_version_support(self, version: str) -> dict:
        """Kiểm tra phiên bản có được hỗ trợ không"""
        supported_versions = self.get_all_supported_versions()

        return {
            "is_supported": version in supported_versions,
            "version": version,
            "supported_versions": supported_versions,
            "message": f"Phiên bản {version} {'được hỗ trợ' if version in supported_versions else 'chưa được hỗ trợ'}"
        }

    def reload_equation_prefixes(self):
        """Reload lại cấu hình prefix (hữu ích khi cập nhật file config)"""
        try:
            self.equation_prefixes_data = self._load_equation_prefixes()
            return True
        except Exception as e:
            print(f"Lỗi khi reload equation prefixes: {e}")
            return False

    def debug_prefix_info(self) -> dict:
        """Debug thông tin prefix cho tất cả số ẩn của phiên bản hiện tại"""
        result = {
            "current_version": self.phien_ban,
            "prefixes": {},
            "version_config": self.get_version_info()
        }

        for so_an in [2, 3, 4]:
            result["prefixes"][f"{so_an}_an"] = self.get_equation_prefix(so_an)

        return result