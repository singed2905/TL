# services/equation_actions.py
import tkinter as tk
from tkinter import messagebox, filedialog
import os
from datetime import datetime

from processors.excel_processor import ExcelProcessor

# IMPORT TỪ THƯ MỤC equation_services
from .equation import (
    EquationSolverService,
    BatchProcessingService,
    FileImportExportService,
    DataValidationService,
    EquationEncodingService
)


class EquationActions:
    def __init__(self, view, controller):
        self.view = view
        self.controller = controller
        self.excel_processor = ExcelProcessor()

        # Khởi tạo các service từ equation_services
        self.solver = EquationSolverService()
        self.batch_processor = BatchProcessingService(controller, self.excel_processor)
        self.file_service = FileImportExportService(self.excel_processor)
        self.validation_service = DataValidationService()
        self.encoding_service = EquationEncodingService(controller)

        # Biến lưu trữ file import
        self.imported_file_path = None
        self.imported_file_info = None

    def _xu_ly_du_lieu(self):
        """Xử lý dữ liệu - tự động phát hiện chế độ"""
        try:
            if self.imported_file_path and os.path.exists(self.imported_file_path):
                self._xu_ly_file_import()
            else:
                self._xu_ly_thu_cong()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi xử lý dữ liệu: {str(e)}")
            self._update_ui_error_state(str(e))

    def _xu_ly_thu_cong(self):
        """Xử lý mã hóa dữ liệu thủ công"""
        try:
            so_an = int(self.view.so_an_var.get())

            # Validate dữ liệu thủ công
            validation_result = self.validation_service.validate_manual_input(
                self.view.input_entries, so_an
            )

            if validation_result['all_empty']:
                self.view.status_label.config(text="Chưa có dữ liệu để xử lý")
                self.view.update_ket_qua_nghiem("Chưa có dữ liệu")
                return

            # Mã hóa dữ liệu
            encoding_result = self.encoding_service.encode_equation_data(
                validation_result['coefficients'],
                so_an,
                self.view.phien_ban_var.get()
            )

            if not encoding_result['success']:
                raise Exception(encoding_result['error'])

            # Giải hệ phương trình
            ket_qua_nghiem = self.solver.solve_equation_system(
                validation_result['coefficients'], so_an
            )

            # Cập nhật UI
            self._update_ui_with_results(
                encoding_result['encoded_coefficients'],
                ket_qua_nghiem,
                encoding_result['total_result'],
                validation_result['messages']
            )

        except Exception as e:
            raise Exception(f"Lỗi xử lý thủ công: {str(e)}")

    def _xu_ly_file_import(self):
        """Xử lý hàng loạt file Excel đã import"""
        try:
            if not self.imported_file_path:
                messagebox.showerror("Lỗi", "Không tìm thấy file import!")
                return

            so_an = int(self.view.so_an_var.get())
            file_name = os.path.basename(self.imported_file_path)

            self.view.status_label.config(text=f"⏳ Đang xử lý hàng loạt file: {file_name}...")
            self.view.window.update()

            # Xử lý hàng loạt
            results = self.batch_processor.process_batch_file(
                self.imported_file_path,
                so_an,
                self.view.phien_ban_var.get()
            )

            if not results:
                messagebox.showerror("Lỗi", "Không có dữ liệu hợp lệ để xử lý!")
                return

            # Xuất kết quả
            output_file = self.file_service.export_batch_results(
                self.imported_file_path, results, so_an
            )

            # Hiển thị kết quả tổng quan
            self._display_batch_results(results, output_file)

            # Hiển thị thông báo thành công
            success_count = sum(1 for r in results if r.get('trang_thai') == 'Thành công')
            error_count = sum(1 for r in results if r.get('trang_thai') == 'Lỗi')
            total_rows = len(results)

            messagebox.showinfo(
                "Xử lý hàng loạt hoàn tất",
                f"Đã xử lý {total_rows} dòng dữ liệu:\n"
                f"- Thành công: {success_count} dòng\n"
                f"- Lỗi: {error_count} dòng\n\n"
                f"Kết quả đã được lưu vào file:\n{output_file}"
            )

        except Exception as e:
            error_msg = f"Lỗi xử lý hàng loạt: {str(e)}"
            messagebox.showerror("Lỗi", error_msg)
            self.view.status_label.config(text=f"❌ {error_msg}")

    def _import_excel(self):
        """Import từ Excel"""
        try:
            if self.validation_service.check_existing_data(self.view.input_entries)['has_data']:
                self._show_import_warning()
                return

            file_path = filedialog.askopenfilename(
                title="Chọn file Excel để import",
                filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
            )

            if not file_path:
                self.view.status_label.config(text="❌ Không có file được chọn")
                return

            self.imported_file_path = file_path
            so_an = int(self.view.so_an_var.get())

            # Import file
            import_result = self.file_service.import_excel_file(file_path, so_an)

            if not import_result['success']:
                raise Exception(import_result['error'])

            self._handle_successful_import(import_result, file_path)

        except Exception as e:
            self._handle_import_error(e)

    # Các phương thức hỗ trợ UI
    def _update_ui_with_results(self, encoded_coefficients, ket_qua_nghiem, ket_qua_tong, adjustment_messages):
        """Cập nhật UI với kết quả xử lý"""
        # Hiển thị kết quả mã hóa
        for i, entry in enumerate(self.view.result_entries):
            if i < len(encoded_coefficients):
                entry.config(state='normal')
                entry.delete(0, tk.END)
                entry.insert(0, encoded_coefficients[i])
                entry.config(state='readonly')

        # Hiển thị kết quả nghiệm và tổng
        self.view.update_ket_qua_nghiem(ket_qua_nghiem)
        self.view.entry_tong.delete(0, tk.END)
        self.view.entry_tong.insert(0, ket_qua_tong)

        # Thông báo trạng thái
        status_message = "Đã xử lý mã hóa và tính nghiệm thành công"
        if adjustment_messages:
            status_message += f" ({', '.join(adjustment_messages)})"
        self.view.status_label.config(text=status_message)

    def _update_ui_error_state(self, error_message):
        """Cập nhật UI khi có lỗi"""
        self.view.entry_tong.delete(0, tk.END)
        self.view.entry_tong.insert(0, "❌ Lỗi khi xử lý dữ liệu")
        self.view.update_ket_qua_nghiem(f"❌ Lỗi: {error_message}")

    def _display_batch_results(self, results, output_file):
        """Hiển thị kết quả xử lý hàng loạt"""
        success_count = sum(1 for r in results if r.get('trang_thai') == 'Thành công')
        error_count = sum(1 for r in results if r.get('trang_thai') == 'Lỗi')
        total_rows = len(results)

        self.view.entry_tong.delete(0, tk.END)
        self.view.entry_tong.insert(0,
                                    f"📊 Đã xử lý {success_count}/{total_rows} dòng - File: {os.path.basename(output_file)}")

        self.view.update_ket_qua_nghiem(f"✅ Xử lý hàng loạt hoàn tất: {success_count} thành công, {error_count} lỗi")

        self.view.status_label.config(
            text=f"✅ Đã xử lý hàng loạt: {success_count} thành công, {error_count} lỗi - Kết quả: {os.path.basename(output_file)}"
        )

    def _handle_successful_import(self, import_result, file_path):
        """Xử lý import thành công"""
        file_info = import_result['file_info']
        quality_info = import_result['quality_info']
        file_name = os.path.basename(file_path)

        if not quality_info['valid']:
            warning_msg = f"File có vấn đề: {len(quality_info['data_issues'])} dòng lỗi"
            messagebox.showwarning("Cảnh báo chất lượng dữ liệu", warning_msg)

        total_rows = file_info['total_rows']
        valid_rows = quality_info['rows_with_data']

        self.view.entry_tong.delete(0, tk.END)
        self.view.entry_tong.insert(0, f"📁 {file_name} ({valid_rows}/{total_rows} dòng có dữ liệu)")

        self.view.update_ket_qua_nghiem(f"📊 File: {file_name} - Sẵn sàng xử lý hàng loạt")

        self.view.status_label.config(
            text=f"✅ Đã import: {file_name} ({valid_rows}/{total_rows} dòng có dữ liệu). Nhấn 'Xử lý' để xử lý hàng loạt."
        )

        self.view.set_imported_mode(True)

    def _handle_import_error(self, error):
        """Xử lý lỗi import"""
        self.imported_file_path = None
        self.imported_file_info = None

        error_msg = f"Không thể import file Excel: {str(error)}"
        messagebox.showerror("Lỗi", error_msg)
        self.view.status_label.config(text=f"❌ {error_msg}")

    def _show_import_warning(self):
        """Hiển thị cảnh báo khi đã có dữ liệu"""
        status = self.validation_service.check_existing_data(self.view.input_entries)

        warning_message = (
            f"❌ KHÔNG THỂ IMPORT\n\n"
            f"Các ô nhập liệu đã có dữ liệu:\n"
            f"- Số ô đã điền: {status['filled_count']}/{status['total_count']}\n"
            f"- Số ô trống: {status['empty_count']}/{status['total_count']}\n\n"
            f"Vui lòng xóa dữ liệu hiện tại trước khi import.\n\n"
            f"Bạn có thể:\n"
            f"1. Nhấn 'Quay lại' để xóa dữ liệu hiện tại\n"
            f"2. Import file Excel khác sau khi xóa dữ liệu"
        )

        messagebox.showwarning("Cảnh báo", warning_message)
        self.view.status_label.config(text="Không thể import - Đã có dữ liệu trong ô nhập")
        self.view.entry_tong.delete(0, tk.END)
        self.view.entry_tong.insert(0, "❌ Import thất bại: Đã có dữ liệu")

    def _import_excel_khac(self):
        """Import file Excel khác"""
        try:
            self.imported_file_path = None
            self.imported_file_info = None
            self._import_excel()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể import file Excel khác: {str(e)}")

    def _quay_lai(self):
        """Xử lý khi nhấn nút Quay lại"""
        try:
            if self.imported_file_path:
                result = messagebox.askyesno(
                    "Xác nhận",
                    "Bạn có chắc muốn quay lại trạng thái nhập liệu thủ công?\nFile import hiện tại sẽ bị hủy."
                )
                if not result:
                    return

            self.imported_file_path = None
            self.imported_file_info = None

            self.view.entry_tong.delete(0, tk.END)
            self.view.entry_tong.insert(0, "Chưa có kết quả tổng")
            self.view.update_ket_qua_nghiem("Chưa có kết quả nghiệm")

            self.view.set_imported_mode(False)
            self.view.clear_all_input_fields()

            self.view.status_label.config(text="🟢 Đã quay lại trạng thái nhập liệu thủ công")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể quay lại: {str(e)}")