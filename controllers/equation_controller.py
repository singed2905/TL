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

        # Load version mapping
        self.version_mapping = self._load_version_mapping()
        self.current_version_config = self._load_version_config(self.phien_ban)
        self.equation_prefixes = self._load_equation_prefixes()

    def _load_equation_prefixes(self, file_path: str = "config/equation_prefixes.json") -> dict:
        """Load tiền tố phương trình từ JSON"""
        try:
            if not os.path.exists(file_path):
                return {"2": "w912", "3": "w913", "4": "w914"}

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("prefixes", {"2": "w912", "3": "w913", "4": "w914"})
        except Exception as e:
            print(f"Lỗi khi đọc file equation_prefixes.json: {e}")
            return {"2": "w912", "3": "w913", "4": "w914"}

    def get_equation_prefix(self, so_an: int) -> str:
        """Lấy tiền tố cho số ẩn cụ thể"""
        return self.equation_prefixes.get(str(so_an), "")

    def _load_version_mapping(self):
        """Load mapping phiên bản từ file JSON"""
        try:
            with open("config/version_configs/version_mapping.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("version_file_mapping", {})
        except Exception as e:
            print(f"Lỗi load version mapping: {e}")
            return {
                "fx799": "fx799.json",
                "fx800": "fx800.json",
                "fx801": "fx801.json",
                "fx802": "fx802.json",
                "fx803": "fx803.json"
            }

    def _load_version_config(self, version_name):
        """Load cấu hình cho phiên bản được chọn"""
        try:
            config_file = self.version_mapping.get(version_name, "fx799.json")
            config_path = f"config/version_configs/{config_file}"

            if not os.path.exists(config_path):
                print(f"File config không tồn tại: {config_path}")
                return {"version": version_name, "prefix": "wj"}

            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Lỗi load config phiên bản {version_name}: {e}")
            return {"version": version_name, "prefix": "wj"}

    def set_so_an(self, so_an):
        """Thiết lập số ẩn"""
        self.so_an = int(so_an)

    def set_phien_ban(self, phien_ban):
        """Thiết lập phiên bản"""
        self.phien_ban = phien_ban
        self.current_version_config = self._load_version_config(phien_ban)

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

    def get_export_info(self):
        """Lấy thông tin cho export"""
        return {
            "so_an": self.so_an,
            "phien_ban": self.phien_ban,
            "he_so": self.he_so,
            "ket_qua_ma_hoa": self.ket_qua_ma_hoa,
            "has_data": len(self.he_so) > 0
        }