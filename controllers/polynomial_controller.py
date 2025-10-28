from typing import List, Dict, Any, Tuple
from models.polynomial_models import PolynomialSolver, validate_polynomial_input

class PolynomialController:
    """
    Controller cho chức năng Polynomial:
    - Nhận input từ View
    - Validate và chuyển đổi hệ số
    - Gọi Model để giải
    - Trả kết quả đã format cho View
    """

    def __init__(self):
        self.solver = PolynomialSolver()

    def validate_input(self, degree: int, coeffs: List[str]) -> Tuple[bool, str]:
        """
        Validate nhanh dữ liệu đầu vào từ UI
        """
        try:
            ok, msg = validate_polynomial_input(coeffs, degree)
            return ok, msg
        except Exception as e:
            return False, str(e)

    def process_equation(self, degree: int, coeffs: List[str], version: str) -> Dict[str, Any]:
        """
        Xử lý phương trình: validate → solve → format → encode (optional)

        Args:
            degree: 2, 3, 4
            coeffs: danh sách hệ số dạng string từ UI
            version: phiên bản máy tính (fx799, fx991, ...)

        Returns:
            Dict kết quả cho View (an toàn, có success flag)
        """
        try:
            # 1) Validate input
            ok, err = self.validate_input(degree, coeffs)
            if not ok:
                return {
                    'success': False,
                    'error': f'Dữ liệu không hợp lệ: {err}',
                    'degree': degree,
                    'coefficients_raw': coeffs
                }

            # 2) Solve bằng Model
            result = self.solver.solve_polynomial(degree, coeffs)
            if not result.get('success', False):
                # Trường hợp Model trả lỗi đã có reason
                return {
                    'success': False,
                    'error': result.get('error', 'Không rõ lỗi'),
                    'degree': degree,
                    'coefficients_raw': coeffs
                }

            # 3) Bổ sung thông tin cho View
            formatted = result.get('formatted', {})
            view_payload = {
                'success': True,
                'degree': result['degree'],
                'coefficients': result['coefficients'],
                'equation_display': formatted.get('equation', ''),
                'roots_display': formatted.get('roots_display', []),
                'summary': formatted.get('summary', ''),
                'analysis': result.get('analysis', {}),
                'version': version,
                # Chỗ để mở rộng mã hóa cho máy tính ở Phase 3
                'encoded_for_calculator': self._encode_for_calculator_stub(result, version)
            }
            return view_payload

        except Exception as e:
            return {
                'success': False,
                'error': f'Lỗi xử lý: {str(e)}',
                'degree': degree,
                'coefficients_raw': coeffs
            }

    def _encode_for_calculator_stub(self, result: Dict[str, Any], version: str) -> str:
        """
        Placeholder cho Phase 3 (Calculator encoding).
        Hiện tại chỉ trả về mô tả tạm thời.
        """
        deg = result.get('degree', '')
        return f'[ENCODER-{version}] Ready for encoding (degree={deg})'
