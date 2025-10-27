# services/data_validation_service.py
from typing import Dict, Any, List


class DataValidationService:
    def __init__(self):
        pass

    def check_existing_data(self, input_entries: List) -> Dict[str, Any]:
        """Kiểm tra xem các ô nhập liệu đã có dữ liệu chưa"""
        try:
            filled_count = 0
            total_count = len(input_entries)

            for entry in input_entries:
                if entry.get().strip():
                    filled_count += 1

            return {
                'has_data': filled_count > 0,
                'filled_count': filled_count,
                'total_count': total_count,
                'empty_count': total_count - filled_count
            }

        except Exception as e:
            print(f"Lỗi khi kiểm tra dữ liệu hiện có: {e}")
            return {'has_data': False, 'filled_count': 0, 'total_count': 0, 'empty_count': 0}

    def validate_manual_input(self, input_entries: List, so_an: int) -> Dict[str, Any]:
        """Validate dữ liệu nhập thủ công"""
        try:
            validation_result = {
                'is_valid': True,
                'messages': [],
                'coefficients': [],
                'has_empty_fields': False
            }

            required_per_equation = so_an + 1
            all_empty = True

            for i, entry in enumerate(input_entries):
                value = entry.get().strip()

                if value:
                    all_empty = False
                    parts = [part.strip() for part in value.split(',')]

                    # Thay thế phần tử trống bằng '0'
                    processed_parts = []
                    for part in parts:
                        if part == "":
                            processed_parts.append('0')
                            validation_result['messages'].append(f"điền 0 cho PT {i + 1}")
                        else:
                            processed_parts.append(part)

                    parts = processed_parts

                    # Điều chỉnh số lượng hệ số
                    if len(parts) < required_per_equation:
                        missing_count = required_per_equation - len(parts)
                        parts.extend(['0'] * missing_count)
                        validation_result['messages'].append(f"điền {missing_count} số 0 cho PT {i + 1}")

                    elif len(parts) > required_per_equation:
                        parts = parts[:required_per_equation]
                        validation_result['messages'].append(f"cắt bớt hệ số thừa ở PT {i + 1}")

                    validation_result['coefficients'].extend(parts)
                else:
                    validation_result['coefficients'].extend(['0'] * required_per_equation)
                    validation_result['has_empty_fields'] = True
                    if not all_empty:
                        validation_result['messages'].append(f"điền 0 cho PT {i + 1} (trống)")

            validation_result['all_empty'] = all_empty
            return validation_result

        except Exception as e:
            raise Exception(f"Lỗi validate dữ liệu thủ công: {str(e)}")