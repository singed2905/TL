# services/batch_processing_service.py
from typing import List, Dict, Any
from processors.excel_processor import ExcelProcessor
from .equation_solver_service import EquationSolverService

class BatchProcessingService:
    def __init__(self, equation_controller, excel_processor: ExcelProcessor):
        self.controller = equation_controller
        self.excel_processor = excel_processor
        self.solver = EquationSolverService()

    def process_batch_file(self, file_path: str, so_an: int, phien_ban: str) -> List[Dict[str, Any]]:
        """Xử lý hàng loạt file Excel"""
        try:
            all_rows_data = self.excel_processor.process_equation_batch(file_path, so_an)
            results = []

            for row_data in all_rows_data:
                try:
                    result = self._process_single_row(row_data, so_an, phien_ban)
                    results.append(result)
                except Exception as e:
                    error_result = {
                        'row_index': row_data['row_index'],
                        'trang_thai': 'Lỗi',
                        'ghi_chu': f"Lỗi xử lý: {str(e)}",
                        'ket_qua_ma_hoa': '',
                        'ket_qua_nghiem': f"❌ Lỗi: {str(e)}",
                        'ket_qua_tong': ''
                    }
                    results.append(error_result)

            return results

        except Exception as e:
            raise Exception(f"Lỗi xử lý hàng loạt: {str(e)}")

    def _process_single_row(self, row_data: Dict[str, Any], so_an: int, phien_ban: str) -> Dict[str, Any]:
        """Xử lý một dòng dữ liệu trong chế độ hàng loạt"""
        try:
            he_so_list = row_data['he_so']
            required_per_equation = so_an + 1
            total_required = so_an * required_per_equation

            # Xử lý điều chỉnh hệ số
            adjustment_result = self._adjust_coefficients(he_so_list, so_an)
            danh_sach_he_so_dieu_chinh = adjustment_result['coefficients']
            adjustment_messages = adjustment_result['messages']

            # Kiểm tra dữ liệu hợp lệ
            if not any(hs != "0" for hs in danh_sach_he_so_dieu_chinh):
                return {
                    'row_index': row_data['row_index'],
                    'trang_thai': 'Lỗi',
                    'ghi_chu': 'Tất cả hệ số đều bằng 0 - Không có dữ liệu hợp lệ',
                    'ket_qua_ma_hoa': '',
                    'ket_qua_nghiem': '❌ Không có dữ liệu hợp lệ',
                    'ket_qua_tong': ''
                }

            # Cập nhật controller và xử lý
            self.controller.set_so_an(so_an)
            self.controller.set_phien_ban(phien_ban)
            self.controller.set_he_so(danh_sach_he_so_dieu_chinh)

            ket_qua_ma_hoa = self.controller.xu_ly_ma_hoa()
            ket_qua_nghiem = self.solver.solve_equation_system(danh_sach_he_so_dieu_chinh, so_an)
            ket_qua_tong = self._create_total_result_string(ket_qua_ma_hoa, so_an)

            # Tạo ghi chú điều chỉnh
            ghi_chu_dieu_chinh = ""
            if adjustment_messages:
                ghi_chu_dieu_chinh = f"Đã điều chỉnh: {', '.join(adjustment_messages)}"

            return {
                'row_index': row_data['row_index'],
                'trang_thai': 'Thành công',
                'ghi_chu': ghi_chu_dieu_chinh,
                'ket_qua_ma_hoa': "=".join(ket_qua_ma_hoa) + "=",
                'ket_qua_nghiem': ket_qua_nghiem,
                'ket_qua_tong': ket_qua_tong,
                'he_so_goc': he_so_list,
                'he_so_dieu_chinh': danh_sach_he_so_dieu_chinh
            }

        except Exception as e:
            return {
                'row_index': row_data['row_index'],
                'trang_thai': 'Lỗi',
                'ghi_chu': f'Lỗi xử lý: {str(e)}',
                'ket_qua_ma_hoa': '',
                'ket_qua_nghiem': f'❌ Lỗi: {str(e)}',
                'ket_qua_tong': ''
            }

    def _adjust_coefficients(self, he_so_list: List[str], so_an: int) -> Dict[str, Any]:
        """Điều chỉnh hệ số - tự động điền số 0 khi cần"""
        required_per_equation = so_an + 1
        total_required = so_an * required_per_equation

        adjustment_messages = []
        danh_sach_he_so_dieu_chinh = []

        for i in range(so_an):
            start_idx = i * required_per_equation
            end_idx = start_idx + required_per_equation

            if start_idx < len(he_so_list):
                equation_coeffs = he_so_list[start_idx:end_idx]
            else:
                equation_coeffs = []

            # Xử lý từng phương trình
            processed_coeffs = []
            for j, coeff in enumerate(equation_coeffs):
                if coeff == "" or coeff is None:
                    processed_coeffs.append('0')
                    if f"PT {i + 1}" not in [msg for msg in adjustment_messages if "trống" in msg]:
                        adjustment_messages.append(f"điền 0 cho PT {i + 1} (trống)")
                else:
                    processed_coeffs.append(coeff)

            # Điều chỉnh số lượng hệ số
            if len(processed_coeffs) < required_per_equation:
                missing_count = required_per_equation - len(processed_coeffs)
                processed_coeffs.extend(['0'] * missing_count)
                adjustment_messages.append(f"điền {missing_count} số 0 cho PT {i + 1}")

            elif len(processed_coeffs) > required_per_equation:
                processed_coeffs = processed_coeffs[:required_per_equation]
                adjustment_messages.append(f"cắt bớt hệ số thừa ở PT {i + 1}")

            danh_sach_he_so_dieu_chinh.extend(processed_coeffs)

        # Xử lý thiếu phương trình
        current_equation_count = len(danh_sach_he_so_dieu_chinh) // required_per_equation
        if current_equation_count < so_an:
            missing_equations = so_an - current_equation_count
            for i in range(missing_equations):
                danh_sach_he_so_dieu_chinh.extend(['0'] * required_per_equation)
                adjustment_messages.append(f"thêm PT {current_equation_count + i + 1} toàn số 0")

        # Đảm bảo đủ số lượng hệ số
        if len(danh_sach_he_so_dieu_chinh) < total_required:
            missing_total = total_required - len(danh_sach_he_so_dieu_chinh)
            danh_sach_he_so_dieu_chinh.extend(['0'] * missing_total)
            adjustment_messages.append(f"điền thêm {missing_total} số 0")

        return {
            'coefficients': danh_sach_he_so_dieu_chinh,
            'messages': adjustment_messages
        }

    def _create_total_result_string(self, ket_qua_ma_hoa: List[str], so_an: int) -> str:
        """Tạo chuỗi kết quả tổng với định dạng theo số ẩn"""
        try:
            prefix = self.controller.get_equation_prefix(so_an)
            required_counts = {2: 6, 3: 12, 4: 20}

            if so_an in required_counts:
                required_count = required_counts[so_an]
                if len(ket_qua_ma_hoa) >= required_count:
                    he_so_can_thiet = ket_qua_ma_hoa[:required_count]
                    chuoi_he_so = "=".join(he_so_can_thiet)

                    # ĐIỀU CHỈNH ĐỊNH DẠNG THEO SỐ ẨN
                    ending_map = {
                        2: "== =",
                        3: "== = =",
                        4: "== = = ="
                    }
                    return f"{prefix}{chuoi_he_so}{ending_map.get(so_an, '=')}"

            return "=".join(ket_qua_ma_hoa) + "="

        except Exception as e:
            return "=".join(ket_qua_ma_hoa) + "="