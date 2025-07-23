# Mouse Macro Tool

## Giới thiệu
Mouse Macro Tool là ứng dụng giúp bạn ghi lại và tự động phát lại các thao tác chuột trên máy tính Windows. Ứng dụng hỗ trợ ghi lại các thao tác click, double click, giữ chuột, kéo thả (drag & drop) và cho phép chạy lại các thao tác này một cách tự động, phù hợp cho tự động hóa thao tác lặp đi lặp lại.

## Cách cài đặt
1. **Yêu cầu:**
   - Python 3.7 trở lên
   - Các thư viện: `pyautogui`, `pynput`, `tkinter`, `Pillow`
2. **Cài đặt thư viện:**
   ```bash
   pip install pyautogui pynput Pillow
   ```
   (Tkinter thường có sẵn với Python trên Windows)
3. **Chạy ứng dụng:**
   - Tải tất cả các file về để chung trong 1 thư mục
   - Hành động:
     ```bash
     Mở file ActionMouse.exe
     ```
## Tính Năng
   - Mô phỏng cử chỉ cơ bản : L/R click, Hold/Drag/Move Object

## Cách sử dụng
1. **Ghi macro:**
   - Nhấn nút "Ghi Macro" trên giao diện.
   - Thực hiện các thao tác chuột bạn muốn ghi lại (chỉ thao tác trong vùng màn hình được chọn).
   - Nhấn ESC hoặc "Lưu Macro" để dừng ghi và lưu lại macro.
2. **Chạy macro:**
   - Nhấn nút "Chạy Macro".
   - Chọn file macro đã lưu.
   - Cài đặt thời gian delay, số vòng lặp và chế độ chạy (mô phỏng trên UI hoặc chạy thật điều khiển chuột).
   - Nhấn "Bắt đầu chạy macro" để tự động thực hiện lại các thao tác đã ghi.

## Credit
- Tác giả: **Nguyễn Thành Phong**  
  Trường Đại học Văn Lang (VLU) - VLTECH
- Email liên hệ: phong.2474802010304@vanlanguni.vn
