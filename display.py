#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in7 # import the display drivers
import threading
import time
from datetime import datetime
from PIL import Image,ImageDraw,ImageFont,ImageChops # import the image libraries
import traceback
from gpiozero import Button # import the Button control from gpiozero
from signal import pause
import epsimplelib

interval = 20                                 # loop every ? seconds

btn1 = Button(5)                              # assign each button to a variable
btn2 = Button(6)                              # by passing in the pin number
btn3 = Button(13)                             # associated with the button
btn4 = Button(19)                             #

font24 = ImageFont.truetype('font/Font.ttc', 24)
font18 = ImageFont.truetype('font/Font.ttc', 18)
font35 = ImageFont.truetype('font/Font.ttc', 35)
font30 = ImageFont.truetype('font/Bangers-Regular.ttf', 30)

GRAY1  = 0xff #white
GRAY2  = 0xC0
GRAY3  = 0x80 #gray
GRAY4  = 0x00 #Blackest

GScaleimage = Image.open('pic/2in7_Scale.bmp')
bmp = Image.open('pic/100x100.bmp')
Liveimage = Image.open('pic/liveimage.bmp')

UPDATESTARTED = 0

epd = epd2in7.EPD()

def loading():
    eps = epsimplelib.EPScreen('landscape') # eps = e-Ink Paper Screen
    eps.set_title("Loading...")
    eps.update_screen()

def bmpToDisplay(image):
    print('[{}] start update display'.format(datetime.now().strftime('%I:%M:%S %p')))
    global UPDATESTARTED
    UPDATESTARTED = 1
    global Liveimage
    with Image.open('pic/liveimage.bmp') as Liveimage:
        if Liveimage.size == image.size:
            if ImageChops.difference(Liveimage, image).getbbox() is not None:
                print('[{}] = refresh display = '.format(datetime.now().strftime('%I:%M:%S %p')))
                epd.display_4Gray(epd.getbuffer_4Gray(image))
                image.save('pic/liveimage.bmp')
            else:
                print('[{}] SKIPPING display refresh'.format(datetime.now().strftime('%I:%M:%S %p')))
        else:
            print('[{}] = refresh display (different sizes) = '.format(datetime.now().strftime('%I:%M:%S %p')))
            epd.display_4Gray(epd.getbuffer_4Gray(image))
#    epd.display_4Gray(epd.getbuffer_4Gray(image))
    print('[{}]  done update display'.format(datetime.now().strftime('%I:%M:%S %p')))
    UPDATESTARTED = 0

def drawBMP():
    Himage = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(Himage)
    draw.text((70, 0), 'hello world!', font = font30, fill = 0)
    time = datetime.now().strftime('%I:%M %p')
    draw.text((90, 135), time, font = font30, fill = 0)
    # draw.line((165, 50, 165, 100), fill = 0)
    Himage.paste(bmp, (90,35))
    return Himage

def stringToDisplay(string):
    print('[{}] start writing text'.format(datetime.now().strftime('%I:%M:%S %p')))
    global UPDATESTARTED
    UPDATESTARTED = 1
    Limage = Image.new('L', (epd.height, epd.width), 0)  # 255: clear the frame
    draw = ImageDraw.Draw(Limage)
    draw.text((25, 65), string, font = font30, fill = epd.GRAY1)
    epd.display_4Gray(epd.getbuffer_4Gray(Limage))
    print('[{}]  done writing text'.format(datetime.now().strftime('%I:%M:%S %p')))
    UPDATESTARTED = 0

def handleBtnPress(btn):
    pinNum = btn.pin.number
    print('[{0}] Pin {1} received'.format(datetime.now().strftime('%I:%M:%S %p'), pinNum))

    if pinNum == 5:
        stringToDisplay('Hello World!\nButton 1')
    elif pinNum == 6:
        stringToDisplay('This is my first \nRPi project.\nButton 2')
    elif pinNum == 13:
        stringToDisplay('Hope you liked it \nButton 3')
    elif pinNum == 19:
        bmpToDisplay(GScaleimage)
 
def startTimer():
    if UPDATESTARTED:
        print('[{}] SKIPPING timed display update'.format(datetime.now().strftime('%I:%M:%S %p')))
    else:
        bmpToDisplay(drawBMP())
    threading.Timer(interval, startTimer).start()

def main():
    try:
        #logging.basicConfig(level=logging.DEBUG)

        loading()

        global epd
        epd = epd2in7.EPD()
        epd.Init_4Gray()

        # tell the button what to do when pressed
        btn1.when_pressed = handleBtnPress
        btn2.when_pressed = handleBtnPress
        btn3.when_pressed = handleBtnPress
        btn4.when_pressed = handleBtnPress

        print("Press Ctrl+C to Exit")
        startTimer()
        pause()

    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd2in7.epdconfig.module_exit()
        threading.Timer(interval, startTimer).cancel()
        exit()


#        Limage = Image.new('L', (epd.height, epd.width), 0)  # 255: clear the frame
#        draw = ImageDraw.Draw(Limage)
#        draw.text((40, 110), 'Loading...', font = font18, fill = epd.GRAY1)
#        draw.line((10, 140, 60, 190), fill = epd.GRAY1)
#        draw.line((60, 140, 10, 190), fill = epd.GRAY1)
#        draw.rectangle((10, 140, 60, 190), outline = epd.GRAY1)
#        draw.line((95, 140, 95, 190), fill = epd.GRAY1)
#        draw.line((70, 165, 120, 165), fill = epd.GRAY1)
#        draw.arc((70, 140, 120, 190), 0, 360, fill = epd.GRAY1)
#        draw.rectangle((10, 200, 60, 250), fill = epd.GRAY1)
#        draw.chord((70, 200, 120, 250), 0, 360, fill = epd.GRAY1)
#        epd.display_4Gray(epd.getbuffer_4Gray(Limage))
        #time.sleep(2)

if __name__ == "__main__":
    main()
