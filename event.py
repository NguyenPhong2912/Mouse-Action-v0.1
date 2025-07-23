# event.py
# File này sẽ chứa các hàm xử lý sự kiện cho MacroApp

import pyautogui 
import threading
import macro_storage
import os
import subprocess
import tkinter as tk
import time
import datetime


from tkinter import filedialog
from pynput.mouse import Controller, Button
from PIL import ImageGrab, ImageTk
from pynput import mouse


recorded_events = []
listener = None
recording = False
record_shape = None
record_canvas = None
drag_start = None  

last_click_time = 0
click_count = 0
hold_start_time = None
HOLD_THRESHOLD = 0.3  # giây
DOUBLE_CLICK_THRESHOLD = 0.3  # giây

# Thêm biến lưu ảnh screenshot
screenshot_img = None
screenshot_tk = None

def is_in_shape(x, y):
    global record_shape
    if record_shape is None:
        return True
    left = record_shape.winfo_rootx()
    top = record_shape.winfo_rooty()
    right = left + record_shape.winfo_width()
    bottom = top + record_shape.winfo_height()
    return left <= x <= right and top <= y <= bottom

def show_ripple_animation(x, y):
    global record_canvas, record_shape
    if record_canvas is None or record_shape is None:
        return
    canvas_x = x - record_shape.winfo_rootx()
    canvas_y = y - record_shape.winfo_rooty()
    ripple = record_canvas.create_oval(canvas_x-10, canvas_y-10, canvas_x+10, canvas_y+10, outline='blue', width=3)
    def expand():
        for i in range(10):
            def update_coords(i=i):
                if record_canvas is not None:
                    record_canvas.coords(ripple, canvas_x-10-i*2, canvas_y-10-i*2, canvas_x+10+i*2, canvas_y+10+i*2)
            if record_canvas is not None:
                record_canvas.after(i*15, update_coords)
        def delete_ripple():
            if record_canvas is not None:
                record_canvas.delete(ripple)
        if record_canvas is not None:
            record_canvas.after(150, delete_ripple)
    expand()

def on_move(x, y):
    # Không lưu khi move nữa
    pass

def on_scroll(x, y, dx, dy):
    # Không lưu khi scroll nữa
    pass

# --- GHI CLICK, DOUBLE CLICK, HOLD ---
def on_click(x, y, button, pressed):
    global drag_start, last_click_time, click_count, hold_start_time
    now = time.time()
    if recording and is_in_shape(x, y):
        if pressed:
            # Kiểm tra double click
            if now - last_click_time < DOUBLE_CLICK_THRESHOLD:
                click_count += 1
            else:
                click_count = 1
            last_click_time = now
            hold_start_time = now
            if click_count == 2:
                recorded_events.append(('double_click', x, y, str(button)))
                print(f"Lưu thao tác double click tại ({x}, {y}), button={button}")
                click_count = 0
            else:
                recorded_events.append(('click', x, y, str(button), pressed))
                print(f"Lưu tọa độ click: ({x}, {y})")
                show_ripple_animation(x, y)
            # Ghi nhận bắt đầu kéo (drag)
            if pressed and button == mouse.Button.left:
                drag_start = (x, y)
        else:
            # Kiểm tra nhấn giữ (hold)
            if hold_start_time and (now - hold_start_time) > HOLD_THRESHOLD:
                recorded_events.append(('hold', x, y, str(button), now - hold_start_time))
                print(f"Lưu thao tác nhấn giữ tại ({x}, {y}), button={button}, thời gian: {now - hold_start_time:.2f}s")
            # Ghi nhận kết thúc kéo (drop)
            if not pressed and button == mouse.Button.left:
                if drag_start is not None and (x, y) != drag_start:
                    recorded_events.append(('drag', drag_start[0], drag_start[1], x, y))
                    print(f"Lưu thao tác kéo thả: từ ({drag_start[0]}, {drag_start[1]}) đến ({x}, {y})")
                drag_start = None
            hold_start_time = None

