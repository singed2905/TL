import tkinter as tk
from tkinter import messagebox
import json
import os
from controllers.geometry_controller import GeometryController
from .geometry_actions import GeometryActions
import gc
import psutil


class GeometryView:
    def __init__(self, window):
        self.window = window
        self.controller = GeometryController()
        self.actions = GeometryActions(self, self.controller)

        # Khởi tạo cửa sổ
        self.window.title("Geometry Mode")
        self.window.geometry("700x700")
        self.window.configure(bg="#F8F9FA")

        # Biến và trạng thái
        self._initialize_variables()
        self._initialize_data_storage()

        # Tạo giao diện
        self._create_smart_header()
        self._setup_ui()
        self._setup_bindings()

        # Khởi động
        self._update_operation_menu()
        self.start_header_updates()
        self._hide_all_input_frames()
        self._hide_action_buttons()

    def _initialize_variables(self):
        """Khởi tạo tất cả biến"""
        self.dropdown1_var = tk.StringVar(value="")
        self.dropdown2_var = tk.StringVar(value="")
        self.kich_thuoc_A_var = tk.StringVar(value="3")
        self.kich_thuoc_B_var = tk.StringVar(value="3")
        self.pheptoan_var = tk.StringVar(value="")

        # Load phiên bản
        self.phien_ban_list = self._load_phien_ban_from_json()
        self.phien_ban_var = tk.StringVar(value=self.phien_ban_list[0] if self.phien_ban_list else "Phiên bản 1.0")

        # Trạng thái
        self.imported_data = False
        self.manual_data_entered = False
        self.imported_file_path = ""

    def _initialize_data_storage(self):
        """Khởi tạo storage cho kết quả"""
        self.ket_qua_A1 = [];
        self.ket_qua_X1 = [];
        self.ket_qua_N1 = []
        self.ket_qua_A2 = [];
        self.ket_qua_X2 = [];
        self.ket_qua_N2 = []
        self.ket_qua_diem_A = [];
        self.ket_qua_diem_B = []
        self.ket_qua_duong_tron_A = [];
        self.ket_qua_mat_cau_A = []
        self.ket_qua_duong_tron_B = [];
        self.ket_qua_mat_cau_B = []

    def _load_phien_ban_from_json(self, file_path: str = "config/versions.json") -> list:
        """Load danh sách phiên bản từ JSON"""
        try:
            if not os.path.exists(file_path):
                default_versions = {
                    "versions": [
                        "Phiên bản 1.0", "Phiên bản 2.0", "Phiên bản 3.0",
                        "Phiên bản đặc biệt", "Phiên bản nâng cao"
                    ]
                }
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(default_versions, f, ensure_ascii=False, indent=2)
                return default_versions["versions"]

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("versions", ["Phiên bản 1.0"])

        except Exception as e:
            print(f"Lỗi khi đọc file versions.json: {e}")
            return ["Phiên bản 1.0", "Phiên bản 2.0", "Phiên bản 3.0"]

    def _create_smart_header(self):
        """Tạo header thông minh"""
        HEADER_COLORS = {
            "primary": "#2E86AB", "secondary": "#1B5299", "text": "#FFFFFF",
            "accent": "#F18F01", "success": "#4CAF50", "warning": "#FF9800"
        }

        # Main header frame
        self.header_frame = tk.Frame(self.window, bg=HEADER_COLORS["primary"], height=80)
        self.header_frame.pack(fill="x", padx=10, pady=5)
        self.header_frame.pack_propagate(False)

        header_content = tk.Frame(self.header_frame, bg=HEADER_COLORS["primary"])
        header_content.pack(fill="both", expand=True, padx=15, pady=10)

        # === PHẦN TRÁI: Logo và Operation ===
        left_section = tk.Frame(header_content, bg=HEADER_COLORS["primary"])
        left_section.pack(side="left", fill="y")

        # Logo
        logo_frame = tk.Frame(left_section, bg=HEADER_COLORS["primary"])
        logo_frame.pack(side="top", fill="x")
        tk.Label(logo_frame, text="🧮", font=("Arial", 20),
                 bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left")
        tk.Label(logo_frame, text="Geometry Mode", font=("Arial", 16, "bold"),
                 bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left", padx=(5, 20))

        # Operation selector
        operation_frame = tk.Frame(left_section, bg=HEADER_COLORS["primary"])
        operation_frame.pack(side="top", fill="x", pady=(5, 0))
        tk.Label(operation_frame, text="Phép toán:", font=("Arial", 10),
                 bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left")

        self.operation_menu = tk.OptionMenu(operation_frame, self.pheptoan_var, "")
        self.operation_menu.config(
            bg=HEADER_COLORS["secondary"], fg=HEADER_COLORS["text"],
            font=("Arial", 10, "bold"), width=15, relief="flat", borderwidth=0
        )
        self.operation_menu.pack(side="left", padx=(5, 0))

        # === PHẦN GIỮA: Version và Stats ===
        center_section = tk.Frame(header_content, bg=HEADER_COLORS["primary"])
        center_section.pack(side="left", fill="both", expand=True, padx=20)

        # Version selector
        version_frame = tk.Frame(center_section, bg=HEADER_COLORS["primary"])
        version_frame.pack(side="top", fill="x")
        tk.Label(version_frame, text="Phiên bản:", font=("Arial", 9),
                 bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]).pack(side="left")

        self.version_menu = tk.OptionMenu(version_frame, self.phien_ban_var, *self.phien_ban_list)
        self.version_menu.config(
            bg=HEADER_COLORS["accent"], fg="white", font=("Arial", 9),
            width=15, relief="flat", borderwidth=0
        )
        self.version_menu.pack(side="left", padx=(5, 0))

        # Quick stats
        self.stats_frame = tk.Frame(center_section, bg=HEADER_COLORS["primary"])
        self.stats_frame.pack(side="top", fill="x", pady=(5, 0))
        self.quick_stats_label = tk.Label(
            self.stats_frame, text="🔧 Sẵn sàng", font=("Arial", 9),
            bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]
        )
        self.quick_stats_label.pack(side="left")

        # === PHẦN PHẢI: System Info ===
        right_section = tk.Frame(header_content, bg=HEADER_COLORS["primary"])
        right_section.pack(side="right", fill="y")

        # System info
        sys_info_frame = tk.Frame(right_section, bg=HEADER_COLORS["primary"])
        sys_info_frame.pack(side="top", fill="x")
        self.memory_label = tk.Label(
            sys_info_frame, text="", font=("Arial", 8),
            bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["text"]
        )
        self.memory_label.pack(side="top", anchor="e")
        self.status_label = tk.Label(
            sys_info_frame, text="✅ Hệ thống ổn định", font=("Arial", 8),
            bg=HEADER_COLORS["primary"], fg=HEADER_COLORS["success"]
        )
        self.status_label.pack(side="top", anchor="e")

        # Quick action buttons
        action_frame = tk.Frame(right_section, bg=HEADER_COLORS["primary"])
        action_frame.pack(side="top", fill="x", pady=(5, 0))
        self.btn_quick_help = tk.Button(
            action_frame, text="❓", font=("Arial", 10),
            bg=HEADER_COLORS["secondary"], fg="white", relief="flat", width=3,
            command=self._show_quick_help
        )
        self.btn_quick_help.pack(side="right", padx=(2, 0))

    def _update_operation_menu(self):
        """Cập nhật operation menu"""
        operations_with_icons = {
            "Tương giao": "", "Khoảng cách": "", "Diện tích": "",
            "Thể tích": "", "PT đường thẳng": ""
        }

        menu = self.operation_menu["menu"]
        menu.delete(0, "end")
        for operation, icon in operations_with_icons.items():
            menu.add_command(
                label=f"{operation}",
                command=lambda op=operation: self._on_operation_selected(op)
            )

        if not self.pheptoan_var.get() and operations_with_icons:
            self.pheptoan_var.set(list(operations_with_icons.keys())[0])

    def _on_operation_selected(self, operation):
        """Xử lý khi chọn operation"""
        self.pheptoan_var.set(operation)
        self._update_operation_display()

    def _update_operation_display(self):
        """Cập nhật hiển thị operation"""
        operation = self.pheptoan_var.get()
        if operation:
            self._update_quick_stats()
            self._on_operation_selected_callback()

    def _on_operation_selected_callback(self, *args):
        """Callback khi operation được chọn"""
        operation = self.pheptoan_var.get()
        if operation:
            if hasattr(self, 'label_A') and hasattr(self, 'dropdown1_menu'):
                self.label_A.grid()
                self.dropdown1_menu.grid()

                if operation not in ["Diện tích", "Thể tích"]:
                    self.label_B.grid()
                    self.dropdown2_menu.grid()
                else:
                    self.label_B.grid_remove()
                    self.dropdown2_menu.grid_remove()

                self._update_dropdown_options()
                if hasattr(self, 'btn_import_excel'):
                    self.btn_import_excel.grid()

    def _update_quick_stats(self):
        """Cập nhật thông tin thống kê nhanh"""
        try:
            if self.imported_data and self.imported_file_path:
                file_name = os.path.basename(self.imported_file_path)
                file_size = os.path.getsize(self.imported_file_path) / 1024
                stats_text = f"📁 {file_name} ({file_size:.1f}KB)"
                self.quick_stats_label.config(text=stats_text)
            elif self.manual_data_entered:
                shape_a = self.dropdown1_var.get()
                shape_b = self.dropdown2_var.get() if self.dropdown2_var.get() else "Không có"
                stats_text = f"✍️ {shape_a} + {shape_b}"
                self.quick_stats_label.config(text=stats_text)
            else:
                operation = self.pheptoan_var.get()
                if operation:
                    self.quick_stats_label.config(text=f"🔧 Đã chọn: {operation}")
                else:
                    self.quick_stats_label.config(text="🔧 Chọn phép toán để bắt đầu")
        except Exception as e:
            self.quick_stats_label.config(text="⚠️ Lỗi thống kê")

    def _update_system_info(self):
        """Cập nhật thông tin hệ thống"""
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024

            memory_color = "#4CAF50"
            if memory_mb > 500: memory_color = "#FF9800"
            if memory_mb > 800: memory_color = "#F44336"

            self.memory_label.config(text=f"💾 {memory_mb:.1f}MB", fg=memory_color)

            if memory_mb > 800:
                self.status_label.config(text="⚠️ Memory cao", fg="#FF9800")
            else:
                self.status_label.config(text="✅ Ổn định", fg="#4CAF50")
        except ImportError:
            self.memory_label.config(text="💾 N/A")
            self.status_label.config(text="ℹ️ Thiếu psutil")

    def _show_quick_help(self):
        """Hiển thị hướng dẫn nhanh"""
        help_text = """
🎯 HƯỚNG DẪN NHANH

1. Chọn PHÉP TOÁN từ dropdown
2. Chọn hình dạng cho NHÓM A (và NHÓM B nếu cần)
3. Nhập dữ liệu thủ công hoặc IMPORT EXCEL
4. Nhấn THỰC THI để mã hóa kết quả
5. Xuất file Excel nếu cần

📖 Chi tiết: Xem documentation đầy đủ
        """
        messagebox.showinfo("Hướng Dẫn Nhanh", help_text.strip())

    def start_header_updates(self):
        """Bắt đầu cập nhật tự động cho header"""
        self._update_system_info()
        self._update_quick_stats()
        self.window.after(5000, self.start_header_updates)

    def _setup_ui(self):
        """Setup giao diện chính"""
        self.main_container = tk.Frame(self.window, bg="#F8F9FA")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Top frame với dropdown
        top_frame = tk.Frame(self.main_container, bg="#F8F9FA")
        top_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        self._setup_dropdowns(top_frame)
        self._setup_group_a_frames()
        self._setup_group_b_frames()
        self._setup_control_frame()

    def _setup_dropdowns(self, parent):
        """Setup dropdown chọn nhóm"""
        shapes = self.controller.get_available_shapes()

        self.label_A = tk.Label(parent, text="Chọn nhóm A:", bg="#F8F9FA", font=("Arial", 10))
        self.label_A.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.label_A.grid_remove()

        self.dropdown1_menu = tk.OptionMenu(parent, self.dropdown1_var, *shapes)
        self.dropdown1_menu.config(width=15, font=("Arial", 9))
        self.dropdown1_menu.grid(row=0, column=1, padx=5, pady=5)
        self.dropdown1_menu.grid_remove()

        self.label_B = tk.Label(parent, text="Chọn nhóm B:", bg="#F8F9FA", font=("Arial", 10))
        self.label_B.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.label_B.grid_remove()

        self.dropdown2_menu = tk.OptionMenu(parent, self.dropdown2_var, *shapes)
        self.dropdown2_menu.config(width=15, font=("Arial", 9))
        self.dropdown2_menu.grid(row=0, column=3, padx=5, pady=5)
        self.dropdown2_menu.grid_remove()

    def _setup_group_a_frames(self):
        """Setup frames cho nhóm A"""
        # Frame Điểm A
        self.frame_A_diem = tk.LabelFrame(
            self.main_container, text="🎯 NHÓM A - Điểm",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        self.frame_A_diem.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_A_diem, text="Kích thước:", bg="#FFFFFF").grid(row=0, column=0)
        tk.OptionMenu(self.frame_A_diem, self.kich_thuoc_A_var, "2", "3").grid(row=0, column=1)

        tk.Label(self.frame_A_diem, text="Nhập toạ độ:", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_dau_vao_diem_A = tk.Entry(self.frame_A_diem, width=40)
        self.entry_dau_vao_diem_A.grid(row=1, column=1)

        self.entry_Xd_A = tk.Entry(self.frame_A_diem, width=10)
        self.entry_Yd_A = tk.Entry(self.frame_A_diem, width=10)
        self.entry_Zd_A = tk.Entry(self.frame_A_diem, width=10)
        self.entry_Xd_A.grid(row=2, column=0)
        self.entry_Yd_A.grid(row=2, column=1)
        self.entry_Zd_A.grid(row=2, column=2)

        # Frame Đường thẳng A
        self.frame_A_duong = tk.LabelFrame(
            self.main_container, text="📏 NHÓM A - Đường thẳng",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        self.frame_A_duong.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_A_duong, text="Nhập A1,B1,C1:", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_dau_vao_A1 = tk.Entry(self.frame_A_duong, width=40)
        self.entry_dau_vao_A1.grid(row=0, column=1)

        tk.Label(self.frame_A_duong, text="Nhập X1,Y1,Z1:", bg="#FFFFFF").grid(row=2, column=0)
        self.entry_dau_vao_X1 = tk.Entry(self.frame_A_duong, width=40)
        self.entry_dau_vao_X1.grid(row=2, column=1)

        self.entry_A1 = tk.Entry(self.frame_A_duong, width=10)
        self.entry_B1 = tk.Entry(self.frame_A_duong, width=10)
        self.entry_C1 = tk.Entry(self.frame_A_duong, width=10)
        self.entry_X1 = tk.Entry(self.frame_A_duong, width=10)
        self.entry_Y1 = tk.Entry(self.frame_A_duong, width=10)
        self.entry_Z1 = tk.Entry(self.frame_A_duong, width=10)
        self.entry_A1.grid(row=1, column=0);
        self.entry_B1.grid(row=1, column=1);
        self.entry_C1.grid(row=1, column=2)
        self.entry_X1.grid(row=3, column=0);
        self.entry_Y1.grid(row=3, column=1);
        self.entry_Z1.grid(row=3, column=2)

        # Frame Mặt phẳng A
        self.frame_A_mat = tk.LabelFrame(
            self.main_container, text="📐 NHÓM A - Mặt phẳng (4 tham số)",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        self.frame_A_mat.grid(row=3, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        # Input boxes
        tk.Label(self.frame_A_mat, text="Input - Nhập hệ số:", bg="#FFFFFF").grid(row=0, column=0, columnspan=8, pady=5)
        tk.Label(self.frame_A_mat, text="a:", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_N1_in = tk.Entry(self.frame_A_mat, width=10);
        self.entry_N1_in.grid(row=1, column=1)
        tk.Label(self.frame_A_mat, text="b:", bg="#FFFFFF").grid(row=1, column=2)
        self.entry_N2_in = tk.Entry(self.frame_A_mat, width=10);
        self.entry_N2_in.grid(row=1, column=3)
        tk.Label(self.frame_A_mat, text="c:", bg="#FFFFFF").grid(row=1, column=4)
        self.entry_N3_in = tk.Entry(self.frame_A_mat, width=10);
        self.entry_N3_in.grid(row=1, column=5)
        tk.Label(self.frame_A_mat, text="d:", bg="#FFFFFF").grid(row=1, column=6)
        self.entry_N4_in = tk.Entry(self.frame_A_mat, width=10);
        self.entry_N4_in.grid(row=1, column=7)

        # Output boxes
        tk.Label(self.frame_A_mat, text="Output - Kết quả mã hóa:", bg="#FFFFFF").grid(row=2, column=0, columnspan=8,
                                                                                       pady=5)
        tk.Label(self.frame_A_mat, text="a:", bg="#FFFFFF").grid(row=3, column=0)
        self.entry_N1_out = tk.Entry(self.frame_A_mat, width=10);
        self.entry_N1_out.grid(row=3, column=1);
        self.entry_N1_out.config(state='readonly')
        tk.Label(self.frame_A_mat, text="b:", bg="#FFFFFF").grid(row=3, column=2)
        self.entry_N2_out = tk.Entry(self.frame_A_mat, width=10);
        self.entry_N2_out.grid(row=3, column=3);
        self.entry_N2_out.config(state='readonly')
        tk.Label(self.frame_A_mat, text="c:", bg="#FFFFFF").grid(row=3, column=4)
        self.entry_N3_out = tk.Entry(self.frame_A_mat, width=10);
        self.entry_N3_out.grid(row=3, column=5);
        self.entry_N3_out.config(state='readonly')
        tk.Label(self.frame_A_mat, text="d:", bg="#FFFFFF").grid(row=3, column=6)
        self.entry_N4_out = tk.Entry(self.frame_A_mat, width=10);
        self.entry_N4_out.grid(row=3, column=7);
        self.entry_N4_out.config(state='readonly')

        # Frame Đường tròn A
        self.frame_A_duong_tron = tk.LabelFrame(
            self.main_container, text="⭕ NHÓM A - Đường tròn (2 tham số: tâm và bán kính)",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        self.frame_A_duong_tron.grid(row=4, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_A_duong_tron, text="Nhập tâm (x,y):", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_dau_vao_tam_duong_tron_A = tk.Entry(self.frame_A_duong_tron, width=30)
        self.entry_dau_vao_tam_duong_tron_A.grid(row=0, column=1)

        tk.Label(self.frame_A_duong_tron, text="Nhập bán kính r:", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_dau_vao_ban_kinh_duong_tron_A = tk.Entry(self.frame_A_duong_tron, width=30)
        self.entry_dau_vao_ban_kinh_duong_tron_A.grid(row=1, column=1)

        self.entry_duong_tron_A1 = tk.Entry(self.frame_A_duong_tron, width=10)
        self.entry_duong_tron_A2 = tk.Entry(self.frame_A_duong_tron, width=10)
        self.entry_duong_tron_A3 = tk.Entry(self.frame_A_duong_tron, width=10)
        tk.Label(self.frame_A_duong_tron, text="Kết quả:", bg="#FFFFFF").grid(row=2, column=0)
        self.entry_duong_tron_A1.grid(row=2, column=1)
        self.entry_duong_tron_A2.grid(row=2, column=2)
        self.entry_duong_tron_A3.grid(row=2, column=3)

        # Frame Mặt cầu A
        self.frame_A_mat_cau = tk.LabelFrame(
            self.main_container, text="🔴 NHÓM A - Mặt cầu (2 tham số: tâm và bán kính)",
            bg="#FFFFFF", fg="#1B5299", font=("Arial", 10, "bold")
        )
        self.frame_A_mat_cau.grid(row=5, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_A_mat_cau, text="Nhập tâm (x,y,z):", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_dau_vao_tam_mat_cau_A = tk.Entry(self.frame_A_mat_cau, width=30)
        self.entry_dau_vao_tam_mat_cau_A.grid(row=0, column=1)

        tk.Label(self.frame_A_mat_cau, text="Nhập bán kính:", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_dau_vao_ban_kinh_mat_cau_A = tk.Entry(self.frame_A_mat_cau, width=30)
        self.entry_dau_vao_ban_kinh_mat_cau_A.grid(row=1, column=1)

        self.entry_mat_cau_A1 = tk.Entry(self.frame_A_mat_cau, width=10)
        self.entry_mat_cau_A2 = tk.Entry(self.frame_A_mat_cau, width=10)
        self.entry_mat_cau_A3 = tk.Entry(self.frame_A_mat_cau, width=10)
        self.entry_mat_cau_A4 = tk.Entry(self.frame_A_mat_cau, width=10)
        tk.Label(self.frame_A_mat_cau, text="Kết quả:", bg="#FFFFFF").grid(row=2, column=0)
        self.entry_mat_cau_A1.grid(row=2, column=1)
        self.entry_mat_cau_A2.grid(row=2, column=2)
        self.entry_mat_cau_A3.grid(row=2, column=3)
        self.entry_mat_cau_A4.grid(row=2, column=4)

        # Ẩn tất cả frame ban đầu
        for frame in [self.frame_A_diem, self.frame_A_duong, self.frame_A_mat,
                      self.frame_A_duong_tron, self.frame_A_mat_cau]:
            frame.grid_remove()

    def _setup_group_b_frames(self):
        """Setup frames cho nhóm B"""
        # Frame Điểm B
        self.frame_B_diem = tk.LabelFrame(
            self.main_container, text="🎯 NHÓM B - Điểm",
            bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold")
        )
        self.frame_B_diem.grid(row=6, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_B_diem, text="Kích thước:", bg="#FFFFFF").grid(row=0, column=0)
        tk.OptionMenu(self.frame_B_diem, self.kich_thuoc_B_var, "2", "3").grid(row=0, column=1)

        tk.Label(self.frame_B_diem, text="Nhập toạ độ:", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_dau_vao_diem_B = tk.Entry(self.frame_B_diem, width=40)
        self.entry_dau_vao_diem_B.grid(row=1, column=1)

        self.entry_Xd_B = tk.Entry(self.frame_B_diem, width=10)
        self.entry_Yd_B = tk.Entry(self.frame_B_diem, width=10)
        self.entry_Zd_B = tk.Entry(self.frame_B_diem, width=10)
        self.entry_Xd_B.grid(row=2, column=0)
        self.entry_Yd_B.grid(row=2, column=1)
        self.entry_Zd_B.grid(row=2, column=2)

        # Frame Đường thẳng B
        self.frame_B_duong = tk.LabelFrame(
            self.main_container, text="📏 NHÓM B - Đường thẳng",
            bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold")
        )
        self.frame_B_duong.grid(row=7, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_B_duong, text="Nhập A2,B2,C2:", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_dau_vao_A2 = tk.Entry(self.frame_B_duong, width=40)
        self.entry_dau_vao_A2.grid(row=0, column=1)

        tk.Label(self.frame_B_duong, text="Nhập X2,Y2,Z2:", bg="#FFFFFF").grid(row=2, column=0)
        self.entry_dau_vao_X2 = tk.Entry(self.frame_B_duong, width=40)
        self.entry_dau_vao_X2.grid(row=2, column=1)

        self.entry_A2 = tk.Entry(self.frame_B_duong, width=10)
        self.entry_B2 = tk.Entry(self.frame_B_duong, width=10)
        self.entry_C2 = tk.Entry(self.frame_B_duong, width=10)
        self.entry_X2 = tk.Entry(self.frame_B_duong, width=10)
        self.entry_Y2 = tk.Entry(self.frame_B_duong, width=10)
        self.entry_Z2 = tk.Entry(self.frame_B_duong, width=10)
        self.entry_A2.grid(row=1, column=0);
        self.entry_B2.grid(row=1, column=1);
        self.entry_C2.grid(row=1, column=2)
        self.entry_X2.grid(row=3, column=0);
        self.entry_Y2.grid(row=3, column=1);
        self.entry_Z2.grid(row=3, column=2)

        # Frame Mặt phẳng B
        self.frame_B_mat = tk.LabelFrame(
            self.main_container, text="📐 NHÓM B - Mặt phẳng (4 tham số)",
            bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold")
        )
        self.frame_B_mat.grid(row=8, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        # Input boxes
        tk.Label(self.frame_B_mat, text="Input - Nhập hệ số:", bg="#FFFFFF").grid(row=0, column=0, columnspan=8, pady=5)
        tk.Label(self.frame_B_mat, text="a:", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_N5_in = tk.Entry(self.frame_B_mat, width=10);
        self.entry_N5_in.grid(row=1, column=1)
        tk.Label(self.frame_B_mat, text="b:", bg="#FFFFFF").grid(row=1, column=2)
        self.entry_N6_in = tk.Entry(self.frame_B_mat, width=10);
        self.entry_N6_in.grid(row=1, column=3)
        tk.Label(self.frame_B_mat, text="c:", bg="#FFFFFF").grid(row=1, column=4)
        self.entry_N7_in = tk.Entry(self.frame_B_mat, width=10);
        self.entry_N7_in.grid(row=1, column=5)
        tk.Label(self.frame_B_mat, text="d:", bg="#FFFFFF").grid(row=1, column=6)
        self.entry_N8_in = tk.Entry(self.frame_B_mat, width=10);
        self.entry_N8_in.grid(row=1, column=7)

        # Output boxes
        tk.Label(self.frame_B_mat, text="Output - Kết quả mã hóa:", bg="#FFFFFF").grid(row=2, column=0, columnspan=8,
                                                                                       pady=5)
        tk.Label(self.frame_B_mat, text="a:", bg="#FFFFFF").grid(row=3, column=0)
        self.entry_N5_out = tk.Entry(self.frame_B_mat, width=10);
        self.entry_N5_out.grid(row=3, column=1);
        self.entry_N5_out.config(state='readonly')
        tk.Label(self.frame_B_mat, text="b:", bg="#FFFFFF").grid(row=3, column=2)
        self.entry_N6_out = tk.Entry(self.frame_B_mat, width=10);
        self.entry_N6_out.grid(row=3, column=3);
        self.entry_N6_out.config(state='readonly')
        tk.Label(self.frame_B_mat, text="c:", bg="#FFFFFF").grid(row=3, column=4)
        self.entry_N7_out = tk.Entry(self.frame_B_mat, width=10);
        self.entry_N7_out.grid(row=3, column=5);
        self.entry_N7_out.config(state='readonly')
        tk.Label(self.frame_B_mat, text="d:", bg="#FFFFFF").grid(row=3, column=6)
        self.entry_N8_out = tk.Entry(self.frame_B_mat, width=10);
        self.entry_N8_out.grid(row=3, column=7);
        self.entry_N8_out.config(state='readonly')

        # Frame Đường tròn B
        self.frame_B_duong_tron = tk.LabelFrame(
            self.main_container, text="⭕ NHÓM B - Đường tròn (2 tham số: tâm và bán kính)",
            bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold")
        )
        self.frame_B_duong_tron.grid(row=9, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_B_duong_tron, text="Nhập tâm (x,y):", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_dau_vao_tam_duong_tron_B = tk.Entry(self.frame_B_duong_tron, width=30)
        self.entry_dau_vao_tam_duong_tron_B.grid(row=0, column=1)

        tk.Label(self.frame_B_duong_tron, text="Nhập bán kính r:", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_dau_vao_ban_kinh_duong_tron_B = tk.Entry(self.frame_B_duong_tron, width=30)
        self.entry_dau_vao_ban_kinh_duong_tron_B.grid(row=1, column=1)

        self.entry_duong_tron_B1 = tk.Entry(self.frame_B_duong_tron, width=10)
        self.entry_duong_tron_B2 = tk.Entry(self.frame_B_duong_tron, width=10)
        self.entry_duong_tron_B3 = tk.Entry(self.frame_B_duong_tron, width=10)
        tk.Label(self.frame_B_duong_tron, text="Kết quả:", bg="#FFFFFF").grid(row=2, column=0)
        self.entry_duong_tron_B1.grid(row=2, column=1)
        self.entry_duong_tron_B2.grid(row=2, column=2)
        self.entry_duong_tron_B3.grid(row=2, column=3)

        # Frame Mặt cầu B
        self.frame_B_mat_cau = tk.LabelFrame(
            self.main_container, text="🔴 NHÓM B - Mặt cầu (2 tham số: tâm và bán kính)",
            bg="#FFFFFF", fg="#A23B72", font=("Arial", 10, "bold")
        )
        self.frame_B_mat_cau.grid(row=10, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        tk.Label(self.frame_B_mat_cau, text="Nhập tâm (x,y,z):", bg="#FFFFFF").grid(row=0, column=0)
        self.entry_dau_vao_tam_mat_cau_B = tk.Entry(self.frame_B_mat_cau, width=30)
        self.entry_dau_vao_tam_mat_cau_B.grid(row=0, column=1)

        tk.Label(self.frame_B_mat_cau, text="Nhập bán kính:", bg="#FFFFFF").grid(row=1, column=0)
        self.entry_dau_vao_ban_kinh_mat_cau_B = tk.Entry(self.frame_B_mat_cau, width=30)
        self.entry_dau_vao_ban_kinh_mat_cau_B.grid(row=1, column=1)

        self.entry_mat_cau_B1 = tk.Entry(self.frame_B_mat_cau, width=10)
        self.entry_mat_cau_B2 = tk.Entry(self.frame_B_mat_cau, width=10)
        self.entry_mat_cau_B3 = tk.Entry(self.frame_B_mat_cau, width=10)
        self.entry_mat_cau_B4 = tk.Entry(self.frame_B_mat_cau, width=10)
        tk.Label(self.frame_B_mat_cau, text="Kết quả:", bg="#FFFFFF").grid(row=2, column=0)
        self.entry_mat_cau_B1.grid(row=2, column=1)
        self.entry_mat_cau_B2.grid(row=2, column=2)
        self.entry_mat_cau_B3.grid(row=2, column=3)
        self.entry_mat_cau_B4.grid(row=2, column=4)

        # Ẩn tất cả frame ban đầu
        for frame in [self.frame_B_diem, self.frame_B_duong, self.frame_B_mat,
                      self.frame_B_duong_tron, self.frame_B_mat_cau]:
            frame.grid_remove()

    def _setup_control_frame(self):
        """Setup control frame với buttons và result display"""
        self.frame_tong = tk.LabelFrame(
            self.main_container, text="🎉 KẾT QUẢ & ĐIỀU KHIỂN",
            bg="#FFFFFF", font=("Arial", 10, "bold")
        )
        self.frame_tong.grid(row=11, column=0, columnspan=4, padx=10, pady=10, sticky="we")

        # 🎨 THAY THẾ ENTRY BẰNG TEXT ĐỂ XUỐNG DÒNG
        self.entry_tong = tk.Text(
            self.frame_tong,
            width=30,
            height=3,  # Chiều cao 3 dòng
            font=("Arial", 10),
            wrap=tk.WORD,  # Tự động xuống dòng theo từ
            bg="#F8F9FA",
            fg="black",
            relief="solid",
            bd=1,
            padx=5,  # Padding ngang
            pady=5  # Padding dọc
        )
        self.entry_tong.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="we")

        # Tạo thanh cuộn dọc cho Text widget
        scrollbar = tk.Scrollbar(self.frame_tong, orient="vertical", command=self.entry_tong.yview)
        scrollbar.grid(row=0, column=4, sticky="ns", pady=5)
        self.entry_tong.config(yscrollcommand=scrollbar.set)

        # Nút Import Excel - Ẩn ban đầu
        self.btn_import_excel = tk.Button(
            self.frame_tong, text="📁 Import Excel",
            command=self.actions._import_from_excel,
            bg="#FF9800", fg="white", font=("Arial", 9, "bold")
        )
        self.btn_import_excel.grid(row=1, column=0, columnspan=4, pady=5, sticky="we")
        self.btn_import_excel.grid_remove()

        # Frame cho nút thủ công
        self.frame_buttons_manual = tk.Frame(self.frame_tong, bg="#FFFFFF")
        self.frame_buttons_manual.grid(row=2, column=0, columnspan=4, pady=5, sticky="we")

        tk.Button(self.frame_buttons_manual, text="🔄 Xử lý Nhóm A",
                  command=self.actions._thuc_thi_A,
                  bg="#2196F3", fg="white", font=("Arial", 9)).grid(row=0, column=0, padx=5)
        tk.Button(self.frame_buttons_manual, text="🔄 Xử lý Nhóm B",
                  command=self.actions._thuc_thi_B,
                  bg="#2196F3", fg="white", font=("Arial", 9)).grid(row=0, column=1, padx=5)
        tk.Button(self.frame_buttons_manual, text="🚀 Thực thi tất cả",
                  command=self.actions._thuc_thi_tat_ca,
                  bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=5)
        tk.Button(self.frame_buttons_manual, text="💾 Xuất Excel",
                  command=self.actions._export_to_excel,
                  bg="#FF9800", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=3, padx=5)

        self.frame_buttons_manual.grid_remove()

        # Frame cho nút import
        self.frame_buttons_import = tk.Frame(self.frame_tong, bg="#FFFFFF")
        self.frame_buttons_import.grid(row=2, column=0, columnspan=4, pady=5, sticky="we")

        tk.Button(self.frame_buttons_import, text="🚀 Xử lý File Excel",
                  command=self.actions._thuc_thi_import_excel,
                  bg="#4CAF50", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=5)
        tk.Button(self.frame_buttons_import, text="📁 Import File Khác",
                  command=self.actions._import_from_excel,
                  bg="#2196F3", fg="white", font=("Arial", 9)).grid(row=0, column=1, padx=5)
        tk.Button(self.frame_buttons_import, text="↩️ Quay lại",
                  command=self.actions._quit_import_mode,
                  bg="#F44336", fg="white", font=("Arial", 9)).grid(row=0, column=2, padx=5)

        self.frame_buttons_import.grid_remove()

    def _setup_bindings(self):
        """Setup event bindings"""
        self.kich_thuoc_A_var.trace_add("write", self._on_kich_thuoc_changed)
        self.kich_thuoc_B_var.trace_add("write", self._on_kich_thuoc_changed)
        self.dropdown1_var.trace_add("write", self._on_dropdown_change)
        self.dropdown2_var.trace_add("write", self._on_dropdown_change)
        self.pheptoan_var.trace_add("write", self._on_operation_selected_callback)
        self.phien_ban_var.trace_add("write", self._on_version_changed)

    def _on_version_changed(self, *args):
        """Xử lý khi thay đổi phiên bản"""
        selected_version = self.phien_ban_var.get()
        self.controller.set_current_version(selected_version)
        self._update_quick_stats()

    def _hide_all_input_frames(self):
        """Ẩn tất cả input frames ban đầu"""
        frames = [self.frame_A_diem, self.frame_A_duong, self.frame_A_mat,
                  self.frame_A_duong_tron, self.frame_A_mat_cau,
                  self.frame_B_diem, self.frame_B_duong, self.frame_B_mat,
                  self.frame_B_duong_tron, self.frame_B_mat_cau]

        for frame in frames:
            frame.grid_remove()

    def _hide_action_buttons(self):
        """Ẩn action buttons ban đầu"""
        self.frame_buttons_manual.grid_remove()
        self.frame_buttons_import.grid_remove()

    def _on_dropdown_change(self, *args):
        """Khi chọn nhóm A, B, hiện các frame nhập liệu tương ứng"""
        chonA = self.dropdown1_var.get()
        chonB = self.dropdown2_var.get()
        pheptoan = self.pheptoan_var.get()

        if chonA and chonB or (chonA and pheptoan in ["Diện tích", "Thể tích"]):
            self._show_input_frames(chonA, chonB, pheptoan)
            self._bind_input_events()

    def _show_input_frames(self, chonA, chonB, pheptoan):
        """Hiện các frame nhập liệu tương ứng"""
        # Ẩn tất cả frame nhóm A trước
        for frame in [self.frame_A_diem, self.frame_A_duong, self.frame_A_mat,
                      self.frame_A_duong_tron, self.frame_A_mat_cau]:
            frame.grid_remove()

        # Hiện frame nhóm A tương ứng
        if chonA == "Điểm":
            self.frame_A_diem.grid()
            self._update_point_ui()
        elif chonA == "Đường thẳng":
            self.frame_A_duong.grid()
        elif chonA == "Mặt phẳng":
            self.frame_A_mat.grid()
        elif chonA == "Đường tròn":
            self.frame_A_duong_tron.grid()
        elif chonA == "Mặt cầu":
            self.frame_A_mat_cau.grid()

        # Xử lý nhóm B - Ẩn hoàn toàn khi là Diện tích/Thể tích
        if pheptoan in ["Diện tích", "Thể tích"]:
            for frame in [self.frame_B_diem, self.frame_B_duong, self.frame_B_mat,
                          self.frame_B_duong_tron, self.frame_B_mat_cau]:
                frame.grid_remove()
        else:
            # Ẩn tất cả frame nhóm B trước
            for frame in [self.frame_B_diem, self.frame_B_duong, self.frame_B_mat,
                          self.frame_B_duong_tron, self.frame_B_mat_cau]:
                frame.grid_remove()

            # Hiện frame nhóm B tương ứng
            if chonB == "Điểm":
                self.frame_B_diem.grid()
                self._update_point_ui()
            elif chonB == "Đường thẳng":
                self.frame_B_duong.grid()
            elif chonB == "Mặt phẳng":
                self.frame_B_mat.grid()
            elif chonB == "Đường tròn":
                self.frame_B_duong_tron.grid()
            elif chonB == "Mặt cầu":
                self.frame_B_mat_cau.grid()

    def _bind_input_events(self):
        """Gắn sự kiện theo dõi nhập liệu vào tất cả các ô nhập"""
        entries = self._get_all_input_entries()
        for entry in entries:
            entry.bind('<KeyRelease>', self._on_input_data_changed)

    def _get_all_input_entries(self):
        """Lấy tất cả các ô nhập liệu"""
        entries = []

        # Nhóm A
        entries.extend([
            self.entry_dau_vao_diem_A, self.entry_Xd_A, self.entry_Yd_A, self.entry_Zd_A,
            self.entry_dau_vao_A1, self.entry_dau_vao_X1,
            self.entry_A1, self.entry_B1, self.entry_C1, self.entry_X1, self.entry_Y1, self.entry_Z1,
            self.entry_N1_in, self.entry_N2_in, self.entry_N3_in, self.entry_N4_in,
            self.entry_dau_vao_tam_duong_tron_A, self.entry_dau_vao_ban_kinh_duong_tron_A,
            self.entry_duong_tron_A1, self.entry_duong_tron_A2, self.entry_duong_tron_A3,
            self.entry_dau_vao_tam_mat_cau_A, self.entry_dau_vao_ban_kinh_mat_cau_A,
            self.entry_mat_cau_A1, self.entry_mat_cau_A2, self.entry_mat_cau_A3, self.entry_mat_cau_A4
        ])

        # Nhóm B
        entries.extend([
            self.entry_dau_vao_diem_B, self.entry_Xd_B, self.entry_Yd_B, self.entry_Zd_B,
            self.entry_dau_vao_A2, self.entry_dau_vao_X2,
            self.entry_A2, self.entry_B2, self.entry_C2, self.entry_X2, self.entry_Y2, self.entry_Z2,
            self.entry_N5_in, self.entry_N6_in, self.entry_N7_in, self.entry_N8_in,
            self.entry_dau_vao_tam_duong_tron_B, self.entry_dau_vao_ban_kinh_duong_tron_B,
            self.entry_duong_tron_B1, self.entry_duong_tron_B2, self.entry_duong_tron_B3,
            self.entry_dau_vao_tam_mat_cau_B, self.entry_dau_vao_ban_kinh_mat_cau_B,
            self.entry_mat_cau_B1, self.entry_mat_cau_B2, self.entry_mat_cau_B3, self.entry_mat_cau_B4
        ])

        return entries

    def _on_input_data_changed(self, event):
        """Khi dữ liệu nhập thay đổi"""
        if self.imported_data:
            messagebox.showerror("Lỗi", "Đã import Excel, không thể nhập dữ liệu thủ công!")
            event.widget.delete(0, tk.END)
            return

        has_data = self._check_manual_data()

        if has_data and not self.manual_data_entered:
            self.manual_data_entered = True
            self._show_manual_buttons()
        elif not has_data and self.manual_data_entered:
            self.manual_data_entered = False
            self._hide_action_buttons()

    def _check_manual_data(self):
        """Kiểm tra xem có dữ liệu nhập thủ công không"""
        entries = self._get_all_input_entries()
        for entry in entries:
            if entry.get().strip():
                return True
        return False

    def _show_manual_buttons(self):
        """Hiện nút cho chế độ nhập thủ công"""
        self.frame_buttons_manual.grid()
        self.frame_buttons_import.grid_remove()

    def _show_import_buttons(self):
        """Hiện nút cho chế độ import Excel"""
        self.frame_buttons_import.grid()
        self.frame_buttons_manual.grid_remove()

    def _update_dropdown_options(self, *args):
        """Update dropdown options based on operation"""
        pheptoan = self.pheptoan_var.get()
        allowed_shapes = self.controller.update_dropdown_options(pheptoan)

        # Update dropdown A
        menu_A = self.dropdown1_menu["menu"]
        menu_A.delete(0, "end")
        for shape in allowed_shapes:
            menu_A.add_command(label=shape, command=lambda value=shape: self.dropdown1_var.set(value))

        # Update dropdown B
        menu_B = self.dropdown2_menu["menu"]
        menu_B.delete(0, "end")

        if pheptoan in ["Diện tích", "Thể tích"]:
            self.label_B.grid_remove()
            self.dropdown2_menu.grid_remove()
            self.dropdown2_var.set("")
        else:
            self.label_B.grid()
            self.dropdown2_menu.grid()
            for shape in allowed_shapes:
                menu_B.add_command(label=shape, command=lambda value=shape: self.dropdown2_var.set(value))

        # Set default values if current selection is not allowed
        current_A = self.dropdown1_var.get()
        current_B = self.dropdown2_var.get()

        if current_A not in allowed_shapes:
            self.dropdown1_var.set(allowed_shapes[0] if allowed_shapes else "")
        if current_B not in allowed_shapes and pheptoan not in ["Diện tích", "Thể tích"]:
            self.dropdown2_var.set(allowed_shapes[0] if allowed_shapes else "")

        self._reset_interface()

    def _reset_interface(self):
        """Reset giao diện về trạng thái ban đầu"""
        self.imported_data = False
        self.manual_data_entered = False

        self.actions._unlock_all_input_entries()

        entries = self._get_all_input_entries()
        for entry in entries:
            entry.delete(0, tk.END)

        self._hide_action_buttons()

        if self.dropdown1_var.get() and (
                self.dropdown2_var.get() or self.pheptoan_var.get() in ["Diện tích", "Thể tích"]):
            self.btn_import_excel.grid()

    def _on_kich_thuoc_changed(self, *args):
        """Xử lý khi kích thước thay đổi"""
        if self.dropdown1_var.get() == "Điểm" or self.dropdown2_var.get() == "Điểm":
            self._update_point_ui()

    def _update_point_ui(self):
        """Cập nhật giao diện nhập điểm theo kích thước"""
        # Cập nhật nhóm A
        kich_thuoc_A = self.kich_thuoc_A_var.get()
        if kich_thuoc_A == "2":
            self.entry_Zd_A.grid_remove()
        else:
            self.entry_Zd_A.grid()

        # Cập nhật nhóm B
        kich_thuoc_B = self.kich_thuoc_B_var.get()
        if kich_thuoc_B == "2":
            self.entry_Zd_B.grid_remove()
        else:
            self.entry_Zd_B.grid()

    def update_final_result_display(self, result_text):
        """Cập nhật hiển thị kết quả tổng với định dạng font đặc biệt"""
        try:
            # Xóa nội dung cũ
            self.entry_tong.delete(1.0, tk.END)  # Text widget bắt đầu từ 1.0

            # Chèn kết quả mới
            self.entry_tong.insert(tk.END, result_text)

            # 🎨 TÙY CHỈNH MÀU SẮC THEO LOẠI KẾT QUẢ
            if "LỖI" in result_text or "lỗi" in result_text:
                self.entry_tong.config(bg="#FFEBEE", fg="#D32F2F")  # Nền đỏ nhạt, chữ đỏ
            elif "Đã import" in result_text or "Đã xuất" in result_text:
                self.entry_tong.config(bg="#E8F5E8", fg="#388E3C")  # Nền xanh lá nhạt, chữ xanh
            elif "Đang xử lý" in result_text:
                self.entry_tong.config(bg="#FFF3E0", fg="#F57C00")  # Nền cam nhạt, chữ cam
            else:
                self.entry_tong.config(bg="#F8F9FA", fg="#2E86AB")  # Mặc định

        except Exception as e:
            print(f"Lỗi cập nhật hiển thị kết quả: {e}")

    def optimize_memory_usage(self):
        """Tối ưu hóa sử dụng bộ nhớ"""
        gc.collect()
        try:
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            if memory_mb > 500:
                return f"Memory usage cao: {memory_mb:.1f}MB. Cân nhắc tăng chunksize."
            return f"Memory usage: {memory_mb:.1f}MB"
        except:
            return "Memory usage: N/A"