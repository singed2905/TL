import PyInstaller.__main__
import os
import shutil

def build():
    app_name = "main"  # Xuất ra file main.exe
    main_script = "main.py"

    # Xóa thư mục build/dist cũ (nếu có)
    for folder in ["build", "dist"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)

    # Lệnh build EXE
    PyInstaller.__main__.run([
        main_script,
        "--onefile",                 # Gộp thành 1 file duy nhất
        "--noconsole",               # Ẩn cửa sổ console (nếu muốn hiển thị thì bỏ dòng này)
        "--name", app_name,          # Đặt tên file xuất ra là main.exe
        "--add-data", "config;config",          # Giữ nguyên thư mục config
        "--add-data", "controllers;controllers",
        "--add-data", "models;models",
        "--add-data", "processors;processors",
        "--add-data", "utils;utils",
        "--add-data", "views;views",
    ])

    # Di chuyển file exe ra cùng cấp với main.py
    exe_path = os.path.join("dist", f"{app_name}.exe")
    if os.path.exists(exe_path):
        shutil.move(exe_path, "./main.exe")

    print("✅ Build hoàn tất! File main.exe đã được tạo thành công.")

if __name__ == "__main__":
    build()
