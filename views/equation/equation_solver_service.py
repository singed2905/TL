import math
import re
import json
from typing import List, Tuple


class EquationSolverService:
    def __init__(self):
        self.eps = 1e-10
        self.math_config = self._load_math_replacements()

    def _load_math_replacements(self):
        """Load math replacements từ JSON config"""
        try:
            with open('config/math_replacements.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Lỗi load math config: {e}")
            return self._get_default_replacements()

    def _get_default_replacements(self):
        """Fallback config nếu JSON không load được"""
        return {
            "math_function_replacements": {
                "operators": {
                    "^": {"python_equivalent": "**"}
                },
                "functions": {
                    "sqrt": {"python_equivalent": "math.sqrt"},
                    "sin": {"python_equivalent": "math.sin"},
                    "cos": {"python_equivalent": "math.cos"},
                    "tan": {"python_equivalent": "math.tan"},
                    "log": {"python_equivalent": "math.log10"},
                    "ln": {"python_equivalent": "math.log"},
                    "abs": {"python_equivalent": "abs"},
                    "exp": {"python_equivalent": "math.exp"}
                },
                "constants": {
                    "pi": {"python_equivalent": "math.pi"},
                    "e": {"python_equivalent": "math.e"}
                }
            },
            "latex_symbol_replacements": {
                "mathematical_operators": {
                    r'\\pi': {"python_equivalent": "math.pi"},
                    r'\\cdot': {"python_equivalent": "*"},
                    r'\\times': {"python_equivalent": "*"},
                    r'\\div': {"python_equivalent": "/"}
                },
                "delimiters": {
                    r'\\left\(': {"python_equivalent": "("},
                    r'\\right\)': {"python_equivalent": ")"},
                    r'\\left\{': {"python_equivalent": "("},
                    r'\\right\}': {"python_equivalent": ")"}
                },
                "whitespace": {
                    r'\\ ': {"python_equivalent": " "},
                    r'\ ': {"python_equivalent": " "}
                }
            },
            "safe_evaluation_environment": {
                "allowed_modules": {
                    "math": {"description": "Python math module"}
                },
                "allowed_builtins": {
                    "abs": {"safe": True},
                    "round": {"safe": True},
                    "min": {"safe": True},
                    "max": {"safe": True}
                }
            }
        }

    def _get_replacements_dict(self):
        """Tạo dict replacements từ JSON config"""
        config = self.math_config
        replacements = {}

        # Load operators  
        operators = config['math_function_replacements']['operators']
        for key, value in operators.items():
            replacements[key] = value['python_equivalent']

        # Load functions
        functions = config['math_function_replacements']['functions']
        for key, value in functions.items():
            replacements[key] = value['python_equivalent']

        # Load constants
        constants = config['math_function_replacements']['constants']
        for key, value in constants.items():
            replacements[key] = value['python_equivalent']

        return replacements

    def _get_safe_dict(self):
        """Tạo safe evaluation environment từ JSON"""
        config = self.math_config['safe_evaluation_environment']

        safe_dict = {'__builtins__': {}}

        # Add math module
        if 'math' in config['allowed_modules']:
            safe_dict['math'] = math

        # Add allowed builtins
        allowed_builtins = config['allowed_builtins']
        for func_name, func_config in allowed_builtins.items():
            if func_config['safe']:
                safe_dict[func_name] = eval(func_name)

        return safe_dict

    def _get_latex_replacements(self):
        """Load LaTeX replacements từ JSON"""
        config = self.math_config['latex_symbol_replacements']
        latex_replacements = {}

        # Mathematical operators
        math_ops = config['mathematical_operators']
        latex_replacements.update({k: v['python_equivalent'] for k, v in math_ops.items()})

        # Delimiters  
        delims = config['delimiters']
        latex_replacements.update({k: v['python_equivalent'] for k, v in delims.items()})

        # Whitespace
        whitespace = config['whitespace']
        latex_replacements.update({k: v['python_equivalent'] for k, v in whitespace.items()})

        return latex_replacements

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

        # Sử dụng config từ JSON thay vì hardcode
        replacements = self._get_replacements_dict()

        for old, new in replacements.items():
            expr = expr.replace(old, new)

        # Sử dụng safe dict từ JSON config
        safe_dict = self._get_safe_dict()

        try:
            result = eval(expr, safe_dict)
            return float(result)
        except Exception as e:
            raise ValueError(f"Không thể đánh giá: '{expr}'")

    def _convert_latex_to_python(self, expr: str) -> str:
        """Chuyển đổi biểu thức LaTeX sang Python"""
        expr = self._convert_latex_fractions(expr)

        # Sử dụng LaTeX replacements từ JSON config
        latex_replacements = self._get_latex_replacements()

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

    def reload_math_config(self):
        """Reload lại math configuration (hữu ích cho development)"""
        try:
            self.math_config = self._load_math_replacements()
            return True
        except Exception as e:
            print(f"Lỗi khi reload math config: {e}")
            return False

    def get_supported_functions(self):
        """Lấy danh sách các functions được hỗ trợ"""
        config = self.math_config
        functions = list(config['math_function_replacements']['functions'].keys())
        constants = list(config['math_function_replacements']['constants'].keys())
        operators = list(config['math_function_replacements']['operators'].keys())

        return {
            'functions': functions,
            'constants': constants,
            'operators': operators
        }

    def validate_expression(self, expr: str) -> dict:
        """Validate biểu thức trước khi eval"""
        try:
            # Test conversion
            converted = self._convert_latex_to_python(expr)

            # Test replacements
            replacements = self._get_replacements_dict()
            for old, new in replacements.items():
                converted = converted.replace(old, new)

            return {
                'valid': True,
                'original': expr,
                'converted': converted,
                'message': 'Biểu thức hợp lệ'
            }
        except Exception as e:
            return {
                'valid': False,
                'original': expr,
                'converted': '',
                'message': f'Lỗi: {str(e)}'
            }