# --- SHOW SHAPE VỚI ẢNH CHỤP MÀN HÌNH ---
def show_record_shape():
    global record_shape, record_canvas, screenshot_img, screenshot_tk
    if record_shape is not None:
        try:
            record_shape.lift()
            return
        except:
            pass
    # Chụp màn hình
    screenshot_img = ImageGrab.grab()
    record_shape = tk.Toplevel()
    record_shape.title("Vùng ghi macro")
    record_shape.attributes('-fullscreen', True)
    record_shape.attributes('-topmost', True)
    record_shape.configure(bg='gray90')
    record_shape.attributes('-alpha', 0.98)
    record_canvas = tk.Canvas(record_shape, bg='gray90', highlightthickness=0)
    record_canvas.pack(fill='both', expand=True)
    # Hiển thị ảnh screenshot làm nền
    screenshot_tk = ImageTk.PhotoImage(screenshot_img)
    record_canvas.create_image(0, 0, anchor='nw', image=screenshot_tk)
    label = tk.Label(record_shape, text="Đang ghi macro... Chỉ thao tác trong vùng này sẽ được ghi lại.\nNhấn ESC để thoát ghi macro", font=("Arial", 24), bg='gray90')
    label.place(relx=0.5, rely=0.05, anchor='n')
    def on_close():
        global record_shape, record_canvas, screenshot_img, screenshot_tk
        if record_shape:
            record_shape.destroy()
            record_shape = None
            record_canvas = None
            screenshot_img = None
            screenshot_tk = None
    record_shape.protocol("WM_DELETE_WINDOW", on_close)
    def on_esc(event):
        print("Đã nhấn ESC - Thoát ghi macro.")
        stop_recording()
    record_shape.bind('<Escape>', on_esc)


def start_recording():
    global listener, recording, recorded_events
    recorded_events = []
    recording = True
    show_record_shape()
    listener = mouse.Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll
    )
    listener.start()
    print("Bắt đầu ghi macro...")

def stop_recording():
    global listener, recording, record_shape, record_canvas
    recording = False
    if listener:
        listener.stop()
        listener = None
    if record_shape:
        record_shape.destroy()
        record_shape = None
    record_canvas = None
    print("Dừng ghi macro.")
    # Tự động lưu macro khi dừng ghi
    if recorded_events:
        folder = os.path.join(os.getcwd(), 'marco_storage')
        if not os.path.exists(folder):
            os.makedirs(folder)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(folder, f"macro_{timestamp}.json")
        print(f"Số thao tác sẽ lưu: {len(recorded_events)}")
        for i, event in enumerate(recorded_events, 1):
            print(f"{i}: {event}")
        macro_storage.save_macro_to_file(recorded_events, file_path)
        print(f"Đã lưu macro vào: {file_path}")
    else:
        print("Không có thao tác nào để lưu.")


def record_macro():
    # Hàm này sẽ được gọi khi bấm nút Ghi Macro
    # Có thể disable các nút khác ở đây nếu cần
    threading.Thread(target=start_recording).start()

def save_macro():
    # Hàm này sẽ được gọi khi bấm nút Lưu Macro
    stop_recording()  # Đảm bảo shape đóng và dừng ghi trước khi lưu
    # Đảm bảo thư mục marco_storage tồn tại
    folder = os.path.join(os.getcwd(), 'marco_storage')
    if not os.path.exists(folder):
        os.makedirs(folder)
    if not recorded_events:
        print("Không có thao tác nào để lưu.")
        return
    # Chọn tên file lưu
    file_path = filedialog.asksaveasfilename(
        title="Lưu macro",
        initialdir=folder,
        defaultextension=".json",
        filetypes=[("Macro files", "*.json"), ("All files", "*.*")],
        initialfile="macro.json"
    )
    if not file_path:
        print("Đã hủy lưu macro.")
        return
    print(f"Số thao tác sẽ lưu: {len(recorded_events)}")
    for i, event in enumerate(recorded_events, 1):
        print(f"{i}: {event}")
    macro_storage.save_macro_to_file(recorded_events, file_path)
    print(f"Đã lưu macro vào: {file_path}")
    # Mở thư mục chứa file macro
    folder = os.path.dirname(file_path)
    try:
        if os.name == 'nt':  # Windows
            os.startfile(folder)
        elif os.name == 'posix':
            subprocess.Popen(['xdg-open', folder])
        else:
            print(f"Hãy mở thư mục thủ công: {folder}")
    except Exception as e:
        print(f"Không thể mở thư mục: {e}")

