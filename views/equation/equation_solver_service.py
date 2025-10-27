# services/equation_solver_service.py
import math
import re
from typing import List, Tuple


class EquationSolverService:
    def __init__(self):
        self.eps = 1e-10

    def solve_equation_system(self, danh_sach_he_so: List[str], so_an: int) -> str:
        """Giải hệ phương trình từ danh sách hệ số"""
        try:
            so_an = int(so_an)
            required_count = so_an * (so_an + 1)

            if len(danh_sach_he_so) < required_count:
                return f"❌ Thiếu hệ số: cần {required_count}, hiện có {len(danh_sach_he_so)}"

            # Chuyển đổi hệ số sang số
            he_so_float = []
            for hs in danh_sach_he_so:
                try:
                    value = self._eval_math_expression(hs)
                    he_so_float.append(value)
                except Exception as e:
                    return f"❌ Lỗi hệ số '{hs}': {str(e)}"

            # Tạo ma trận và giải
            matrix = self._tao_ma_tran_mo_rong(he_so_float, so_an)
            ket_qua = self._gauss_jordan(matrix, so_an)

            return ket_qua

        except Exception as e:
            return f"❌ Lỗi tính nghiệm: {str(e)}"

    def _eval_math_expression(self, expr: str) -> float:
        """Đánh giá biểu thức toán học"""
        expr = expr.strip().replace(' ', '')
        expr = self._convert_latex_to_python(expr)

        replacements = {
            '^': '**',
            'sqrt': 'math.sqrt',
            'sin': 'math.sin',
            'cos': 'math.cos',
            'tan': 'math.tan',
            'log': 'math.log10',
            'ln': 'math.log',
            'pi': 'math.pi',
            'e': 'math.e',
            'abs': 'abs',
            'exp': 'math.exp'
        }

        for old, new in replacements.items():
            expr = expr.replace(old, new)

        safe_dict = {
            'math': math,
            '__builtins__': {},
            'abs': abs,
            'round': round,
            'min': min,
            'max': max
        }

        try:
            result = eval(expr, safe_dict)
            return float(result)
        except Exception as e:
            raise ValueError(f"Không thể đánh giá: '{expr}'")

    def _convert_latex_to_python(self, expr: str) -> str:
        """Chuyển đổi biểu thức LaTeX sang Python"""
        expr = self._convert_latex_fractions(expr)

        latex_replacements = {
            r'\\pi': 'math.pi',
            r'\\cdot': '*',
            r'\\times': '*',
            r'\\div': '/',
            r'\\left\(': '(',
            r'\\right\)': ')',
            r'\\left\{': '(',
            r'\\right\}': ')',
            r'\\ ': ' ',
            r'\ ': ' ',
        }

        for latex, python in latex_replacements.items():
            expr = re.sub(latex, python, expr)

        return expr

    def _convert_latex_fractions(self, expr: str) -> str:
        """Chuyển đổi phân số LaTeX"""
        fraction_pattern = r'\\frac\{([^{}]+)\}\{([^{}]+)\}'

        def replace_fraction(match):
            numerator = match.group(1)
            denominator = match.group(2)
            numerator = self._convert_latex_fractions(numerator)
            denominator = self._convert_latex_fractions(denominator)
            return f'({numerator})/({denominator})'

        while re.search(fraction_pattern, expr):
            expr = re.sub(fraction_pattern, replace_fraction, expr)

        return expr

    def _tao_ma_tran_mo_rong(self, he_so: List[float], so_an: int) -> List[List[float]]:
        """Tạo ma trận mở rộng"""
        matrix = []
        for i in range(so_an):
            hang = []
            for j in range(so_an + 1):
                idx = i * (so_an + 1) + j
                if idx < len(he_so):
                    hang.append(he_so[idx])
                else:
                    hang.append(0.0)
            matrix.append(hang)
        return matrix

    def _gauss_jordan(self, matrix: List[List[float]], so_an: int) -> str:
        """Giải hệ bằng Gauss-Jordan"""
        n = so_an
        mat = [row[:] for row in matrix]

        for i in range(n):
            # Pivoting
            max_row = i
            for k in range(i + 1, n):
                if abs(mat[k][i]) > abs(mat[max_row][i]):
                    max_row = k

            if max_row != i:
                mat[i], mat[max_row] = mat[max_row], mat[i]

            if abs(mat[i][i]) < self.eps:
                if abs(mat[i][n]) > self.eps:
                    return "❌ Hệ vô nghiệm"
                else:
                    return "🔶 Hệ vô số nghiệm"

            # Chuẩn hóa hàng
            pivot = mat[i][i]
            for j in range(i, n + 1):
                mat[i][j] /= pivot

            # Khử các hàng khác
            for k in range(n):
                if k != i and abs(mat[k][i]) > self.eps:
                    factor = mat[k][i]
                    for j in range(i, n + 1):
                        mat[k][j] -= factor * mat[i][j]

        # Trích xuất nghiệm
        nghiem = []
        for i in range(n):
            nghiem_lam_tron = round(mat[i][n], 8)
            if abs(nghiem_lam_tron) < self.eps:
                nghiem_lam_tron = 0.0
            nghiem.append(nghiem_lam_tron)

        return self._kiem_tra_va_dinh_dang_nghiem(nghiem, matrix, so_an)

    def _kiem_tra_va_dinh_dang_nghiem(self, nghiem: List[float], matrix_ban_dau: List[List[float]], so_an: int) -> str:
        """Kiểm tra và định dạng nghiệm"""
        eps = 1e-6
        max_sai_so = 0.0

        for i in range(so_an):
            tong = 0.0
            for j in range(so_an):
                tong += matrix_ban_dau[i][j] * nghiem[j]
            sai_so = abs(tong - matrix_ban_dau[i][so_an])
            max_sai_so = max(max_sai_so, sai_so)

        if max_sai_so > eps:
            return f"⚠️ Nghiệm gần đúng (sai số: {max_sai_so:.2e})\n" + self._dinh_dang_ket_qua(nghiem, so_an)

        return self._dinh_dang_ket_qua(nghiem, so_an)

    def _dinh_dang_ket_qua(self, nghiem: List[float], so_an: int) -> str:
        """Định dạng kết quả nghiệm"""
        if all(abs(x) < 1e-10 for x in nghiem):
            return "✅ Nghiệm tầm thường: Tất cả ẩn = 0"

        if so_an == 2:
            return f"✅ x = {nghiem[0]:.6g}, y = {nghiem[1]:.6g}"
        elif so_an == 3:
            return f"✅ x = {nghiem[0]:.6g}, y = {nghiem[1]:.6g}, z = {nghiem[2]:.6g}"
        elif so_an == 4:
            return f"✅ x₁ = {nghiem[0]:.6g}, x₂ = {nghiem[1]:.6g}, x₃ = {nghiem[2]:.6g}, x₄ = {nghiem[3]:.6g}"
        else:
            ket_qua = ", ".join([f"x_{i + 1} = {nghiem[i]:.6g}" for i in range(so_an)])
            return f"✅ {ket_qua}"