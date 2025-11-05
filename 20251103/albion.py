import mss
import numpy as np
import cv2
import time
import pyautogui
import win32gui
import win32con

# ---- 模板與設定 ----
template = cv2.imread(r"C:\Users\yei_pinwei\Desktop\visual\20251103\loot.jpg", 0)
if template is None:
    raise FileNotFoundError("找不到模板圖片，請檢查路徑與檔名")
else:
    w, h = template.shape[::-1]

monitor = {"left": 500, "top": 200, "width": 900, "height": 600}

threshold = 0.5
FPS_DELAY = 0.2
paused = False
running = True

# ---- UI按鈕定義 (右上角只保留結束) ----
buttons = {
    "stop": {"pos": (monitor["width"] - 110, 20), "size": (600, 200), "label": "❌ 結束"},
}

def draw_buttons(frame):
    """在畫面右上角繪製控制按鈕"""
    for key, btn in buttons.items():
        x, y = btn["pos"]
        w, h = btn["size"]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 50), -1)
        cv2.putText(frame, btn["label"], (x + 5, y + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    return frame

def check_button_click(x, y):
    """檢查滑鼠點擊是否落在按鈕範圍"""
    global running
    for key, btn in buttons.items():
        bx, by = btn["pos"]
        bw, bh = btn["size"]
        if bx <= x <= bx + bw and by <= y <= by + bh:
            if key == "stop":
                running = False
            print(f"👉 按下：{btn['label']}")
            break

# ---- 滑鼠事件 ----
def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        check_button_click(x, y)

cv2.namedWindow("Albion", cv2.WINDOW_NORMAL)
cv2.setMouseCallback("Albion", mouse_callback)

# 讓視窗保持在最上層
hwnd = win32gui.FindWindow(None, "Albion")
win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                      win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

# ---- 主程式迴圈 ----
with mss.mss() as sct:
    while running:
        # 檢查 ESC 鍵切換暫停/繼續
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC鍵
            paused = not paused
            print("⏸ 暫停中" if paused else "▶ 繼續搜尋")
        elif key == ord('q'):
            break

        if not paused:
            img = np.array(sct.grab(monitor))
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

            # 模板比對
            res = cv2.matchTemplate(gray_img, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            if max_val >= threshold:
                print("✅ 找到相似圖片!")
                # 計算模板中心位置
                center_x = monitor["left"] + max_loc[0] + w // 2
                center_y = monitor["top"] + max_loc[1] + h // 2

                # 模擬 Shift + 點擊
                pyautogui.keyDown('shift')
                pyautogui.click(center_x, center_y)
                pyautogui.keyUp('shift')

                paused = True  # 找到後暫停
            else:
                print("❌ 未找到相似圖片")
        else:
            img = np.array(sct.grab(monitor))
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

        # 顯示畫面 + UI
        ui_frame = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)
        ui_frame = draw_buttons(ui_frame)
        cv2.imshow("Albion", ui_frame)

        time.sleep(FPS_DELAY)

cv2.destroyAllWindows()
