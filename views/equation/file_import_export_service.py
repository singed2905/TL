# services/file_import_export_service.py
import os
import pandas as pd
from tkinter import filedialog, messagebox
from datetime import datetime
from processors.excel_processor import ExcelProcessor


class FileImportExportService:
    def __init__(self, excel_processor: ExcelProcessor):
        self.excel_processor = excel_processor

    def import_excel_file(self, file_path: str, so_an: int) -> dict:
        """Import file Excel và trả về thông tin file"""
        try:
            file_info = self.excel_processor.get_file_info(file_path)
            df = self.excel_processor.read_excel_data(file_path)

            # Validate cấu trúc
            is_valid, missing_cols = self.excel_processor.validate_equation_structure_by_phuong_trinh(df, so_an)
            if not is_valid:
                raise Exception(f"File thiếu các cột: {', '.join(missing_cols)}")

            # Kiểm tra chất lượng dữ liệu
            quality_info = self.excel_processor.validate_equation_data_quality(df, so_an)

            return {
                'file_info': file_info,
                'quality_info': quality_info,
                'success': True
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def export_batch_results(self, original_file_path: str, results: list, so_an: int) -> str:
        """Xuất kết quả xử lý hàng loạt ra file Excel mới"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"equation_batch_results_{so_an}an_{timestamp}.xlsx"

            output_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Lưu kết quả xử lý hàng loạt",
                initialfile=output_filename
            )

            if not output_path:
                raise Exception("Chưa chọn nơi lưu file kết quả")

            output_file = self.excel_processor.export_batch_results(
                original_file_path,
                results,
                output_path,
                so_an
            )

            return output_file

        except Exception as e:
            raise Exception(f"Lỗi xuất kết quả: {str(e)}")

    def create_excel_template(self, so_an: int) -> str:
        """Tạo file Excel template cho equation mode"""
        try:
            template_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Lưu template Excel",
                initialfile=f"equation_template_{so_an}an.xlsx"
            )

            if template_path:
                output_path = self.excel_processor.create_equation_template(so_an, template_path)
                return output_path
            else:
                raise Exception("Chưa chọn nơi lưu template")

        except Exception as e:
            raise Exception(f"Không thể tạo template Excel: {str(e)}")