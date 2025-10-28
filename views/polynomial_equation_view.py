import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from controllers.polynomial_controller import PolynomialController



class PolynomialEquationView:
    def __init__(self, window):
        self.window = window
        self.window.title("Polynomial Equation Mode - Giải Phương Trình Bậc 2, 3, 4")
        self.window.geometry("900x1300")
        self.window.configure(bg="#F0F8FF")
        # Make window resizable
        self.window.resizable(True, True)
        self.window.minsize(800, 600)

        # Configure grid weights for responsive behavior
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # Biến giao diện
        self.bac_phuong_trinh_var = tk.StringVar(value="2")
        self.phien_ban_var = tk.StringVar(value="fx799")

        # Biến lưu trữ các ô nhập liệu và kết quả
        self.coefficient_entries = []
        self.root_entries = []

        # Trạng thái
        self.is_imported_mode = False
        self.has_manual_data = False

        # Load danh sách phiên bản
        self.phien_ban_list = self._load_phien_ban_from_json()

        self._setup_ui()
        self._update_input_fields()
        self._update_button_visibility()

    def _load_phien_ban_from_json(self, file_path: str = "config/versions.json") -> list:
        """Load danh sách phiên bản từ JSON"""
        try:
            if not os.path.exists(file_path):
                return ["fx799", "fx880"]

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("versions", ["fx799", "fx991", "fx570", "fx580", "fx115"])
        except Exception as e:
            print(f"Lỗi khi đọc file versions.json: {e}")
            return ["fx799", "fx991", "fx570", "fx580", "fx115"]

    def _setup_ui(self):
        """Setup giao diện chính"""
        # Container chính với scrollbar
        main_container = tk.Frame(self.window, bg="#F0F8FF")
        main_container.pack(fill="both", expand=True, padx=15, pady=10)

        # === HEADER ===
        self._create_header(main_container)

        # === CONTROL PANEL ===
        self._create_control_panel(main_container)

        # === HƯỚNG DẪN ===
        self._create_guide_section(main_container)

        # === NHẬP HỆ SỐ ===
        self._create_input_section(main_container)

        # === KẾT QUẢ NGHIỆM ===
        self._create_roots_section(main_container)

        # === KẾT QUẢ TỔNG ===
        self._create_final_result_section(main_container)

        # === CONTROL BUTTONS ===
        self._create_control_buttons(main_container)

        # === STATUS BAR ===
        self._create_status_bar(main_container)

    def _create_header(self, parent):
        """Tạo header với title và icon"""
        header_frame = tk.Frame(parent, bg="#1E3A8A", height=80)
        header_frame.pack(fill="x", pady=(0, 15))
        header_frame.pack_propagate(False)

        # Icon và Title
        title_frame = tk.Frame(header_frame, bg="#1E3A8A")
        title_frame.pack(expand=True, fill="both")

        icon_label = tk.Label(
            title_frame,
            text="📊",
            font=("Arial", 24),
            bg="#1E3A8A",
            fg="white"
        )
        icon_label.pack(side="left", padx=(20, 10), pady=20)

        title_label = tk.Label(
            title_frame,
            text="POLYNOMIAL EQUATION MODE",
            font=("Arial", 18, "bold"),
            bg="#1E3A8A",
            fg="white"
        )
        title_label.pack(side="left", pady=20)

        subtitle_label = tk.Label(
            title_frame,
            text="Giải phương trình bậc 2, 3, 4 với mã hóa cho máy tính",
            font=("Arial", 11),
            bg="#1E3A8A",
            fg="#B3D9FF"
        )
        subtitle_label.pack(side="right", padx=(0, 20), pady=(25, 15))

    def _create_control_panel(self, parent):
        """Tạo panel điều khiển chính"""
        control_frame = tk.LabelFrame(
            parent,
            text="⚙️ THIẾT LẬP PHƯƠNG TRÌNH",
            font=("Arial", 12, "bold"),
            bg="#FFFFFF",
            fg="#1E3A8A",
            bd=2,
            relief="groove"
        )
        control_frame.pack(fill="x", pady=10)

        # Dòng 1: Chọn bậc phương trình
        row1 = tk.Frame(control_frame, bg="#FFFFFF")
        row1.pack(fill="x", padx=20, pady=15)

        tk.Label(
            row1,
            text="Bậc phương trình:",
            font=("Arial", 11, "bold"),
            bg="#FFFFFF",
            fg="#333333",
            width=15
        ).pack(side="left")

        bac_menu = ttk.Combobox(
            row1,
            textvariable=self.bac_phuong_trinh_var,
            values=["2", "3", "4"],
            state="readonly",
            width=20,
            font=("Arial", 11)
        )
        bac_menu.pack(side="left", padx=10)
        bac_menu.bind("<<ComboboxSelected>>", self._on_bac_changed)

        # Thông tin về dạng phương trình
        self.equation_form_label = tk.Label(
            row1,
            text="ax² + bx + c = 0",
            font=("Arial", 11, "italic"),
            bg="#FFFFFF",
            fg="#666666"
        )
        self.equation_form_label.pack(side="left", padx=20)

        # Dòng 2: Chọn phiên bản máy tính
        row2 = tk.Frame(control_frame, bg="#FFFFFF")
        row2.pack(fill="x", padx=20, pady=(0, 15))

        tk.Label(
            row2,
            text="Phiên bản máy:",
            font=("Arial", 11, "bold"),
            bg="#FFFFFF",
            fg="#333333",
            width=15
        ).pack(side="left")

        phien_ban_menu = ttk.Combobox(
            row2,
            textvariable=self.phien_ban_var,
            values=self.phien_ban_list,
            state="readonly",
            width=20,
            font=("Arial", 11)
        )
        phien_ban_menu.pack(side="left", padx=10)
        phien_ban_menu.bind("<<ComboboxSelected>>", self._on_phien_ban_changed)

    def _create_guide_section(self, parent):
        """Tạo section hướng dẫn"""
        guide_frame = tk.LabelFrame(
            parent,
            text="💡 HƯỚNG DẪN NHẬP LIỆU",
            font=("Arial", 10, "bold"),
            bg="#E8F4FD",
            fg="#1565C0",
            bd=1
        )
        guide_frame.pack(fill="x", pady=5)

        guide_text = (
            "• Nhập hệ số theo thứ tự từ cao đến thấp (a, b, c cho bậc 2)\n"
            "• Hỗ trợ biểu thức: sqrt(5), sin(pi/2), 1/2, 2^3, log(10)\n"
            "• Ô trống sẽ tự động điền số 0\n"
            "• Phương trình dạng: ax^n + bx^(n-1) + ... + k = 0"
        )

        guide_label = tk.Label(
            guide_frame,
            text=guide_text,
            font=("Arial", 9),
            bg="#E8F4FD",
            fg="#333333",
            justify="left"
        )
        guide_label.pack(padx=15, pady=10)

    def _create_input_section(self, parent):
        """Tạo section nhập hệ số"""
        self.input_frame = tk.LabelFrame(
            parent,
            text="📝 NHẬP HỆ SỐ PHƯƠNG TRÌNH",
            font=("Arial", 12, "bold"),
            bg="#FFFFFF",
            fg="#1E3A8A",
            bd=2,
            relief="groove"
        )
        self.input_frame.pack(fill="x", pady=10)

    def _create_roots_section(self, parent):
        """Tạo section kết quả nghiệm"""
        self.roots_frame = tk.LabelFrame(
            parent,
            text="🎯 NGHIỆM PHƯƠNG TRÌNH",
            font=("Arial", 12, "bold"),
            bg="#FFFFFF",
            fg="#D35400",
            bd=2,
            relief="groove"
        )
        self.roots_frame.pack(fill="x", pady=10)

        self.roots_text = tk.Text(
            self.roots_frame,
            width=80,
            height=10,
            font=("Courier New", 10),
            wrap=tk.WORD,
            bg="#FFF9E6",
            fg="#D35400"
        )
        self.roots_text.pack(padx=15, pady=12, fill="x")
        self.roots_text.insert("1.0", "Chưa có nghiệm được tính")

        # Scrollbar cho roots text
        scrollbar_roots = tk.Scrollbar(self.roots_frame, orient="vertical", command=self.roots_text.yview)
        scrollbar_roots.pack(side="right", fill="y")
        self.roots_text.config(yscrollcommand=scrollbar_roots.set)

    def _create_final_result_section(self, parent):
        """Tạo section kết quả tổng"""
        self.final_frame = tk.LabelFrame(
            parent,
            text="📦 KẾT QUẢ TỔNG (CHO MÁY TÍNH)",
            font=("Arial", 12, "bold"),
            bg="#FFFFFF",
            fg="#2E7D32",
            bd=2,
            relief="groove"
        )
        self.final_frame.pack(fill="x", pady=10)

        self.final_result_text = tk.Text(
            self.final_frame,
            width=80,
            height=3,
            font=("Courier New", 9),
            wrap=tk.WORD,
            bg="#F1F8E9",
            fg="#2E7D32"
        )
        self.final_result_text.pack(padx=15, pady=12, fill="x")
        self.final_result_text.insert("1.0", "Chưa có kết quả tổng")

    def _create_control_buttons(self, parent):
        """Tạo các nút điều khiển"""
        button_frame = tk.Frame(parent, bg="#F0F8FF")
        button_frame.pack(fill="x", pady=20)

        # Nút Import Excel
        self.btn_import = tk.Button(
            button_frame,
            text="📁 Import Excel",
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            height=2,
            command=self._import_excel_placeholder
        )
        self.btn_import.pack(side="left", padx=10)

        # Nút Xử lý
        self.btn_process = tk.Button(
            button_frame,
            text="🔄 Giải & Mã hóa",
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            height=2,
            command=self._process_placeholder  # đã dùng method xử lý thực
        )
        self.btn_process.pack(side="left", padx=10)

        # Nút Export
        self.btn_export = tk.Button(
            button_frame,
            text="💾 Export Excel",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            width=15,
            height=2,
            command=self._export_excel_placeholder
        )
        self.btn_export.pack(side="left", padx=10)

        # Nút Reset
        self.btn_reset = tk.Button(
            button_frame,
            text="🔄 Reset",
            bg="#607D8B",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
            height=2,
            command=self._reset_all
        )
        self.btn_reset.pack(side="left", padx=10)

        # Nút Đóng
        self.btn_close = tk.Button(
            button_frame,
            text="❌ Đóng",
            bg="#F44336",
            fg="white",
            font=("Arial", 10, "bold"),
            width=12,
            height=2,
            command=self.window.destroy
        )
        self.btn_close.pack(side="right", padx=10)

    def _create_status_bar(self, parent):
        """Tạo thanh trạng thái"""
        self.status_label = tk.Label(
            parent,
            text="🟢 Sẵn sàng nhập liệu phương trình bậc 2",
            font=("Arial", 10, "bold"),
            bg="#F0F8FF",
            fg="#2E7D32",
            relief="sunken",
            bd=1
        )
        self.status_label.pack(fill="x", pady=(10, 0))

        # Footer
        footer_label = tk.Label(
            parent,
            text="Polynomial Equation Mode • Hỗ trợ giải phương trình bậc cao • Mã hóa tự động",
            font=("Arial", 8),
            bg="#F0F8FF",
            fg="#666666"
        )
        footer_label.pack(pady=5)

    def _on_bac_changed(self, event=None):
        """Xử lý khi thay đổi bậc phương trình"""
        bac = int(self.bac_phuong_trinh_var.get())

        # Cập nhật dạng phương trình
        forms = {
            2: "ax² + bx + c = 0",
            3: "ax³ + bx² + cx + d = 0",
            4: "ax⁴ + bx³ + cx² + dx + e = 0"
        }
        self.equation_form_label.config(text=forms[bac])

        # Cập nhật input fields
        self._update_input_fields()

        # Cập nhật status
        self.status_label.config(text=f"🟢 Đã chọn phương trình bậc {bac}")

    def _on_phien_ban_changed(self, event=None):
        """Xử lý khi thay đổi phiên bản"""
        phien_ban = self.phien_ban_var.get()
        self.status_label.config(text=f"🟢 Đã chọn phiên bản: {phien_ban}")

    def _update_input_fields(self):
        """Cập nhật các ô nhập liệu theo bậc phương trình"""
        try:
            bac = int(self.bac_phuong_trinh_var.get())

            # Xóa widgets cũ
            for widget in self.input_frame.winfo_children():
                widget.destroy()

            self.coefficient_entries = []

            # Tạo input fields mới
            self._create_coefficient_inputs(bac)

        except Exception as e:
            print(f"Lỗi khi cập nhật input fields: {e}")

    def _create_coefficient_inputs(self, bac):
        """Tạo các ô nhập hệ số"""
        # Header
        tk.Label(
            self.input_frame,
            text=f"Nhập {bac + 1} hệ số cho phương trình bậc {bac}:",
            font=("Arial", 10, "bold"),
            bg="#FFFFFF",
            fg="#333333"
        ).pack(anchor="w", padx=20, pady=10)

        # Container cho inputs
        input_container = tk.Frame(self.input_frame, bg="#FFFFFF")
        input_container.pack(fill="x", padx=20, pady=10)

        # Labels và entries theo bậc
        labels = self._get_coefficient_labels(bac)

        for i, (label, var_name) in enumerate(labels):
            row_frame = tk.Frame(input_container, bg="#FFFFFF")
            row_frame.pack(fill="x", pady=5)

            # Label hệ số
            coef_label = tk.Label(
                row_frame,
                text=label,
                font=("Arial", 10, "bold"),
                bg="#FFFFFF",
                fg="#1E3A8A",
                width=20,
                anchor="w"
            )
            coef_label.pack(side="left")

            # Entry
            entry = tk.Entry(
                row_frame,
                width=30,
                font=("Arial", 10),
                relief="groove",
                bd=2
            )
            entry.pack(side="left", padx=10)
            entry.bind('<KeyRelease>', self._on_manual_input)

            # Placeholder text
            placeholder = tk.Label(
                row_frame,
                text=f"(hệ số {var_name})",
                font=("Arial", 9, "italic"),
                bg="#FFFFFF",
                fg="#666666"
            )
            placeholder.pack(side="left", padx=10)

            self.coefficient_entries.append(entry)

    def _get_coefficient_labels(self, bac):
        """Lấy labels cho hệ số theo bậc"""
        labels_config = {
            2: [("Hệ số a (x²):", "a"), ("Hệ số b (x):", "b"), ("Hệ số c (hằng số):", "c")],
            3: [("Hệ số a (x³):", "a"), ("Hệ số b (x²):", "b"), ("Hệ số c (x):", "c"), ("Hệ số d (hằng số):", "d")],
            4: [("Hệ số a (x⁴):", "a"), ("Hệ số b (x³):", "b"), ("Hệ số c (x²):", "c"), ("Hệ số d (x):", "d"),
                ("Hệ số e (hằng số):", "e")]
        }
        return labels_config.get(bac, labels_config[2])

    def _update_button_visibility(self):
        """Cập nhật hiển thị nút"""
        # Implement logic hiển thị nút theo trạng thái
        pass

    def _on_manual_input(self, event=None):
        """Xử lý khi nhập liệu thủ công"""
        self.has_manual_data = True
        self.is_imported_mode = False
        self.status_label.config(text="✏️ Đang nhập liệu thủ công...")

    # Placeholder methods cho các chức năng
    def _import_excel_placeholder(self):
        """Placeholder cho import Excel"""
        messagebox.showinfo("Chức năng", "Import Excel - Chưa được triển khai")

    def _process_placeholder(self):
        """Thay thế placeholder: thực hiện xử lý phương trình"""
        try:
            degree = int(self.bac_phuong_trinh_var.get())
            version = self.phien_ban_var.get()
            coeffs = [entry.get() for entry in self.coefficient_entries]

            controller = PolynomialController()
            result = controller.process_equation(degree, coeffs, version)

            if not result.get('success', False):
                error = result.get('error', 'Có lỗi không xác định')
                self.status_label.config(text=f"🔴 Lỗi: {error}", fg="#C62828")

                self.roots_text.delete("1.0", tk.END)
                self.roots_text.insert("1.0", f"Lỗi: {error}")
                self.final_result_text.delete("1.0", tk.END)
                self.final_result_text.insert("1.0", "Chưa có kết quả tổng")
                return

            # Lấy thông tin từ kết quả
            equation_display = result.get('equation_display', '')
            summary = result.get('summary', '')
            roots_display = result.get('roots_display', [])
            analysis = result.get('analysis', {})

            # ===== CẬP NHẬT Ô NGHIỆM - CHUYỂN TẤT CẢ LÊN ĐÂY =====
            roots_lines = []

            # 1. Phương trình
            if equation_display:
                roots_lines.append(f"Phương trình: {equation_display}")
                roots_lines.append("")

            # 2. Nghiệm cụ thể
            if roots_display:
                roots_lines.append("Nghiệm:")
                for root in roots_display:
                    roots_lines.append(f"  {root}")
                roots_lines.append("")

            # 3. Phân tích
            if analysis and 'type' in analysis:
                roots_lines.append(f"Phân loại: {analysis['type']}")

                # Thêm chi tiết cho bậc 2
                if 'discriminant_value' in analysis:
                    roots_lines.append(f"Discriminant (Δ): {analysis['discriminant_value']:.6f}")

            # 4. Tóm tắt
            if summary:
                roots_lines.append("")
                roots_lines.append(summary)

            # Cập nhật ô nghiệm với TẤT CẢ thông tin
            self.roots_text.delete("1.0", tk.END)
            self.roots_text.insert("1.0", "\n".join(roots_lines))

            # ===== Ô KẾT QUẢ TỔNG - CHỈ DỰ TRỮ CHO MÃ HÓA =====
            final_lines = [
                "=== DÀNH CHO MÃ HÓA MÁY TÍNH ===",
                "",
                f"Phiên bản: {version}",
                "",
                "Mã lệnh sẽ được tạo ở Phase 3...",
                "",
                "(Khu vực này để trống cho Calculator Encoding)"
            ]

            self.final_result_text.delete("1.0", tk.END)
            self.final_result_text.insert("1.0", "\n".join(final_lines))

            self.status_label.config(text="🟢 Giải phương trình thành công!", fg="#2E7D32")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
            self.status_label.config(text=f"🔴 Lỗi: {str(e)}", fg="#C62828")

    def _export_excel_placeholder(self):
        """Placeholder cho export Excel"""
        messagebox.showinfo("Chức năng", "Export Excel - Chưa được triển khai")

    def _reset_all(self):
        """Reset tất cả dữ liệu"""
        # Clear all entries
        for entry in self.coefficient_entries:
            entry.delete(0, tk.END)

        # Clear text areas
        self.roots_text.delete("1.0", tk.END)
        self.roots_text.insert("1.0", "Chưa có nghiệm được tính")

        self.final_result_text.delete("1.0", tk.END)
        self.final_result_text.insert("1.0", "Chưa có kết quả tổng")

        # Reset status
        bac = self.bac_phuong_trinh_var.get()
        self.status_label.config(text=f"🔄 Đã reset - Sẵn sàng nhập phương trình bậc {bac}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PolynomialEquationView(root)
    root.mainloop()