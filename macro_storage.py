import json
import pyautogui
import time

# macro_storage.py
# File này sẽ xử lý việc lưu và chèn (insert) macro

def save_macro_to_file(macro_data, file_path):
    """
    Lưu macro vào file.
    macro_data: dữ liệu macro (danh sách các sự kiện, v.v.)
    file_path: đường dẫn file để lưu
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(macro_data, f, ensure_ascii=False, indent=2)
        print(f"Lưu macro vào {file_path}")
    except Exception as e:
        print(f"Lỗi khi lưu macro: {e}")


def insert_macro_from_file(file_path):
    """
    Đọc macro từ file và trả về dữ liệu macro.
    file_path: đường dẫn file macro
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            macro_data = json.load(f)
        print(f"Đọc macro từ {file_path}")
        return macro_data
    except Exception as e:
        print(f"Lỗi khi đọc macro: {e}")
        return None 

time.sleep(3)  # Đợi 3 giây để bạn chuyển sang cửa sổ khác
pyautogui.moveTo(100, 100)
pyautogui.click() 