def run_macro():
    # Mở giao diện chọn file macro từ thư mục marco_storage
    folder = os.path.join(os.getcwd(), 'marco_storage')
    if not os.path.exists(folder):
        os.makedirs(folder)
    file_path = filedialog.askopenfilename(
        title="Chọn file macro để chạy",
        initialdir=folder,
        filetypes=[("Macro files", "*.json"), ("All files", "*.*")]
    )
    if not file_path:
        print("Không chọn file macro nào.")
        return
    print(f"Đã chọn file macro: {file_path}")
    # Hiện bảng setting tốc độ và số vòng lặp
    setting = tk.Toplevel()
    setting.title("Cài đặt chạy macro")
    setting.geometry("400x350")  # Tăng chiều cao và rộng cho thoải mái
    setting.resizable(False, False)  # Không cho resize để tránh layout vỡ
    frm = tk.Frame(setting)
    frm.pack(fill='both', expand=True, padx=20, pady=20)
    tk.Label(frm, text="Thời gian delay giữa các node (giây):", font=("Arial", 12)).pack(pady=(0,5), anchor='w')
    delay_var = tk.DoubleVar(value=0.5)
    tk.Entry(frm, textvariable=delay_var, font=("Arial", 12), width=15).pack(pady=(0,10), anchor='w')
    tk.Label(frm, text="Số vòng lặp macro:", font=("Arial", 12)).pack(pady=(0,5), anchor='w')
    loop_var = tk.IntVar(value=1)
    tk.Entry(frm, textvariable=loop_var, font=("Arial", 12), width=15).pack(pady=(0,10), anchor='w')
    run_type_var = tk.StringVar(value="simulate")
    tk.Label(frm, text="Chế độ chạy:", font=("Arial", 12)).pack(pady=(0,5), anchor='w')
    tk.Radiobutton(frm, text="Mô phỏng trên UI", variable=run_type_var, value="simulate", font=("Arial", 11)).pack(anchor='w')
    tk.Radiobutton(frm, text="Chạy thật (điều khiển chuột)", variable=run_type_var, value="real", font=("Arial", 11)).pack(anchor='w')
    def on_confirm():
        delay = delay_var.get()
        loop = loop_var.get()
        run_type = run_type_var.get()
        print(f"Chạy macro với delay: {delay}s, số vòng lặp: {loop}, kiểu: {run_type}")
        setting.destroy()
        if run_type == "simulate":
            play_macro(file_path, delay, loop)
        else:
            run_macro_real(file_path, delay, loop)
    btn = tk.Button(frm, text="Bắt đầu chạy macro", font=("Arial", 13, 'bold'), command=on_confirm, bg='#4CAF50', fg='white', height=2)
    btn.pack(pady=(20,0), fill='x')
    setting.transient()
    setting.grab_set()
    setting.wait_window()

# --- CHẠY THẬT (điều khiển chuột thật) ---
def run_macro_real(file_path, delay, loop):
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
                pyautogui.moveTo(x, y)
                pyautogui.click()
                time.sleep(delay)
            elif event[0] == 'double_click':
                x, y = event[1], event[2]
                print(f"Double click tại ({x}, {y})")
                pyautogui.moveTo(x, y)
                pyautogui.click(clicks=2, interval=0.1)
                time.sleep(delay)
            elif event[0] == 'hold':
                x, y, _, hold_time = event[1], event[2], event[3], event[4]
                print(f"Nhấn giữ tại ({x}, {y}) trong {hold_time:.2f}s")
                pyautogui.moveTo(x, y)
                pyautogui.mouseDown()
                time.sleep(hold_time)
                pyautogui.mouseUp()
                time.sleep(delay)
            elif event[0] == 'drag':
                x1, y1, x2, y2 = event[1], event[2], event[3], event[4]
                print(f"Kéo thả từ ({x1}, {y1}) đến ({x2}, {y2})")
                pyautogui.moveTo(x1, y1)
                pyautogui.mouseDown()
                time.sleep(0.7)  # Giữ chuột lâu hơn
                # Di chuyển nhẹ 10 pixel để Windows nhận diện kéo
                pyautogui.moveTo(x1+10, y1+10, duration=0.1)
                time.sleep(0.1)
                pyautogui.moveTo(x2, y2, duration=0.5)
                pyautogui.mouseUp()
                time.sleep(delay)
    print("Đã hoàn thành chạy macro thật!")

