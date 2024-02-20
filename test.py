
import os
from skimage import io
import matplotlib.pyplot as plt
from PIL import Image, ImageGrab
from skimage import io
import win32api
import win32con
import win32gui
import time
import pyautogui as pg

def show_img(name):
    # file = './imgs/{}.jpg'.format(name)
    file = './imgs/{}.png'.format(name)
    img = Image.open(file)
    plt.imshow(img)
    plt.show()
    
def set_forward():
    hwnd_title = {}
    def get_all_hwnd(hwnd, mouse):
        if (win32gui.IsWindow(hwnd) and
            win32gui.IsWindowEnabled(hwnd) and
            win32gui.IsWindowVisible(hwnd)):
            hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})

    win32gui.EnumWindows(get_all_hwnd, 0)
    for h, t in hwnd_title.items():
        if t :
            if '斗地主-新手场' in t:
                h = win32gui.FindWindow(None,t)
                if not win32gui.GetWindowLong(h, win32con.GWL_EXSTYLE):
                    pg.press('enter')
                    win32gui.SetForegroundWindow(h)
                    time.sleep(1)
                break



if __name__ == "__main__":
    # show_img(1)
    os.listdir('./imgs')
    print(len(os.listdir('./imgs')))

 






















