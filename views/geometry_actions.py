# geometry_actions.py
import tkinter as tk
from shlex import shlex
from tkinter import messagebox, filedialog, ttk
import os
from datetime import datetime


class GeometryActions:
    def __init__(self, view, controller):
        self.view = view
        self.controller = controller

    # === XỬ LÝ NHÓM A ===
    def _thuc_thi_A(self):
        """Process group A data"""
        try:
            # Update controller state
            self.controller.set_current_shapes(
                self.view.dropdown1_var.get(),
                self.view.dropdown2_var.get()
            )
            self.controller.set_kich_thuoc(
                self.view.kich_thuoc_A_var.get(),
                self.view.kich_thuoc_B_var.get()
            )

            # Collect data from UI
            data_dict = self._get_group_A_data()

            # Process data through controller
            result = self.controller.thuc_thi_A(data_dict)

            # Update UI with results
            self._update_group_A_results(result)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý nhóm A: {str(e)}")

    # === XỬ LÝ NHÓM B ===
    def _thuc_thi_B(self):
        """Process group B data"""
        try:
            if self.view.pheptoan_var.get() in ["Diện tích", "Thể tích"]:
                return

            # Update controller state
            self.controller.set_current_shapes(
                self.view.dropdown1_var.get(),
                self.view.dropdown2_var.get()
            )
            self.controller.set_kich_thuoc(
                self.view.kich_thuoc_A_var.get(),
                self.view.kich_thuoc_B_var.get()
            )

            # Collect data from UI
            data_dict = self._get_group_B_data()

            # Process data through controller
            result = self.controller.thuc_thi_B(data_dict)

            # Update UI with results
            self._update_group_B_results(result)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi xử lý nhóm B: {str(e)}")

    # === XỬ LÝ TẤT CẢ ===
    def _thuc_thi_tat_ca(self):
        """Process all groups and generate result"""
        try:
            # Update controller state
            self.controller.set_current_shapes(
                self.view.dropdown1_var.get(),
                self.view.dropdown2_var.get()
            )
            self.controller.set_kich_thuoc(
                self.view.kich_thuoc_A_var.get(),
                self.view.kich_thuoc_B_var.get()
            )
            self.controller.current_operation = self.view.pheptoan_var.get()

            # Process all data
            data_dict_A = self._get_group_A_data()
            data_dict_B = self._get_group_B_data() if self.view.pheptoan_var.get() not in ["Diện tích", "Thể tích"] else {}

            self.controller.thuc_thi_tat_ca(data_dict_A, data_dict_B)

            # Generate final result
            result = self.controller.generate_final_result()
            self.view.update_final_result_display(result)

        except Exception as e:
            error_msg = f"Lỗi xử lý dữ liệu: {str(e)}"
            self.view.update_final_result_display(error_msg)
            messagebox.showerror("Lỗi xử lý", error_msg)

    # === IMPORT/EXPORT ===
    def _import_from_excel(self):
        """Import data from Excel file hoặc import file khác"""
        try:
            # Nếu đang trong chế độ import, cho phép import file khác
            if self.view.imported_data:
                response = messagebox.askyesno("Import file khác",
                                               "Bạn có muốn import file Excel khác? Dữ liệu cũ sẽ bị thay thế.")
                if not response:
                    return

            # Mở hộp thoại chọn file
            file_path = filedialog.askopenfilename(
                title="Chọn file Excel để import",
                filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
            )

            if not file_path:
                return

            # Đánh dấu đã import
            self.view.imported_data = True

            # Khóa tất cả các ô nhập liệu
            self._lock_all_input_entries()

            # Hiện nút cho chế độ import
            self.view._show_import_buttons()

            # Ẩn nút Import Excel ban đầu
            self.view.btn_import_excel.grid_remove()

            self.view.imported_file_path = file_path

            # HIỂN THỊ TÊN FILE EXCEL TRONG Ô KẾT QUẢ TỔNG
            file_name = os.path.basename(file_path)
            self.view.update_final_result_display(f"📁 Đã import file: {file_name}")

            print(f"Đã import file: {file_path}")

        except Exception as e:
            error_msg = f"❌ Lỗi import: {str(e)}"
            self.view.update_final_result_display(error_msg)
            messagebox.showerror("Lỗi Import", f"Không thể import file Excel:\n{str(e)}")

    def _export_to_excel(self):
        """Export data to Excel với hộp thoại chọn nơi lưu"""
        try:
            # Kiểm tra xem có dữ liệu để xuất không
            export_info = self.controller.get_export_info()

            if not export_info['has_data_A']:
                response = messagebox.askyesno(
                    "Xác nhận",
                    "Chưa có dữ liệu nhóm A. Bạn có muốn xuất file với dữ liệu hiện tại không?"
                )
                if not response:
                    return

            # Xử lý tất cả dữ liệu trước để có kết quả mới nhất
            self._thuc_thi_tat_ca()

            # HIỂN THỊ HỘP THOẠI CHỌN NƠI LƯU FILE
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[
                    ("Excel files", "*.xlsx"),
                    ("All files", "*.*")
                ],
                title="Chọn nơi lưu file Excel",
                initialfile=f"geometry_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )

            # Nếu người dùng hủy bỏ
            if not file_path:
                return

            # Xuất ra Excel với đường dẫn đã chọn
            filename = self.controller.export_to_excel(file_path)

            # Hiển thị thông báo thành công
            messagebox.showinfo("Thành công", f"Đã xuất file Excel thành công!\n\nFile: {os.path.basename(filename)}")

            # Cập nhật ô hiển thị kết quả
            self.view.update_final_result_display(f"📁 Đã xuất file: {os.path.basename(filename)}")

        except Exception as e:
            error_msg = f"❌ Lỗi xuất file: {str(e)}"
            self.view.update_final_result_display(error_msg)
            if "openpyxl" in str(e):
                error_msg += "\n\nVui lòng cài đặt thư viện openpyxl:\npip install openpyxl"
            messagebox.showerror("Lỗi xuất Excel", error_msg)

    def _thuc_thi_import_excel(self):
        """Xử lý toàn bộ file Excel đã import"""
        try:
            if not self.view.imported_file_path:
                messagebox.showerror("Lỗi", "Chưa import file Excel!")
                return

            if not os.path.exists(self.view.imported_file_path):
                messagebox.showerror("Lỗi", "File Excel không tồn tại!")
                return

            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Chọn nơi lưu file kết quả",
                initialfile=f"geometry_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )

            if not file_path:  # Người dùng hủy
                return
            start_time = datetime.now()
            print("start time: " +start_time.strftime("%Y-%m-%d %H:%M:%S"))

            # Hiển thị thông báo đang xử lý
            self.view.update_final_result_display("🔄 Đang xử lý file Excel...")
            self.view.window.update()

            # Lấy thông tin từ UI
            shape_a = self.view.dropdown1_var.get()
            shape_b = self.view.dropdown2_var.get() if self.view.pheptoan_var.get() not in ["Diện tích", "Thể tích"] else None
            operation = self.view.pheptoan_var.get()
            dimension_a = self.view.kich_thuoc_A_var.get()
            dimension_b = self.view.kich_thuoc_B_var.get()

            # Gọi controller xử lý batch
            results, output_file, success_count, error_count = self.controller.process_excel_batch(
                self.view.imported_file_path, shape_a, shape_b, operation,
                dimension_a, dimension_b, output_path=file_path  # Truyền output_path
            )
            end_time = datetime.now()
            print("end time:" +end_time.strftime("%Y-%m-%d %H:%M:%S"))
            processing_time = end_time - start_time
            processing_seconds = processing_time.total_seconds()
            print(processing_seconds);

            # Hiển thị kết quả
            result_text = f"✅ Đã xử lý: {success_count} dòng thành công, {error_count} dòng lỗi"
            self.view.update_final_result_display(result_text)

            # Thông báo kết quả
            if error_count == 0:
                messagebox.showinfo(
                    "Thành công",
                    f"✅ ĐÃ XỬ LÝ THÀNH CÔNG!\n\n"
                    f"• Số dòng: {success_count} dòng\n"
                    f"• Thời gian bắt đầu: {start_time.strftime('%H:%M:%S')}\n"
                    f"• Thời gian kết thúc: {end_time.strftime('%H:%M:%S')}\n"
                    f"• Tổng thời gian: {processing_seconds:.2f} giây\n"
                    f"• Tốc độ: {success_count / processing_seconds:.1f} dòng/giây\n"
                    f"• File kết quả: {os.path.basename(output_file)}")
            else:
                messagebox.showwarning(
                    "Hoàn thành với lỗi",
                    f"⚠️ HOÀN THÀNH VỚI LỖI!\n\n"
                    f"• Thành công: {success_count} dòng\n"
                    f"• Lỗi: {error_count} dòng\n"
                    f"• Thời gian bắt đầu: {start_time.strftime('%H:%M:%S')}\n"
                    f"• Thời gian kết thúc: {end_time.strftime('%H:%M:%S')}\n"
                    f"• Tổng thời gian: {processing_seconds:.2f} giây\n"
                    f"• File kết quả: {os.path.basename(output_file)}"
                )

        except Exception as e:
            error_msg = f"❌ Lỗi xử lý file Excel: {str(e)}"
            self.view.update_final_result_display(error_msg)
            messagebox.showerror("Lỗi xử lý", f"Không thể xử lý file Excel:\n{str(e)}")

    # === QUẢN LÝ TRẠNG THÁI IMPORT ===
    def _quit_import_mode(self):
        """Thoát khỏi chế độ import Excel và quay lại nhập liệu thủ công"""
        try:
            # Đặt lại trạng thái import
            self.view.imported_data = False

            # Mở khóa tất cả các ô nhập liệu
            self._unlock_all_input_entries()

            # Xóa dữ liệu import (nếu cần)
            self._clear_imported_data()

            # Hiện lại nút Import Excel
            self.view.btn_import_excel.grid()

            # Ẩn frame nút import, hiện frame nút thủ công nếu có dữ liệu
            self.view.frame_buttons_import.grid_remove()
            if self.view._check_manual_data():
                self.view.frame_buttons_manual.grid()
            else:
                self.view._hide_action_buttons()

            # Hiển thị thông báo
            self.view.update_final_result_display("🔙 Đã thoát chế độ import, quay lại nhập liệu thủ công")

            print("Đã thoát chế độ import Excel, quay lại nhập liệu thủ công")

        except Exception as e:
            error_msg = f"❌ Lỗi thoát import: {str(e)}"
            self.view.update_final_result_display(error_msg)
            messagebox.showerror("Lỗi", f"Không thể thoát chế độ import: {str(e)}")

    def _lock_all_input_entries(self):
        """Khóa tất cả các ô nhập liệu"""
        entries = self.view._get_all_input_entries()
        for entry in entries:
            entry.config(state='disabled')

    def _unlock_all_input_entries(self):
        """Mở khóa tất cả các ô nhập liệu"""
        entries = self.view._get_all_input_entries()
        for entry in entries:
            entry.config(state='normal')

    def _clear_imported_data(self):
        """Xóa dữ liệu đã import (nếu cần)"""
        try:
            # Reset dữ liệu trong controller
            self.controller.raw_data_A = {}
            self.controller.raw_data_B = {}

            print("Đã xóa dữ liệu import")
        except Exception as e:
            print(f"Lỗi khi xóa dữ liệu import: {str(e)}")

    # === CÁC PHƯƠNG THỨC TRÍCH XUẤT DỮ LIỆU ===
    def _get_group_A_data(self):
        """Collect data from group A input fields based on current shape"""
        shape_type = self.view.dropdown1_var.get()
        data_dict = {}

        if shape_type == "Điểm":
            data_dict['point_input'] = self.view.entry_dau_vao_diem_A.get()

        elif shape_type == "Đường thẳng":
            data_dict['line_A1'] = self.view.entry_dau_vao_A1.get()
            data_dict['line_X1'] = self.view.entry_dau_vao_X1.get()

        elif shape_type == "Mặt phẳng":
            data_dict['plane_a'] = self.view.entry_N1_in.get()
            data_dict['plane_b'] = self.view.entry_N2_in.get()
            data_dict['plane_c'] = self.view.entry_N3_in.get()
            data_dict['plane_d'] = self.view.entry_N4_in.get()

        elif shape_type == "Đường tròn":
            data_dict['circle_center'] = self.view.entry_dau_vao_tam_duong_tron_A.get()
            data_dict['circle_radius'] = self.view.entry_dau_vao_ban_kinh_duong_tron_A.get()

        elif shape_type == "Mặt cầu":
            data_dict['sphere_center'] = self.view.entry_dau_vao_tam_mat_cau_A.get()
            data_dict['sphere_radius'] = self.view.entry_dau_vao_ban_kinh_mat_cau_A.get()

        return data_dict

    def _get_group_B_data(self):
        """Collect data from group B input fields based on current shape"""
        shape_type = self.view.dropdown2_var.get()
        data_dict = {}

        if shape_type == "Điểm":
            data_dict['point_input'] = self.view.entry_dau_vao_diem_B.get()

        elif shape_type == "Đường thẳng":
            data_dict['line_A2'] = self.view.entry_dau_vao_A2.get()
            data_dict['line_X2'] = self.view.entry_dau_vao_X2.get()

        elif shape_type == "Mặt phẳng":
            data_dict['plane_a'] = self.view.entry_N5_in.get()
            data_dict['plane_b'] = self.view.entry_N6_in.get()
            data_dict['plane_c'] = self.view.entry_N7_in.get()
            data_dict['plane_d'] = self.view.entry_N8_in.get()

        elif shape_type == "Đường tròn":
            data_dict['circle_center'] = self.view.entry_dau_vao_tam_duong_tron_B.get()
            data_dict['circle_radius'] = self.view.entry_dau_vao_ban_kinh_duong_tron_B.get()

        elif shape_type == "Mặt cầu":
            data_dict['sphere_center'] = self.view.entry_dau_vao_tam_mat_cau_B.get()
            data_dict['sphere_radius'] = self.view.entry_dau_vao_ban_kinh_mat_cau_B.get()

        return data_dict

    # === CÁC PHƯƠNG THỨC CẬP NHẬT GIAO DIỆN ===
    def _update_group_A_results(self, result):
        """Update group A result fields in UI"""
        shape_type = self.view.dropdown1_var.get()

        if shape_type == "Điểm":
            so_chieu = int(self.view.kich_thuoc_A_var.get())
            if so_chieu == 2:
                if len(result) >= 2:
                    self.view.entry_Xd_A.delete(0, tk.END)
                    self.view.entry_Xd_A.insert(0, result[0])
                    self.view.entry_Yd_A.delete(0, tk.END)
                    self.view.entry_Yd_A.insert(0, result[1])
            else:
                if len(result) >= 3:
                    self.view.entry_Xd_A.delete(0, tk.END)
                    self.view.entry_Xd_A.insert(0, result[0])
                    self.view.entry_Yd_A.delete(0, tk.END)
                    self.view.entry_Yd_A.insert(0, result[1])
                    self.view.entry_Zd_A.delete(0, tk.END)
                    self.view.entry_Zd_A.insert(0, result[2])

        elif shape_type == "Đường thẳng":
            if len(result) >= 6:
                self.view.entry_A1.delete(0, tk.END)
                self.view.entry_A1.insert(0, result[0])
                self.view.entry_B1.delete(0, tk.END)
                self.view.entry_B1.insert(0, result[1])
                self.view.entry_C1.delete(0, tk.END)
                self.view.entry_C1.insert(0, result[2])
                self.view.entry_X1.delete(0, tk.END)
                self.view.entry_X1.insert(0, result[3])
                self.view.entry_Y1.delete(0, tk.END)
                self.view.entry_Y1.insert(0, result[4])
                self.view.entry_Z1.delete(0, tk.END)
                self.view.entry_Z1.insert(0, result[5])

        elif shape_type == "Mặt phẳng":
            if len(result) >= 4:
                self.view.entry_N1_out.config(state='normal')
                self.view.entry_N2_out.config(state='normal')
                self.view.entry_N3_out.config(state='normal')
                self.view.entry_N4_out.config(state='normal')

                self.view.entry_N1_out.delete(0, tk.END)
                self.view.entry_N1_out.insert(0, result[0])
                self.view.entry_N2_out.delete(0, tk.END)
                self.view.entry_N2_out.insert(0, result[1])
                self.view.entry_N3_out.delete(0, tk.END)
                self.view.entry_N3_out.insert(0, result[2])
                self.view.entry_N4_out.delete(0, tk.END)
                self.view.entry_N4_out.insert(0, result[3])

                self.view.entry_N1_out.config(state='readonly')
                self.view.entry_N2_out.config(state='readonly')
                self.view.entry_N3_out.config(state='readonly')
                self.view.entry_N4_out.config(state='readonly')

        elif shape_type == "Đường tròn":
            if len(result) >= 3:
                self.view.entry_duong_tron_A1.delete(0, tk.END)
                self.view.entry_duong_tron_A1.insert(0, result[0])
                self.view.entry_duong_tron_A2.delete(0, tk.END)
                self.view.entry_duong_tron_A2.insert(0, result[1])
                self.view.entry_duong_tron_A3.delete(0, tk.END)
                self.view.entry_duong_tron_A3.insert(0, result[2])

        elif shape_type == "Mặt cầu":
            if len(result) >= 4:
                self.view.entry_mat_cau_A1.delete(0, tk.END)
                self.view.entry_mat_cau_A1.insert(0, result[0])
                self.view.entry_mat_cau_A2.delete(0, tk.END)
                self.view.entry_mat_cau_A2.insert(0, result[1])
                self.view.entry_mat_cau_A3.delete(0, tk.END)
                self.view.entry_mat_cau_A3.insert(0, result[2])
                self.view.entry_mat_cau_A4.delete(0, tk.END)
                self.view.entry_mat_cau_A4.insert(0, result[3])

    def _update_group_B_results(self, result):
        """Update group B result fields in UI"""
        shape_type = self.view.dropdown2_var.get()

        if shape_type == "Điểm":
            so_chieu = int(self.view.kich_thuoc_B_var.get())
            if so_chieu == 2:
                if len(result) >= 2:
                    self.view.entry_Xd_B.delete(0, tk.END)
                    self.view.entry_Xd_B.insert(0, result[0])
                    self.view.entry_Yd_B.delete(0, tk.END)
                    self.view.entry_Yd_B.insert(0, result[1])
            else:
                if len(result) >= 3:
                    self.view.entry_Xd_B.delete(0, tk.END)
                    self.view.entry_Xd_B.insert(0, result[0])
                    self.view.entry_Yd_B.delete(0, tk.END)
                    self.view.entry_Yd_B.insert(0, result[1])
                    self.view.entry_Zd_B.delete(0, tk.END)
                    self.view.entry_Zd_B.insert(0, result[2])

        elif shape_type == "Đường thẳng":
            if len(result) >= 6:
                self.view.entry_A2.delete(0, tk.END)
                self.view.entry_A2.insert(0, result[0])
                self.view.entry_B2.delete(0, tk.END)
                self.view.entry_B2.insert(0, result[1])
                self.view.entry_C2.delete(0, tk.END)
                self.view.entry_C2.insert(0, result[2])
                self.view.entry_X2.delete(0, tk.END)
                self.view.entry_X2.insert(0, result[3])
                self.view.entry_Y2.delete(0, tk.END)
                self.view.entry_Y2.insert(0, result[4])
                self.view.entry_Z2.delete(0, tk.END)
                self.view.entry_Z2.insert(0, result[5])

        elif shape_type == "Mặt phẳng":
            if len(result) >= 4:
                self.view.entry_N5_out.config(state='normal')
                self.view.entry_N6_out.config(state='normal')
                self.view.entry_N7_out.config(state='normal')
                self.view.entry_N8_out.config(state='normal')

                self.view.entry_N5_out.delete(0, tk.END)
                self.view.entry_N5_out.insert(0, result[0])
                self.view.entry_N6_out.delete(0, tk.END)
                self.view.entry_N6_out.insert(0, result[1])
                self.view.entry_N7_out.delete(0, tk.END)
                self.view.entry_N7_out.insert(0, result[2])
                self.view.entry_N8_out.delete(0, tk.END)
                self.view.entry_N8_out.insert(0, result[3])

                self.view.entry_N5_out.config(state='readonly')
                self.view.entry_N6_out.config(state='readonly')
                self.view.entry_N7_out.config(state='readonly')
                self.view.entry_N8_out.config(state='readonly')

        elif shape_type == "Đường tròn":
            if len(result) >= 3:
                self.view.entry_duong_tron_B1.delete(0, tk.END)
                self.view.entry_duong_tron_B1.insert(0, result[0])
                self.view.entry_duong_tron_B2.delete(0, tk.END)
                self.view.entry_duong_tron_B2.insert(0, result[1])
                self.view.entry_duong_tron_B3.delete(0, tk.END)
                self.view.entry_duong_tron_B3.insert(0, result[2])

        elif shape_type == "Mặt cầu":
            if len(result) >= 4:
                self.view.entry_mat_cau_B1.delete(0, tk.END)
                self.view.entry_mat_cau_B1.insert(0, result[0])
                self.view.entry_mat_cau_B2.delete(0, tk.END)
                self.view.entry_mat_cau_B2.insert(0, result[1])
                self.view.entry_mat_cau_B3.delete(0, tk.END)
                self.view.entry_mat_cau_B3.insert(0, result[2])
                self.view.entry_mat_cau_B4.delete(0, tk.END)
                self.view.entry_mat_cau_B4.insert(0, result[3])

    def _thuc_thi_import_excel_chunked(self):
        """Xử lý file Excel lớn với chunk processing"""
        try:
            if not self.view.imported_file_path:
                messagebox.showerror("Lỗi", "Chưa import file Excel!")
                return

            # Tạo progress window
            progress_window = self._create_progress_window()

            # Biến để theo dõi hủy
            self._cancellation_requested = False

            def update_progress(progress, current, total, success, errors):
                """Cập nhật tiến độ lên GUI"""
                progress_window.progress_var.set(progress)
                progress_window.status_label.config(
                    text=f"Đang xử lý: {current}/{total} dòng | Thành công: {success} | Lỗi: {errors}"
                )
                progress_window.update()

            def cancel_processing():
                """Xử lý hủy bỏ"""
                self._cancellation_requested = True
                progress_window.destroy()

            # Gọi controller xử lý với chunk
            results, output_file, success_count, error_count = self.controller.process_excel_batch_chunked(
                self.view.imported_file_path,
                self.view.dropdown1_var.get(),
                self.view.dropdown2_var.get() if self.view.pheptoan_var.get() not in ["Diện tích", "Thể tích"] else None,
                self.view.pheptoan_var.get(),
                self.view.kich_thuoc_A_var.get(),
                self.view.kich_thuoc_B_var.get(),
                chunksize=500,  # Có thể điều chỉnh
                progress_callback=update_progress
            )

            progress_window.destroy()

            # Hiển thị kết quả
            if self._cancellation_requested:
                self.view.update_final_result_display("Đã hủy xử lý giữa chừng")
                messagebox.showinfo("Thông báo", "Đã hủy xử lý file Excel")
            else:
                result_text = f"Hoàn thành: {success_count} dòng thành công, {error_count} dòng lỗi"
                self.view.update_final_result_display(result_text)

                if error_count == 0:
                    messagebox.showinfo("Thành công",
                                        f"Đã xử lý thành công {success_count} dòng!\nFile: {os.path.basename(output_file)}")
                else:
                    messagebox.showwarning("Hoàn thành với lỗi",
                                           f"Đã xử lý {success_count} dòng thành công, {error_count} dòng lỗi!\nFile: {os.path.basename(output_file)}")

        except Exception as e:
            error_msg = f"❌ Lỗi xử lý file Excel: {str(e)}"
            self.view.update_final_result_display(error_msg)
            messagebox.showerror("Lỗi xử lý", f"Không thể xử lý file Excel:\n{str(e)}")

    def _create_progress_window(self):
        """Tạo cửa sổ hiển thị tiến độ"""
        progress_window = tk.Toplevel(self.view.window)
        progress_window.title("Đang xử lý...")
        progress_window.geometry("400x150")
        progress_window.transient(self.view.window)
        progress_window.grab_set()

        # Progress bar
        tk.Label(progress_window, text="Đang xử lý file Excel...", font=("Arial", 12)).pack(pady=10)

        progress_window.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_window.progress_var, maximum=100)
        progress_bar.pack(fill=tk.X, padx=20, pady=5)

        # Status label
        progress_window.status_label = tk.Label(progress_window, text="Đang khởi tạo...")
        progress_window.status_label.pack(pady=5)

        # Cancel button
        tk.Button(progress_window, text="Hủy", command=lambda: self._cancel_processing(progress_window),
                  bg="#F44336", fg="white").pack(pady=10)

        return progress_window

    def _cancel_processing(self, progress_window):
        """Xử lý sự kiện hủy"""
        self._cancellation_requested = True
        progress_window.destroy()