# --- CHẠY CLICK, DOUBLE CLICK, HOLD, DRAG ---
# --- MÔ PHỎNG LẠI TRÊN SHAPE ---
def play_macro(file_path, delay, loop):
    import macro_storage
    import time
    global record_shape, record_canvas, screenshot_img, screenshot_tk
    # Hiện shape với screenshot
    screenshot_img = ImageGrab.grab()
    record_shape = tk.Toplevel()
    record_shape.title("Mô phỏng macro")
    record_shape.attributes('-fullscreen', True)
    record_shape.attributes('-topmost', True)
    record_shape.configure(bg='gray90')
    record_shape.attributes('-alpha', 0.98)
    record_canvas = tk.Canvas(record_shape, bg='gray90', highlightthickness=0)
    record_canvas.pack(fill='both', expand=True)
    screenshot_tk = ImageTk.PhotoImage(screenshot_img)
    record_canvas.create_image(0, 0, anchor='nw', image=screenshot_tk)
    label = tk.Label(record_shape, text="Đang mô phỏng macro...", font=("Arial", 24), bg='gray90')
    label.place(relx=0.5, rely=0.05, anchor='n')
    def on_close():
        global record_shape, record_canvas, screenshot_img, screenshot_tk
        if record_shape:
            record_shape.destroy()
            record_shape = None
            record_canvas = None
            screenshot_img = None
            screenshot_tk = None
    record_shape.protocol("WM_DELETE_WINDOW", on_close)
    record_shape.update()
    macro_data = macro_storage.insert_macro_from_file(file_path)
    if not macro_data:
        print("Không đọc được macro.")
        return
    for l in range(loop):
        print(f"--- Vòng lặp {l+1} ---")
        for event in macro_data:
            if event[0] == 'click':
                x, y = event[1], event[2]
                print(f"Mô phỏng click tại ({x}, {y})")
                show_ripple_animation_on_canvas(x, y)
                time.sleep(delay)
            elif event[0] == 'double_click':
                x, y = event[1], event[2]
                print(f"Mô phỏng double click tại ({x}, {y})")
                show_ripple_animation_on_canvas(x, y, double=True)
                time.sleep(delay)
            elif event[0] == 'hold':
                x, y, _, hold_time = event[1], event[2], event[3], event[4]
                print(f"Mô phỏng nhấn giữ tại ({x}, {y}), thời gian: {hold_time:.2f}s")
                show_hold_animation_on_canvas(x, y, hold_time)
                time.sleep(delay)
            elif event[0] == 'drag':
                x1, y1, x2, y2 = event[1], event[2], event[3], event[4]
                print(f"Mô phỏng kéo thả từ ({x1}, {y1}) đến ({x2}, {y2})")
                show_drag_animation_on_canvas(x1, y1, x2, y2)
                time.sleep(delay)
    print("Đã hoàn thành mô phỏng macro!")
    record_shape.destroy()
    record_shape = None
    record_canvas = None
    screenshot_img = None
    screenshot_tk = None

# --- HIỆU ỨNG MÔ PHỎNG ---
def show_ripple_animation_on_canvas(x, y, double=False):
    global record_canvas
    if record_canvas is None:
        return
    color = 'red' if double else 'blue'
    ripple = record_canvas.create_oval(x-10, y-10, x+10, y+10, outline=color, width=3)
    def expand():
        for i in range(10):
            record_canvas.after(i*15, lambda i=i: record_canvas.coords(ripple, x-10-i*2, y-10-i*2, x+10+i*2, y+10+i*2))
        record_canvas.after(150, lambda: record_canvas.delete(ripple))
    expand()

def show_hold_animation_on_canvas(x, y, hold_time):
    global record_canvas
    if record_canvas is None:
        return
    ripple = record_canvas.create_oval(x-10, y-10, x+10, y+10, outline='green', width=3)
    record_canvas.after(int(hold_time*1000), lambda: record_canvas.delete(ripple))

def show_drag_animation_on_canvas(x1, y1, x2, y2):
    global record_canvas
    if record_canvas is None:
        return
    dot = record_canvas.create_oval(x1-8, y1-8, x1+8, y1+8, fill='orange', outline='orange')
    steps = 20
    dx = (x2 - x1) / steps
    dy = (y2 - y1) / steps
    def move_dot(step=0):
        if step > steps:
            record_canvas.delete(dot)
            return
        record_canvas.coords(dot, x1-8+dx*step, y1-8+dy*step, x1+8+dx*step, y1+8+dy*step)
        record_canvas.after(20, lambda: move_dot(step+1))
    move_dot()

# --- Biến toàn cục cho drag --- 