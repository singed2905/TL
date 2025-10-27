import pandas as pd
from datetime import datetime
from models.geometry_models import GeometryData
from models.mapping_manager import MappingManager
from processors.excel_processor import ExcelProcessor
from typing import Tuple, List, Dict, Any
import os
import json
from utils.file_utils import FileUtils


class GeometryController:
    def __init__(self):
        self.geometry_data = GeometryData()
        self.mapping_manager = MappingManager()

        # Data storage - giống như trong code gốc
        self.ket_qua_A1 = []
        self.ket_qua_X1 = []
        self.ket_qua_N1 = []
        self.ket_qua_A2 = []
        self.ket_qua_X2 = []
        self.ket_qua_N2 = []
        self.ket_qua_diem_A = []
        self.ket_qua_diem_B = []
        self.ket_qua_duong_tron_A = []
        self.ket_qua_mat_cau_A = []
        self.ket_qua_duong_tron_B = []
        self.ket_qua_mat_cau_B = []

        # store raw data for export
        self.raw_data_A = {}
        self.raw_data_B = {}

        # Current state
        self.current_shape_A = ""
        self.current_shape_B = ""
        self.current_operation = ""
        self.kich_thuoc_A = "3"
        self.kich_thuoc_B = "3"

        self.excel_processor = ExcelProcessor()

        # KHỞI TẠO VERSION MAPPING TRƯỚC
        self.version_mapping = self._load_version_mapping()
        self.current_version_config = self._load_version_config("Phiên bản 1.0")

    def _load_version_mapping(self):
        """Load mapping phiên bản từ file JSON"""
        try:
            with open("config/version_configs/version_mapping.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("version_file_mapping", {})
        except Exception as e:
            print(f"Lỗi load version mapping: {e}")
            # Fallback mapping nếu file không tồn tại
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
            # Đảm bảo version_mapping đã được khởi tạo
            if not hasattr(self, 'version_mapping'):
                self.version_mapping = self._load_version_mapping()

            config_file = self.version_mapping.get(version_name, "version_1.0.json")
            config_path = f"config/version_configs/{config_file}"

            # Kiểm tra file tồn tại
            if not os.path.exists(config_path):
                print(f"File config không tồn tại: {config_path}")
                return {"version": version_name, "prefix": "wj"}

            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            print(f"Lỗi load config phiên bản {version_name}: {e}")
            # Fallback về phiên bản 1.0 nếu có lỗi
            return {"version": version_name, "prefix": "wj"}

    def set_current_version(self, version_name):
        """Thiết lập phiên bản hiện tại"""
        self.current_version_config = self._load_version_config(version_name)

    def get_available_versions(self):
        """Lấy danh sách phiên bản khả dụng"""
        if not hasattr(self, 'version_mapping'):
            self.version_mapping = self._load_version_mapping()
        return list(self.version_mapping.keys())
    def process_excel_batch(self, file_path: str, shape_a: str, shape_b: str,
                            operation: str, dimension_a: str, dimension_b: str,
                            output_path: str = None) -> Tuple[List[str], str, int, int]:
        """Process entire Excel file in batch with pre-selected output path"""
        try:
            # Read and validate Excel file
            df = self.excel_processor.read_excel_data(file_path)
            is_valid, missing_cols = self.excel_processor.validate_excel_structure(df, shape_a, shape_b)

            if not is_valid:
                raise Exception(f"Thiếu các cột: {', '.join(missing_cols)}")

            encoded_results = []
            processed_count = 0
            error_count = 0

            # Process each row
            for index, row in df.iterrows():
                try:
                    # Set current state for this row
                    self.set_current_shapes(shape_a, shape_b)
                    self.set_kich_thuoc(dimension_a, dimension_b)
                    self.current_operation = operation

                    # Extract data for both groups
                    data_a = self.excel_processor.extract_shape_data(row, shape_a, 'A')
                    data_b = self.excel_processor.extract_shape_data(row, shape_b, 'B') if shape_b else {}

                    # Process data
                    self.thuc_thi_tat_ca(data_a, data_b)
                    result = self.generate_final_result()

                    encoded_results.append(result)
                    processed_count += 1

                except Exception as e:
                    # Log error but continue with next row
                    encoded_results.append(f"LỖI: {str(e)}")
                    error_count += 1
                    print(f"Lỗi dòng {index + 1}: {str(e)}")

            # Generate output path if not provided (fallback for backward compatibility)
            if not output_path:
                original_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = f"{original_name}_encoded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                # Ensure we save in current directory if no path provided
                output_path = os.path.join(os.getcwd(), output_path)

            # Export results to the pre-selected output path
            output_file = self.excel_processor.export_results(df, encoded_results, output_path)

            return encoded_results, output_file, processed_count, error_count

        except Exception as e:
            raise Exception(f"Lỗi xử lý file Excel: {str(e)}")
    def get_available_shapes(self):
        """Get list of available geometric shapes"""
        return ["Điểm", "Đường thẳng", "Mặt phẳng", "Đường tròn", "Mặt cầu"]

    def update_dropdown_options(self, operation):
        """Update dropdown options based on selected operation"""
        self.current_operation = operation
        if operation == "Khoảng cách":
            return ["Điểm", "Đường thẳng", "Mặt phẳng"]
        elif operation == "Diện tích":
            return ["Đường tròn", "Mặt cầu"]
        elif operation == "Thể tích":
            return ["Mặt cầu"]
        elif operation == "PT đường thẳng":
            return ["Điểm"]
        else:
            return self.get_available_shapes()

    def set_current_shapes(self, shape_A, shape_B):
        """Set current selected shapes"""
        self.current_shape_A = shape_A
        self.current_shape_B = shape_B

    def set_kich_thuoc(self, kich_thuoc_A, kich_thuoc_B):
        """Set dimensions"""
        self.kich_thuoc_A = kich_thuoc_A
        self.kich_thuoc_B = kich_thuoc_B

    def cap_nhat_ket_qua(self, chuoi_dau_vao, so_tham_so=3, apply_keylog=True):
        """Update results from input string - similar to original function"""
        if not chuoi_dau_vao:
            return ["" for _ in range(so_tham_so)]

        chuoi_dau_vao = chuoi_dau_vao.replace(" ", "")
        ds = chuoi_dau_vao.split(',')
        while len(ds) < so_tham_so:
            ds.append("0")
        ds = ds[:so_tham_so]

        if apply_keylog:
            ket_qua = [self.mapping_manager.encode_string(item) for item in ds]
        else:
            ket_qua = ds

        return ket_qua

    # ========== GROUP A PROCESSING ==========
    def process_point_A(self, input_data):
        """Process point data for group A"""
        so_chieu = int(self.kich_thuoc_A)
        if so_chieu == 2:
            self.ket_qua_diem_A = self.cap_nhat_ket_qua(input_data, so_tham_so=2)
        else:
            self.ket_qua_diem_A = self.cap_nhat_ket_qua(input_data, so_tham_so=3)
        return self.ket_qua_diem_A

    def process_line_A(self, input_A1, input_X1):
        """Process line data for group A"""
        self.ket_qua_A1 = self.cap_nhat_ket_qua(input_A1)
        self.ket_qua_X1 = self.cap_nhat_ket_qua(input_X1)
        return self.ket_qua_A1 + self.ket_qua_X1

    def process_plane_A(self, coefficients):
        """Process plane data for group A"""
        # coefficients should be a list of [a, b, c, d]
        self.ket_qua_N1 = [self.mapping_manager.encode_string(coef) for coef in coefficients]
        return self.ket_qua_N1

    def process_circle_A(self, center_input, radius_input):
        """Process circle data for group A - 2 inputs: center and radius"""
        # Xử lý tâm (2 tham số: x,y)
        center_result = self.cap_nhat_ket_qua(center_input, so_tham_so=2)
        # Xử lý bán kính (1 tham số)
        radius_result = self.cap_nhat_ket_qua(radius_input, so_tham_so=1)

        # Kết hợp kết quả: [x, y, r]
        self.ket_qua_duong_tron_A = center_result + radius_result
        return self.ket_qua_duong_tron_A

    def process_sphere_A(self, center_input, radius_input):
        """Process sphere data for group A - 2 inputs: center and radius"""
        # Xử lý tâm (3 tham số: x,y,z)
        center_result = self.cap_nhat_ket_qua(center_input, so_tham_so=3)
        # Xử lý bán kính (1 tham số)
        radius_result = self.cap_nhat_ket_qua(radius_input, so_tham_so=1)

        # Kết hợp kết quả: [x, y, z, r]
        self.ket_qua_mat_cau_A = center_result + radius_result
        return self.ket_qua_mat_cau_A

    # ========== GROUP B PROCESSING ==========
    def process_point_B(self, input_data):
        """Process point data for group B"""
        so_chieu = int(self.kich_thuoc_B)
        if so_chieu == 2:
            self.ket_qua_diem_B = self.cap_nhat_ket_qua(input_data, so_tham_so=2)
        else:
            self.ket_qua_diem_B = self.cap_nhat_ket_qua(input_data, so_tham_so=3)
        return self.ket_qua_diem_B

    def process_line_B(self, input_A2, input_X2):
        """Process line data for group B"""
        self.ket_qua_A2 = self.cap_nhat_ket_qua(input_A2)
        self.ket_qua_X2 = self.cap_nhat_ket_qua(input_X2)
        return self.ket_qua_A2 + self.ket_qua_X2

    def process_plane_B(self, coefficients):
        """Process plane data for group B"""
        # coefficients should be a list of [a, b, c, d]
        self.ket_qua_N2 = [self.mapping_manager.encode_string(coef) for coef in coefficients]
        return self.ket_qua_N2

    def process_circle_B(self, center_input, radius_input):
        """Process circle data for group B - 2 inputs: center and radius"""
        center_result = self.cap_nhat_ket_qua(center_input, so_tham_so=2)
        radius_result = self.cap_nhat_ket_qua(radius_input, so_tham_so=1)
        self.ket_qua_duong_tron_B = center_result + radius_result
        return self.ket_qua_duong_tron_B

    def process_sphere_B(self, center_input, radius_input):
        """Process sphere data for group B - 2 inputs: center and radius"""
        center_result = self.cap_nhat_ket_qua(center_input, so_tham_so=3)
        radius_result = self.cap_nhat_ket_qua(radius_input, so_tham_so=1)
        self.ket_qua_mat_cau_B = center_result + radius_result
        return self.ket_qua_mat_cau_B

    # ========== MAIN PROCESSING METHODS ==========
    def thuc_thi_A(self, data_dict):
        """Process group A data based on current shape"""
        shape_type = self.current_shape_A
        self.raw_data_A = data_dict.copy()

        if shape_type == "Điểm":
            input_data = data_dict.get('point_input', '')
            return self.process_point_A(input_data)

        elif shape_type == "Đường thẳng":
            input_A1 = data_dict.get('line_A1', '')
            input_X1 = data_dict.get('line_X1', '')
            return self.process_line_A(input_A1, input_X1)

        elif shape_type == "Mặt phẳng":
            coefficients = [
                data_dict.get('plane_a', ''),
                data_dict.get('plane_b', ''),
                data_dict.get('plane_c', ''),
                data_dict.get('plane_d', '')
            ]
            return self.process_plane_A(coefficients)

        elif shape_type == "Đường tròn":
            center_input = data_dict.get('circle_center', '')
            radius_input = data_dict.get('circle_radius', '')
            return self.process_circle_A(center_input, radius_input)

        elif shape_type == "Mặt cầu":
            center_input = data_dict.get('sphere_center', '')
            radius_input = data_dict.get('sphere_radius', '')
            return self.process_sphere_A(center_input, radius_input)

        return []

    def thuc_thi_B(self, data_dict):
        """Process group B data based on current shape"""
        if self.current_operation in ["Diện tích", "Thể tích"]:
            return []

        shape_type = self.current_shape_B
        self.raw_data_B = data_dict.copy()

        if shape_type == "Điểm":
            input_data = data_dict.get('point_input', '')
            return self.process_point_B(input_data)

        elif shape_type == "Đường thẳng":
            input_A2 = data_dict.get('line_A2', '')
            input_X2 = data_dict.get('line_X2', '')
            return self.process_line_B(input_A2, input_X2)

        elif shape_type == "Mặt phẳng":
            coefficients = [
                data_dict.get('plane_a', ''),
                data_dict.get('plane_b', ''),
                data_dict.get('plane_c', ''),
                data_dict.get('plane_d', '')
            ]
            return self.process_plane_B(coefficients)

        elif shape_type == "Đường tròn":
            center_input = data_dict.get('circle_center', '')
            radius_input = data_dict.get('circle_radius', '')
            return self.process_circle_B(center_input, radius_input)

        elif shape_type == "Mặt cầu":
            center_input = data_dict.get('sphere_center', '')
            radius_input = data_dict.get('sphere_radius', '')
            return self.process_sphere_B(center_input, radius_input)

        return []

    def thuc_thi_tat_ca(self, data_dict_A, data_dict_B):
        """Process all groups"""
        result_A = self.thuc_thi_A(data_dict_A)
        result_B = self.thuc_thi_B(data_dict_B)
        return result_A, result_B

    def generate_final_result(self):
        """Generate the final encoded string"""
        if not self.current_shape_A or not self.current_operation:
            return ""

        pheptoan_code = self.geometry_data.pheptoan_map.get(self.current_operation, self.current_operation)

        # Get T-code mappings
        tcodeA = self._get_tcode_mapping("A", self.current_shape_A)

        # For Area and Volume, don't include group B
        if self.current_operation in ["Diện tích", "Thể tích"]:
            tenB_code = ""
            gia_tri_B = ""
            tcodeB = ""
        else:
            tcodeB = self._get_tcode_mapping("B", self.current_shape_B)
            tenB_code = self._get_shape_code_B(self.current_shape_B)
            gia_tri_B = self._get_encoded_values_B()

        tenA_code = self._get_shape_code_A(self.current_shape_A)
        gia_tri_A = self._get_encoded_values_A()
        prefix = self.current_version_config.get("prefix", "wj")
        # Build final result
        if self.current_operation in ["Diện tích", "Thể tích"]:
            ket_qua = f"{prefix}{tenA_code}{gia_tri_A}C{pheptoan_code}{tcodeA}="
        else:
            ket_qua = f"{prefix}{tenA_code}{gia_tri_A}C{tenB_code}{gia_tri_B}C{pheptoan_code}{tcodeA}R{tcodeB}="

        return ket_qua

    def _get_tcode_mapping(self, group, shape):
        """Get T-code mapping for shape"""
        pheptoan = self.current_operation

        if pheptoan in self.geometry_data.operation_tcodes:
            operation_map = self.geometry_data.operation_tcodes[pheptoan]
            if group == "A" and shape in operation_map["group_a"]:
                return operation_map["group_a"][shape]
            elif group == "B" and shape in operation_map["group_b"]:
                return operation_map["group_b"][shape]

        # Return default mapping if no operation-specific mapping found
        if group == "A":
            return self.geometry_data.default_group_a_tcodes.get(shape, "T0")
        else:
            return self.geometry_data.default_group_b_tcodes.get(shape, "T0")

    def _get_shape_code_A(self, shape):
        """Get shape code for group A"""
        if shape == "Điểm" and self.kich_thuoc_A == "2":
            return "112"
        elif shape == "Điểm" and self.kich_thuoc_A == "3":
            return "113"
        elif shape == "Đường thẳng":
            return "21"
        elif shape == "Mặt phẳng":
            return "31"
        elif shape == "Đường tròn":
            return "41"
        elif shape == "Mặt cầu":
            return "51"
        else:
            return "00"

    def _get_shape_code_B(self, shape):
        """Get shape code for group B"""
        if shape == "Điểm" and self.kich_thuoc_B == "2":
            return "qT11T122"
        elif shape == "Điểm" and self.kich_thuoc_B == "3":
            return "qT11T123"
        elif shape == "Đường thẳng":
            return "qT12T12"
        elif shape == "Mặt phẳng":
            return "qT13T12"
        elif shape == "Đường tròn":
            return "qT14T12"
        elif shape == "Mặt cầu":
            return "qT15T12"
        else:
            return "qT00T12"

    def _get_encoded_values_A(self):
        """Get encoded values for group A"""
        shape = self.current_shape_A

        if shape == "Điểm":
            so_chieu = int(self.kich_thuoc_A)
            if so_chieu == 2:
                x_encoded = self.ket_qua_diem_A[0] if len(self.ket_qua_diem_A) > 0 else ""
                y_encoded = self.ket_qua_diem_A[1] if len(self.ket_qua_diem_A) > 1 else ""
                return f"{x_encoded}={y_encoded}="
            else:
                x_encoded = self.ket_qua_diem_A[0] if len(self.ket_qua_diem_A) > 0 else ""
                y_encoded = self.ket_qua_diem_A[1] if len(self.ket_qua_diem_A) > 1 else ""
                z_encoded = self.ket_qua_diem_A[2] if len(self.ket_qua_diem_A) > 2 else ""
                return f"{x_encoded}={y_encoded}={z_encoded}="

        elif shape == "Đường thẳng":
            A_encoded = self.ket_qua_A1[0] if len(self.ket_qua_A1) > 0 else ""
            X_encoded = self.ket_qua_X1[0] if len(self.ket_qua_X1) > 0 else ""
            B_encoded = self.ket_qua_A1[1] if len(self.ket_qua_A1) > 1 else ""
            Y_encoded = self.ket_qua_X1[1] if len(self.ket_qua_X1) > 1 else ""
            C_encoded = self.ket_qua_A1[2] if len(self.ket_qua_A1) > 2 else ""
            Z_encoded = self.ket_qua_X1[2] if len(self.ket_qua_X1) > 2 else ""
            return f"{A_encoded}={X_encoded}={B_encoded}={Y_encoded}={C_encoded}={Z_encoded}="

        elif shape == "Mặt phẳng":
            N1_encoded = self.ket_qua_N1[0] if len(self.ket_qua_N1) > 0 else ""
            N2_encoded = self.ket_qua_N1[1] if len(self.ket_qua_N1) > 1 else ""
            N3_encoded = self.ket_qua_N1[2] if len(self.ket_qua_N1) > 2 else ""
            N4_encoded = self.ket_qua_N1[3] if len(self.ket_qua_N1) > 3 else ""
            return f"{N1_encoded}={N2_encoded}={N3_encoded}={N4_encoded}="

        elif shape == "Đường tròn":
            A1_encoded = self.ket_qua_duong_tron_A[0] if len(self.ket_qua_duong_tron_A) > 0 else ""
            A2_encoded = self.ket_qua_duong_tron_A[1] if len(self.ket_qua_duong_tron_A) > 1 else ""
            A3_encoded = self.ket_qua_duong_tron_A[2] if len(self.ket_qua_duong_tron_A) > 2 else ""
            return f"{A1_encoded}={A2_encoded}={A3_encoded}="

        elif shape == "Mặt cầu":
            A1_encoded = self.ket_qua_mat_cau_A[0] if len(self.ket_qua_mat_cau_A) > 0 else ""
            A2_encoded = self.ket_qua_mat_cau_A[1] if len(self.ket_qua_mat_cau_A) > 1 else ""
            A3_encoded = self.ket_qua_mat_cau_A[2] if len(self.ket_qua_mat_cau_A) > 2 else ""
            A4_encoded = self.ket_qua_mat_cau_A[3] if len(self.ket_qua_mat_cau_A) > 3 else ""
            return f"{A1_encoded}={A2_encoded}={A3_encoded}={A4_encoded}="

        return ""

    def _get_encoded_values_B(self):
        """Get encoded values for group B"""
        if self.current_operation in ["Diện tích", "Thể tích"]:
            return ""

        shape = self.current_shape_B

        if shape == "Điểm":
            so_chieu = int(self.kich_thuoc_B)
            if so_chieu == 2:
                x_encoded = self.ket_qua_diem_B[0] if len(self.ket_qua_diem_B) > 0 else ""
                y_encoded = self.ket_qua_diem_B[1] if len(self.ket_qua_diem_B) > 1 else ""
                return f"{x_encoded}={y_encoded}="
            else:
                x_encoded = self.ket_qua_diem_B[0] if len(self.ket_qua_diem_B) > 0 else ""
                y_encoded = self.ket_qua_diem_B[1] if len(self.ket_qua_diem_B) > 1 else ""
                z_encoded = self.ket_qua_diem_B[2] if len(self.ket_qua_diem_B) > 2 else ""
                return f"{x_encoded}={y_encoded}={z_encoded}="

        elif shape == "Đường thẳng":
            A_encoded = self.ket_qua_A2[0] if len(self.ket_qua_A2) > 0 else ""
            X_encoded = self.ket_qua_X2[0] if len(self.ket_qua_X2) > 0 else ""
            B_encoded = self.ket_qua_A2[1] if len(self.ket_qua_A2) > 1 else ""
            Y_encoded = self.ket_qua_X2[1] if len(self.ket_qua_X2) > 1 else ""
            C_encoded = self.ket_qua_A2[2] if len(self.ket_qua_A2) > 2 else ""
            Z_encoded = self.ket_qua_X2[2] if len(self.ket_qua_X2) > 2 else ""
            return f"{A_encoded}={X_encoded}={B_encoded}={Y_encoded}={C_encoded}={Z_encoded}="

        elif shape == "Mặt phẳng":
            N5_encoded = self.ket_qua_N2[0] if len(self.ket_qua_N2) > 0 else ""
            N6_encoded = self.ket_qua_N2[1] if len(self.ket_qua_N2) > 1 else ""
            N7_encoded = self.ket_qua_N2[2] if len(self.ket_qua_N2) > 2 else ""
            N8_encoded = self.ket_qua_N2[3] if len(self.ket_qua_N2) > 3 else ""
            return f"{N5_encoded}={N6_encoded}={N7_encoded}={N8_encoded}="

        elif shape == "Đường tròn":
            B1_encoded = self.ket_qua_duong_tron_B[0] if len(self.ket_qua_duong_tron_B) > 0 else ""
            B2_encoded = self.ket_qua_duong_tron_B[1] if len(self.ket_qua_duong_tron_B) > 1 else ""
            B3_encoded = self.ket_qua_duong_tron_B[2] if len(self.ket_qua_duong_tron_B) > 2 else ""
            return f"{B1_encoded}={B2_encoded}={B3_encoded}="

        elif shape == "Mặt cầu":
            B1_encoded = self.ket_qua_mat_cau_B[0] if len(self.ket_qua_mat_cau_B) > 0 else ""
            B2_encoded = self.ket_qua_mat_cau_B[1] if len(self.ket_qua_mat_cau_B) > 1 else ""
            B3_encoded = self.ket_qua_mat_cau_B[2] if len(self.ket_qua_mat_cau_B) > 2 else ""
            B4_encoded = self.ket_qua_mat_cau_B[3] if len(self.ket_qua_mat_cau_B) > 3 else ""
            return f"{B1_encoded}={B2_encoded}={B3_encoded}={B4_encoded}="

        return ""

    def export_to_excel(self, file_path=None):
        """Export current data to Excel với đường dẫn an toàn"""
        try:
            if file_path is None:
                # Nếu không có đường dẫn, sử dụng tên file mặc định trong thư mục hiện tại
                file_path = f"geometry_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

            # SỬA LỖI: Xử lý đường dẫn an toàn
            directory = os.path.dirname(file_path)
            if directory:  # Nếu có thư mục trong đường dẫn
                if not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
            else:  # Nếu chỉ có tên file, lưu trong thư mục hiện tại
                file_path = os.path.join(os.getcwd(), file_path)

            # Chuẩn bị dữ liệu để xuất
            data = self._prepare_comprehensive_export_data()
            df = pd.DataFrame(data)

            # Tạo file Excel với nhiều sheet nếu cần
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Geometry Data', index=False)

                # Thêm sheet tóm tắt
                summary_data = self._prepare_summary_data()
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)

            return file_path

        except ImportError:
            raise Exception("Thư viện openpyxl chưa được cài đặt. Vui lòng cài đặt bằng lệnh: pip install openpyxl")
        except Exception as e:
            raise Exception(f"Lỗi xuất Excel: {str(e)}")

    def _prepare_comprehensive_export_data(self):
        """Prepare comprehensive data for Excel export"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Base data
        data = {
            "Thời gian": [timestamp],
            "Phép toán": [self.current_operation],
            "Đối tượng A": [self.current_shape_A],
            "Đối tượng B": [
                self.current_shape_B if self.current_operation not in ["Diện tích", "Thể tích"] else "Không có"],
            "Kết quả mã hóa": [self.generate_final_result()],
            "Kích thước A": [self.kich_thuoc_A],
            "Kích thước B": [self.kich_thuoc_B]
        }

        # Add detailed data based on shape types
        self._add_detailed_export_data(data, "A", self.current_shape_A, self.raw_data_A)

        if self.current_operation not in ["Diện tích", "Thể tích"]:
            self._add_detailed_export_data(data, "B", self.current_shape_B, self.raw_data_B)

        return data

    def _add_detailed_export_data(self, data, group, shape_type, raw_data):
        """Add detailed export data for specific group and shape type"""
        prefix = f"Nhóm {group} - "

        if shape_type == "Điểm":
            dimensions = int(self.kich_thuoc_A if group == "A" else self.kich_thuoc_B)
            if dimensions == 2:
                data[f"{prefix}Tọa độ X"] = [
                    raw_data.get('point_input', '').split(',')[0] if raw_data.get('point_input') else ""]
                data[f"{prefix}Tọa độ Y"] = [
                    raw_data.get('point_input', '').split(',')[1] if raw_data.get('point_input') and len(
                        raw_data.get('point_input', '').split(',')) > 1 else ""]
                data[f"{prefix}Tọa độ X (mã hóa)"] = [self.ket_qua_diem_A[0] if len(self.ket_qua_diem_A) > 0 else ""]
                data[f"{prefix}Tọa độ Y (mã hóa)"] = [self.ket_qua_diem_A[1] if len(self.ket_qua_diem_A) > 1 else ""]
            else:
                data[f"{prefix}Tọa độ X"] = [
                    raw_data.get('point_input', '').split(',')[0] if raw_data.get('point_input') else ""]
                data[f"{prefix}Tọa độ Y"] = [
                    raw_data.get('point_input', '').split(',')[1] if raw_data.get('point_input') and len(
                        raw_data.get('point_input', '').split(',')) > 1 else ""]
                data[f"{prefix}Tọa độ Z"] = [
                    raw_data.get('point_input', '').split(',')[2] if raw_data.get('point_input') and len(
                        raw_data.get('point_input', '').split(',')) > 2 else ""]
                data[f"{prefix}Tọa độ X (mã hóa)"] = [self.ket_qua_diem_A[0] if len(self.ket_qua_diem_A) > 0 else ""]
                data[f"{prefix}Tọa độ Y (mã hóa)"] = [self.ket_qua_diem_A[1] if len(self.ket_qua_diem_A) > 1 else ""]
                data[f"{prefix}Tọa độ Z (mã hóa)"] = [self.ket_qua_diem_A[2] if len(self.ket_qua_diem_A) > 2 else ""]

        elif shape_type == "Đường thẳng":
            # Vector coefficients
            data[f"{prefix}Điểm A"] = [raw_data.get('line_A1', '').split(',')[0] if raw_data.get('line_A1') else ""]
            data[f"{prefix}Điểm B"] = [raw_data.get('line_A1', '').split(',')[1] if raw_data.get('line_A1') and len(
                raw_data.get('line_A1', '').split(',')) > 1 else ""]
            data[f"{prefix}Điểm C"] = [raw_data.get('line_A1', '').split(',')[2] if raw_data.get('line_A1') and len(
                raw_data.get('line_A1', '').split(',')) > 2 else ""]
            data[f"{prefix}Điểm A (mã hóa)"] = [self.ket_qua_A1[0] if len(self.ket_qua_A1) > 0 else ""]
            data[f"{prefix}Điểm B (mã hóa)"] = [self.ket_qua_A1[1] if len(self.ket_qua_A1) > 1 else ""]
            data[f"{prefix}Điểm C (mã hóa)"] = [self.ket_qua_A1[2] if len(self.ket_qua_A1) > 2 else ""]

            # Point coordinates
            data[f"{prefix}Vector X"] = [raw_data.get('line_X1', '').split(',')[0] if raw_data.get('line_X1') else ""]
            data[f"{prefix}Vector Y"] = [raw_data.get('line_X1', '').split(',')[1] if raw_data.get('line_X1') and len(
                raw_data.get('line_X1', '').split(',')) > 1 else ""]
            data[f"{prefix}Vector Z"] = [raw_data.get('line_X1', '').split(',')[2] if raw_data.get('line_X1') and len(
                raw_data.get('line_X1', '').split(',')) > 2 else ""]
            data[f"{prefix}Vector X (mã hóa)"] = [self.ket_qua_X1[0] if len(self.ket_qua_X1) > 0 else ""]
            data[f"{prefix}Vector Y (mã hóa)"] = [self.ket_qua_X1[1] if len(self.ket_qua_X1) > 1 else ""]
            data[f"{prefix}Vector Z (mã hóa)"] = [self.ket_qua_X1[2] if len(self.ket_qua_X1) > 2 else ""]

        elif shape_type == "Mặt phẳng":
            data[f"{prefix}Hệ số a"] = [raw_data.get('plane_a', '')]
            data[f"{prefix}Hệ số b"] = [raw_data.get('plane_b', '')]
            data[f"{prefix}Hệ số c"] = [raw_data.get('plane_c', '')]
            data[f"{prefix}Hệ số d"] = [raw_data.get('plane_d', '')]
            data[f"{prefix}Hệ số a (mã hóa)"] = [self.ket_qua_N1[0] if len(self.ket_qua_N1) > 0 else ""]
            data[f"{prefix}Hệ số b (mã hóa)"] = [self.ket_qua_N1[1] if len(self.ket_qua_N1) > 1 else ""]
            data[f"{prefix}Hệ số c (mã hóa)"] = [self.ket_qua_N1[2] if len(self.ket_qua_N1) > 2 else ""]
            data[f"{prefix}Hệ số d (mã hóa)"] = [self.ket_qua_N1[3] if len(self.ket_qua_N1) > 3 else ""]

        elif shape_type == "Đường tròn":
            # Cập nhật cho 2 ô nhập riêng biệt
            data[f"{prefix}Tâm đường tròn"] = [raw_data.get('circle_center', '')]
            data[f"{prefix}Bán kính đường tròn"] = [raw_data.get('circle_radius', '')]
            data[f"{prefix}Tâm X (mã hóa)"] = [
                self.ket_qua_duong_tron_A[0] if len(self.ket_qua_duong_tron_A) > 0 else ""]
            data[f"{prefix}Tâm Y (mã hóa)"] = [
                self.ket_qua_duong_tron_A[1] if len(self.ket_qua_duong_tron_A) > 1 else ""]
            data[f"{prefix}Bán kính (mã hóa)"] = [
                self.ket_qua_duong_tron_A[2] if len(self.ket_qua_duong_tron_A) > 2 else ""]

        elif shape_type == "Mặt cầu":
            # Cập nhật cho 2 ô nhập riêng biệt
            data[f"{prefix}Tâm mặt cầu"] = [raw_data.get('sphere_center', '')]
            data[f"{prefix}Bán kính mặt cầu"] = [raw_data.get('sphere_radius', '')]
            data[f"{prefix}Tâm X (mã hóa)"] = [self.ket_qua_mat_cau_A[0] if len(self.ket_qua_mat_cau_A) > 0 else ""]
            data[f"{prefix}Tâm Y (mã hóa)"] = [self.ket_qua_mat_cau_A[1] if len(self.ket_qua_mat_cau_A) > 1 else ""]
            data[f"{prefix}Tâm Z (mã hóa)"] = [self.ket_qua_mat_cau_A[2] if len(self.ket_qua_mat_cau_A) > 2 else ""]
            data[f"{prefix}Bán kính (mã hóa)"] = [self.ket_qua_mat_cau_A[3] if len(self.ket_qua_mat_cau_A) > 3 else ""]

    def _prepare_summary_data(self):
        """Prepare summary data for Excel export"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        summary = {
            "Thời gian xuất": [timestamp],
            "Tổng số đối tượng": ["2" if self.current_operation not in ["Diện tích", "Thể tích"] else "1"],
            "Phép toán thực hiện": [self.current_operation],
            "Đối tượng chính": [self.current_shape_A],
            "Đối tượng phụ": [
                self.current_shape_B if self.current_operation not in ["Diện tích", "Thể tích"] else "Không có"],
            "Trạng thái": ["Đã xử lý và mã hóa"],
            "Độ dài kết quả": [len(self.generate_final_result())],
            "Ghi chú": ["Dữ liệu đã được mã hóa theo quy tắc mapping.json"]
        }

        return summary

    def get_export_info(self):
        """Get information about current data for export"""
        return {
            "operation": self.current_operation,
            "shape_A": self.current_shape_A,
            "shape_B": self.current_shape_B,
            "has_data_A": len(self.raw_data_A) > 0,
            "has_data_B": len(self.raw_data_B) > 0,
            "result_length": len(self.generate_final_result()),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _prepare_export_data(self):
        """Prepare data for Excel export"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data = {
            "Thời gian": [timestamp],
            "Phép toán": [self.current_operation],
            "Đối tượng A": [self.current_shape_A],
            "Đối tượng B": [
                self.current_shape_B if self.current_operation not in ["Diện tích", "Thể tích"] else "Không có"],
            "Kết quả mã hóa": [self.generate_final_result()],
            "Kích thước A": [self.kich_thuoc_A],
            "Kích thước B": [self.kich_thuoc_B]
        }

        return data

    def process_excel_batch_chunked(self, file_path: str, shape_a: str, shape_b: str,
                                    operation: str, dimension_a: str, dimension_b: str,
                                    chunksize: int = 1000, progress_callback=None):
        """Xử lý file Excel lớn theo từng chunk"""

        # Lấy tổng số dòng để tính tiến độ
        total_rows = self.excel_processor.get_total_rows(file_path)
        processed_rows = 0
        success_count = 0
        error_count = 0

        all_results = []

        try:
            # Đọc file theo chunk
            chunk_iterator = self.excel_processor.read_excel_data_chunked(file_path, chunksize)

            for chunk_idx, chunk_df in enumerate(chunk_iterator):
                if self._cancellation_requested:
                    break

                chunk_results = []

                # Xử lý từng dòng trong chunk
                for index, row in chunk_df.iterrows():
                    try:
                        # Set current state
                        self.set_current_shapes(shape_a, shape_b)
                        self.set_kich_thuoc(dimension_a, dimension_b)
                        self.current_operation = operation

                        # Extract và xử lý dữ liệu
                        data_a = self.excel_processor.extract_shape_data(row, shape_a, 'A')
                        data_b = self.excel_processor.extract_shape_data(row, shape_b, 'B') if shape_b else {}

                        self.thuc_thi_tat_ca(data_a, data_b)
                        result = self.generate_final_result()

                        chunk_results.append(result)
                        success_count += 1

                    except Exception as e:
                        chunk_results.append(f"LỖI: {str(e)}")
                        error_count += 1

                    processed_rows += 1

                    # Cập nhật tiến độ sau mỗi dòng
                    if progress_callback and processed_rows % 10 == 0:  # Cập nhật mỗi 10 dòng
                        progress = (processed_rows / total_rows) * 100 if total_rows > 0 else 0
                        progress_callback(progress, processed_rows, total_rows, success_count, error_count)

                all_results.extend(chunk_results)

                # Giải phóng bộ nhớ sau mỗi chunk
                del chunk_df
                import gc
                gc.collect()

            # Xuất kết quả cuối cùng
            final_df = self.excel_processor.read_excel_data(file_path)
            output_path = self._get_output_path(file_path)
            final_output_path = self.excel_processor.export_results(final_df, all_results, output_path)

            return all_results, final_output_path, success_count, error_count

        except Exception as e:
            raise Exception(f"Lỗi xử lý file Excel theo chunk: {str(e)}")