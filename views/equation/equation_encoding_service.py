# services/equation_encoding_service.py
from typing import List

class EquationEncodingService:
    def __init__(self, equation_controller):
        self.controller = equation_controller

    def encode_equation_data(self, danh_sach_he_so: List[str], so_an: int, phien_ban: str) -> dict:
        """Mã hóa dữ liệu phương trình"""
        try:
            self.controller.set_so_an(so_an)
            self.controller.set_phien_ban(phien_ban)
            self.controller.set_he_so(danh_sach_he_so)

            ket_qua_ma_hoa = self.controller.xu_ly_ma_hoa()

            return {
                'success': True,
                'encoded_coefficients': ket_qua_ma_hoa,
                'total_result': self._create_total_result_string(ket_qua_ma_hoa, so_an)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
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
                    if so_an == 2:
                        return f"{prefix}{chuoi_he_so}== ="
                    elif so_an == 3:
                        return f"{prefix}{chuoi_he_so}== = ="
                    elif so_an == 4:
                        return f"{prefix}{chuoi_he_so}== = = ="

            return "=".join(ket_qua_ma_hoa) + "="

        except Exception as e:
            print(f"Lỗi khi tạo chuỗi kết quả tổng: {e}")
            return "=".join(ket_qua_ma_hoa) + "="