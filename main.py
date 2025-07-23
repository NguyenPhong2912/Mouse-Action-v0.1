import tkinter as tk
import time
import macro_storage
import event

from tkinter import messagebox, simpledialog, filedialog
from pynput.mouse import Controller, Button


class MacroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Macro Tool")
        self.create_widgets()

    def create_widgets(self):
        self.record_btn = tk.Button(self.root, text="Ghi Macro", width=20, command=event.record_macro)
        self.record_btn.grid(row=0, column=0, padx=10, pady=10)

        self.save_btn = tk.Button(self.root, text="Lưu Macro", width=20, command=event.save_macro)
        self.save_btn.grid(row=0, column=1, padx=10, pady=10)

        self.run_btn = tk.Button(self.root, text="Chạy Macro", width=20, command=event.run_macro)
        self.run_btn.grid(row=1, column=0, padx=10, pady=10)

        # self.log_btn = tk.Button(self.root, text="Xem Log", width=20, command=event.view_log)
        # self.log_btn.grid(row=1, column=1, padx=10, pady=10)

        self.status_label = tk.Label(self.root, text="Trạng thái: Sẵn sàng", anchor="w")
        self.status_label.grid(row=2, column=0, columnspan=2, sticky="we", padx=10, pady=10)

def play_macro(file_path, delay, loop):
    mouse = Controller()
    macro_data = macro_storage.insert_macro_from_file(file_path)
    if not macro_data:
        print("Không đọc được macro.")
        return
    for l in range(loop):
        print(f"--- Vòng lặp {l+1} ---")
        for event in macro_data:
            if event[0] == 'click':
                x, y = event[1], event[2]
                print(f"Click tại ({x}, {y})")
                mouse.position = (x, y)
                mouse.press(Button.left)
                mouse.release(Button.left)
                time.sleep(delay)

if __name__ == "__main__":
    root = tk.Tk()
    app = MacroApp(root)
    root.mainloop() 