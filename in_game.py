
# import tools.infer.predict_system as ps
# import tools.infer.utility as utility
import os
from PIL import Image, ImageGrab
import time
import pyautogui as pg
import win32api
import win32con
import win32gui




i = 1
while True:
    img = ImageGrab.grab((0, 0, 1880, 800))  
    file = r'./imgs/{}.jpg'.format(i)
    img.save(file)
    # fansname,rec_res = ps.main(utility.parse_args())
    time.sleep(3)
    print(i)
    i += 1
    

def baoming():
    if pg.pixelMatchesColor(1050, 660, (84, 185, 17), tolerance=10):
        pg.moveTo(1100, 660,duration=0.6)
        pg.click()
        time.sleep(1)
        return 1
    else:
        pg.moveTo(1250, 350,duration=0.6)
        pg.click()
        time.sleep(1)
        return 0

def in_newplayer():
    pg.moveTo(400, 240,duration=0.6)
    pg.click()
    time.sleep(1)
    res = baoming()
    return res

def in_500player():
    pg.moveTo(740, 240,duration=0.6)
    pg.click()
    time.sleep(1)
    res = baoming()
    return res


# res = in_500player()

# if res == 0:
#     in_newplayer()
























