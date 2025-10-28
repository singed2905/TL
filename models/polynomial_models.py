"""
Polynomial Models - Xử lý logic giải phương trình đa thức
Hỗ trợ giải phương trình bậc 2, 3, 4 với các phương pháp toán học chính xác
"""

import numpy as np
import sympy as sp
import cmath
import math
from typing import List, Union, Tuple, Dict, Any
from decimal import Decimal, getcontext

# Set precision for decimal calculations
getcontext().prec = 28


class PolynomialSolver:
    """
    Class chính để giải phương trình đa thức bậc cao
    Sử dụng các thuật toán toán học chuẩn và thư viện SymPy
    """

    def __init__(self):
        """Initialize solver với symbol và các cấu hình"""
        self.x = sp.Symbol('x', real=True)
        self.tolerance = 1e-10

    def validate_coefficients(self, coefficients: List[Union[str, float, int]], degree: int) -> List[float]:
        if len(coefficients) != degree + 1:
            raise ValueError(f"Cần {degree + 1} hệ số cho phương trình bậc {degree}")

        processed_coeffs = []
        for i, coeff in enumerate(coefficients):
            try:
                if coeff is None or coeff == "":
                    processed_coeffs.append(0.0)
                elif isinstance(coeff, (int, float)):
                    processed_coeffs.append(float(coeff))
                elif isinstance(coeff, str):
                    processed_coeffs.append(self._parse_expression(coeff))
                else:
                    raise ValueError(f"Hệ số {i} không hợp lệ: {coeff}")
            except Exception as e:
                raise ValueError(f"Lỗi parse hệ số {i}: {coeff} - {str(e)}")

        if abs(processed_coeffs[0]) < self.tolerance:
            raise ValueError(f"Hệ số đầu tiên (a) không được bằng 0 cho phương trình bậc {degree}")

        return processed_coeffs

    def _parse_expression(self, expr_str: str) -> float:
        """
        Parse biểu thức toán học từ string
        Hỗ trợ: sqrt(), sin(), cos(), tan(), log(), ln(), pi, e, fractions, powers

        Args:
            expr_str: String biểu thức (vd: "sqrt(5)", "sin(pi/2)", "1/2")

        Returns:
            float: Giá trị số của biểu thức
        """
        try:
            # Replace common expressions
            expr_str = expr_str.replace("^", "**")  # Power notation
            expr_str = expr_str.replace("ln", "log")  # Natural log

            # Use SymPy to evaluate mathematical expressions safely
            expr = sp.sympify(expr_str)
            result = float(expr.evalf())

            if math.isnan(result) or math.isinf(result):
                raise ValueError("Biểu thức tạo ra giá trị không hợp lệ")

            return result

        except Exception as e:
            raise ValueError(f"Không thể parse biểu thức '{expr_str}': {str(e)}")

    def solve_quadratic(self, coefficients: List[float]) -> Dict[str, Any]:
        """
        Giải phương trình bậc 2: ax² + bx + c = 0
        Sử dụng công thức nghiệm và discriminant analysis

        Args:
            coefficients: [a, b, c]

        Returns:
            Dict chứa nghiệm và thông tin phân tích
        """
        a, b, c = coefficients

        # Tính discriminant
        discriminant = b * b - 4 * a * c

        result = {
            'degree': 2,
            'coefficients': coefficients,
            'discriminant': discriminant,
            'roots': [],
            'root_types': [],
            'analysis': {}
        }

        if abs(discriminant) < self.tolerance:
            # Nghiệm kép
            root = -b / (2 * a)
            result['roots'] = [root, root]
            result['root_types'] = ['real_double', 'real_double']
            result['analysis']['type'] = 'Nghiệm kép thực'

        elif discriminant > 0:
            # Hai nghiệm thực phân biệt
            sqrt_d = math.sqrt(discriminant)
            root1 = (-b + sqrt_d) / (2 * a)
            root2 = (-b - sqrt_d) / (2 * a)
            result['roots'] = [root1, root2]
            result['root_types'] = ['real', 'real']
            result['analysis']['type'] = 'Hai nghiệm thực phân biệt'

        else:
            # Nghiệm phức
            sqrt_d = math.sqrt(-discriminant)
            real_part = -b / (2 * a)
            imag_part = sqrt_d / (2 * a)
            root1 = complex(real_part, imag_part)
            root2 = complex(real_part, -imag_part)
            result['roots'] = [root1, root2]
            result['root_types'] = ['complex', 'complex']
            result['analysis']['type'] = 'Hai nghiệm phức liên hợp'

        # Thêm thông tin phân tích
        result['analysis'].update({
            'discriminant_value': discriminant,
            'vertex_x': -b / (2 * a),
            'vertex_y': a * (-b / (2 * a)) ** 2 + b * (-b / (2 * a)) + c,
            'axis_of_symmetry': f'x = {-b / (2 * a):.6f}',
            'opens': 'upward' if a > 0 else 'downward'
        })

        return result

    def solve_cubic(self, coefficients: List[float]) -> Dict[str, Any]:
        """
        Giải phương trình bậc 3: ax³ + bx² + cx + d = 0
        Sử dụng phương pháp Cardano và SymPy

        Args:
            coefficients: [a, b, c, d]

        Returns:
            Dict chứa nghiệm và thông tin phân tích
        """
        a, b, c, d = coefficients

        # Sử dụng SymPy để giải chính xác
        polynomial = a * self.x ** 3 + b * self.x ** 2 + c * self.x + d
        roots_sympy = sp.solve(polynomial, self.x)

        result = {
            'degree': 3,
            'coefficients': coefficients,
            'roots': [],
            'root_types': [],
            'analysis': {}
        }

        # Convert SymPy results to numerical values
        for root in roots_sympy:
            try:
                # Try to get numerical value
                numerical_root = complex(root.evalf())

                if abs(numerical_root.imag) < self.tolerance:
                    # Real root
                    result['roots'].append(float(numerical_root.real))
                    result['root_types'].append('real')
                else:
                    # Complex root
                    result['roots'].append(numerical_root)
                    result['root_types'].append('complex')

            except Exception:
                # If numerical evaluation fails, keep symbolic
                result['roots'].append(root)
                result['root_types'].append('symbolic')

        # Analysis
        real_roots = sum(1 for rt in result['root_types'] if rt == 'real')
        complex_roots = len(result['roots']) - real_roots

        result['analysis'] = {
            'real_roots_count': real_roots,
            'complex_roots_count': complex_roots,
            'type': self._get_cubic_type(real_roots, complex_roots)
        }

        return result

    def solve_quartic(self, coefficients: List[float]) -> Dict[str, Any]:
        """
        Giải phương trình bậc 4: ax⁴ + bx³ + cx² + dx + e = 0
        Sử dụng phương pháp Ferrari và SymPy

        Args:
            coefficients: [a, b, c, d, e]

        Returns:
            Dict chứa nghiệm và thông tin phân tích
        """
        a, b, c, d, e = coefficients

        # Sử dụng SymPy để giải
        polynomial = a * self.x ** 4 + b * self.x ** 3 + c * self.x ** 2 + d * self.x + e
        roots_sympy = sp.solve(polynomial, self.x)

        result = {
            'degree': 4,
            'coefficients': coefficients,
            'roots': [],
            'root_types': [],
            'analysis': {}
        }

        # Process roots similar to cubic
        for root in roots_sympy:
            try:
                numerical_root = complex(root.evalf())

                if abs(numerical_root.imag) < self.tolerance:
                    result['roots'].append(float(numerical_root.real))
                    result['root_types'].append('real')
                else:
                    result['roots'].append(numerical_root)
                    result['root_types'].append('complex')

            except Exception:
                result['roots'].append(root)
                result['root_types'].append('symbolic')

        # Analysis
        real_roots = sum(1 for rt in result['root_types'] if rt == 'real')
        complex_roots = len(result['roots']) - real_roots

        result['analysis'] = {
            'real_roots_count': real_roots,
            'complex_roots_count': complex_roots,
            'type': self._get_quartic_type(real_roots, complex_roots)
        }

        return result

    def _get_cubic_type(self, real_count: int, complex_count: int) -> str:
        """Phân loại phương trình bậc 3 theo nghiệm"""
        if real_count == 3:
            return "Ba nghiệm thực"
        elif real_count == 1:
            return "Một nghiệm thực, hai nghiệm phức liên hợp"
        else:
            return "Trường hợp đặc biệt"

    def _get_quartic_type(self, real_count: int, complex_count: int) -> str:
        """Phân loại phương trình bậc 4 theo nghiệm"""
        if real_count == 4:
            return "Bốn nghiệm thực"
        elif real_count == 2:
            return "Hai nghiệm thực, hai nghiệm phức liên hợp"
        elif real_count == 0:
            return "Bốn nghiệm phức (hai cặp liên hợp)"
        else:
            return "Trường hợp đặc biệt"

    def format_roots(self, result: Dict[str, Any], precision: int = 6) -> Dict[str, str]:
        """
        Format kết quả nghiệm để hiển thị

        Args:
            result: Kết quả từ solve methods
            precision: Số chữ số thập phân

        Returns:
            Dict chứa formatted strings
        """
        formatted = {
            'equation': self._format_equation(result['coefficients'], result['degree']),
            'roots_display': [],
            'summary': '',
            'analysis': result['analysis']
        }

        # Format từng nghiệm
        for i, (root, root_type) in enumerate(zip(result['roots'], result['root_types'])):
            if root_type == 'real':
                formatted['roots_display'].append(f"x₁ = {root:.{precision}f}")
            elif root_type == 'complex':
                if isinstance(root, complex):
                    if root.imag >= 0:
                        formatted['roots_display'].append(
                            f"x₁ = {root.real:.{precision}f} + {root.imag:.{precision}f}i"
                        )
                    else:
                        formatted['roots_display'].append(
                            f"x₁ = {root.real:.{precision}f} - {abs(root.imag):.{precision}f}i"
                        )
            else:
                # Symbolic root
                formatted['roots_display'].append(f"x₁ = {str(root)}")

        # Tạo summary
        formatted['summary'] = f"Phương trình {formatted['equation']} có {len(result['roots'])} nghiệm"

        return formatted

    def _format_equation(self, coeffs: List[float], degree: int) -> str:
        """Format phương trình để hiển thị"""
        terms = []
        variables = ['', 'x', 'x²', 'x³', 'x⁴']

        for i, coeff in enumerate(coeffs):
            power = degree - i
            if abs(coeff) < self.tolerance:
                continue

            # Format coefficient
            if i == 0:  # First term
                if coeff == 1 and power > 0:
                    term = variables[power]
                elif coeff == -1 and power > 0:
                    term = f"-{variables[power]}"
                else:
                    term = f"{coeff:g}{variables[power]}"
            else:  # Other terms
                if coeff > 0:
                    if coeff == 1 and power > 0:
                        term = f" + {variables[power]}"
                    else:
                        term = f" + {coeff:g}{variables[power]}"
                else:
                    if coeff == -1 and power > 0:
                        term = f" - {variables[power]}"
                    else:
                        term = f" - {abs(coeff):g}{variables[power]}"

            terms.append(term)

        equation = "".join(terms) + " = 0"
        return equation.strip()

    def solve_polynomial(self, degree: int, coefficients: List[Union[str, float, int]]) -> Dict[str, Any]:
        """
        Method chính để giải phương trình theo bậc

        Args:
            degree: Bậc phương trình (2, 3, 4)
            coefficients: List hệ số

        Returns:
            Dict kết quả hoàn chỉnh
        """
        try:
            # Validate coefficients
            valid_coeffs = self.validate_coefficients(coefficients, degree)

            # Solve based on degree
            if degree == 2:
                result = self.solve_quadratic(valid_coeffs)
            elif degree == 3:
                result = self.solve_cubic(valid_coeffs)
            elif degree == 4:
                result = self.solve_quartic(valid_coeffs)
            else:
                raise ValueError(f"Không hỗ trợ bậc {degree}")

            # Add formatted output
            result['formatted'] = self.format_roots(result)
            result['success'] = True
            result['error'] = None

            return result

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'degree': degree,
                'coefficients': coefficients
            }


# Utility functions for external use
def quick_solve(degree: int, coefficients: List[Union[str, float, int]]) -> Dict[str, Any]:
    """
    Quick solve function for external usage
    """
    solver = PolynomialSolver()
    return solver.solve_polynomial(degree, coefficients)


def validate_polynomial_input(coefficients: List[str], degree: int) -> Tuple[bool, str]:
    """
    Validate input without solving
    Returns: (is_valid, error_message)
    """
    try:
        solver = PolynomialSolver()
        solver.validate_coefficients(coefficients, degree)
        return True, ""
    except Exception as e:
        return False, str(e)


# Example usage and testing
if __name__ == "__main__":
    solver = PolynomialSolver()

    print("=== Test Quadratic ===")
    result = solver.solve_polynomial(2, ["1", "2", "2"])  # x² - 5x + 6 = 0

    if result.get("success"):
        print(f"Equation: {result['formatted']['equation']}")
        print(f"Roots: {result['formatted']['roots_display']}")
        print(f"Analysis: {result['analysis']}")
    else:
        print(f"❌ Error: {result['error']}")