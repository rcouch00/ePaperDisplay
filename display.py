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
import requests # pip3 install requests
from PIL import Image,ImageDraw,ImageFont,ImageChops # pip3 install pillow
import traceback
from gpiozero import Button # pip3 install gpiozero
from signal import pause
import epsimplelib
import imgkit # pip3 install imgkit
from string import Template

interval = 20                                 # loop every ? seconds

btn1 = Button(5)                              # assign each button to a variable
btn2 = Button(6)                              # by passing in the pin number
btn3 = Button(13)                             # associated with the button
btn4 = Button(19)                             #

font24 = ImageFont.truetype('font/Font.ttc', 24)
font18 = ImageFont.truetype('font/Font.ttc', 18)
font35 = ImageFont.truetype('font/Font.ttc', 35)
font30 = ImageFont.truetype('font/Bangers-Regular.ttf', 30)
font50 = ImageFont.truetype('font/digital-7 (mono).ttf', 50)

GRAY1  = 0xff #white        #FFFFFF
GRAY2  = 0xC0               #C0C0C0
GRAY3  = 0x80 #gray         #808080
GRAY4  = 0x00 #Blackest     #000000

#swap width and height to use landscape
DEVICE_WIDTH = 176
DEVICE_HEIGHT = 264

GScaleimage = Image.open('pic/2in7_Scale.bmp')
bmp = Image.open('pic/hashrate_test.bmp')
#bmp = Image.open('pic/Pico_3in7.bmp')
#bmp = Image.open('pic/100x100.bmp')
Liveimage = Image.open('pic/liveimage.bmp')

UPDATESTARTED = 0

epd = epd2in7.EPD()

def loading():
    print('Loading...')
    #eps = epsimplelib.EPScreen('landscape') # eps = e-Ink Paper Screen
    #eps.set_title("Loading...")
    #eps.update_screen()
    stringToDisplayCenter('Loading...')

def bmpToDisplay(image):
    print('[{}] start update display'.format(datetime.now().strftime('%I:%M:%S %p')))
    global UPDATESTARTED
    UPDATESTARTED = 1
    global Liveimage
    blank = Image.new('L', (DEVICE_HEIGHT, DEVICE_WIDTH), 255)  # 0 = black, 255 = white: clear the frame
    with Image.open('pic/liveimage.bmp').convert(image.mode) as Liveimage:
        if Liveimage.size == image.size:
            if ImageChops.difference(Liveimage, image).getbbox() is not None:
                print('[{}] = refresh display = '.format(datetime.now().strftime('%I:%M:%S %p')))
                epd.display_4Gray(epd.getbuffer_4Gray(blank)) #clear the screen
                epd.display_4Gray(epd.getbuffer_4Gray(image))
                image.save('pic/liveimage.bmp')
            else:
                print('[{}] SKIPPING display refresh'.format(datetime.now().strftime('%I:%M:%S %p')))
        else:
            print('[{}] = refresh display (different sizes) = '.format(datetime.now().strftime('%I:%M:%S %p')))
            epd.display_4Gray(epd.getbuffer_4Gray(blank)) #clear the screen
            epd.display_4Gray(epd.getbuffer_4Gray(image))

    print('[{}]  done update display'.format(datetime.now().strftime('%I:%M:%S %p')))
    UPDATESTARTED = 0

def drawBMP():
    Himage = Image.new('L', (DEVICE_HEIGHT, DEVICE_WIDTH), 255)
    draw = ImageDraw.Draw(Himage)
    Himage.paste(bmp, (0,0)) #0,37
    time = datetime.now().strftime('%I:%M')
    draw.text((35, 135), time, font = font50, fill = 0)
    timeDay = datetime.now().strftime('%p')
    draw.text((175, 135), timeDay, font = font50, fill = 0)
    return Himage

def stringToDisplayCenter(string):
    print('[{}] start writing text'.format(datetime.now().strftime('%I:%M:%S %p')))
    global UPDATESTARTED
    UPDATESTARTED = 1
    Limage = Image.new('L', (DEVICE_HEIGHT, DEVICE_WIDTH), 0)  # 0 = black, 255 = white: clear the frame
    Limage = drawCrossHairs(Limage)
    draw = ImageDraw.Draw(Limage)
    draw.text(((DEVICE_HEIGHT/2),(DEVICE_WIDTH/2)), string, anchor="lt", font = font30, fill = GRAY1)
    del draw
    epd.display_4Gray(epd.getbuffer_4Gray(Limage))
    print('[{}]  done writing text'.format(datetime.now().strftime('%I:%M:%S %p')))
    UPDATESTARTED = 0

def drawCrossHairs(Limage):
    imWidth, imHeight = Limage.size
    chLen = int(min(imWidth, imHeight) / 6)
    gapLen = int(min(imWidth, imHeight) / 60)
    lineWidth = int(max(imWidth, imHeight) / 500)
    lines = []
    l = (imWidth / 2 - gapLen - chLen, imHeight /
         2, imWidth / 2 - gapLen, imHeight / 2)
    lines.append(l)
    l = (imWidth / 2 + gapLen, imHeight /
         2, imWidth / 2 + gapLen + chLen, imHeight / 2)
    lines.append(l)
    l = (imWidth / 2, imHeight /
         2 - gapLen - chLen, imWidth / 2, imHeight / 2 - gapLen)
    lines.append(l)
    l = (imWidth / 2, imHeight /
         2 + gapLen, imWidth / 2, imHeight / 2 + gapLen + chLen)
    lines.append(l)
    
    # GENERATE THE DRAW OBJECT AND DRAW THE CROSSHAIRS
    draw = ImageDraw.Draw(Limage)
    draw.line(l, fill=GRAY1, width=lineWidth)
    for l in lines:
        draw.line(l, fill=GRAY1, width=lineWidth)
    del draw
    return Limage
    
def timeToDisplay():
    print('[{}] start writing text'.format(datetime.now().strftime('%I:%M:%S %p')))
    global UPDATESTARTED
    UPDATESTARTED = 1
    string = datetime.now().strftime('%I:%M')
    Limage = Image.new('L', (DEVICE_HEIGHT, DEVICE_WIDTH), 0)  # 0 = black, 255 = white: clear the frame
    draw = ImageDraw.Draw(Limage)
    draw.text((5, 5), string, font = font50, fill = GRAY1)
    epd.display_4Gray(epd.getbuffer_4Gray(Limage))
    print('[{}]  done writing text'.format(datetime.now().strftime('%I:%M:%S %p')))
    UPDATESTARTED = 0
    
def htmlTest():
    print('[{}] start html test'.format(datetime.now().strftime('%I:%M:%S %p')))
    global UPDATESTARTED
    UPDATESTARTED = 1
    wallets = """
    <table style="border-collapse: collapse; width: 100%; height: 54px;" border="1">
    <tbody>
    <tr style="height: 18px;">
    <td style="width: 33.3333%; height: 18px;">ETH</td>
    <td style="width: 33.3333%; height: 18px; text-align: center;">0.049237</td>
    <td style="width: 33.3333%; height: 18px;">&darr;</td>
    </tr>
    <tr style="height: 18px;">
    <td style="width: 33.3333%; height: 18px;">ZIL</td>
    <td style="width: 33.3333%; height: 18px; text-align: center;">10.2629</td>
    <td style="width: 33.3333%; height: 18px;">&uarr;</td>
    </tr>
    <tr style="height: 18px;">
    <td style="width: 33.3333%; height: 18px;">ALGO</td>
    <td style="width: 33.3333%; text-align: center; height: 18px;">XXXX</td>
    <td style="width: 33.3333%; height: 18px;">&harr;</td>
    </tr>
    </tbody>
    </table>
    """
    loki = """
    <table style="border-collapse: collapse; width: 100%; height: 54px;" border="1">
    <tbody>
    <tr style="height: 18px;">
    <td style="width: 33.3333%; height: 18px;">Loki</td>
    <td style="width: 33.3333%; height: 18px;">&nbsp;</td>
    <td style="width: 33.3333%; height: 18px;">1 minute ago</td>
    </tr>
    <tr style="height: 18px;">
    <td style="width: 33.3333%; height: 18px;">current</td>
    <td style="width: 33.3333%; height: 18px; text-align: center;">average</td>
    <td style="width: 33.3333%; height: 18px;">reported</td>
    </tr>
    <tr style="height: 18px;">
    <td style="width: 33.3333%; height: 18px;">342.88 MH/s</td>
    <td style="width: 33.3333%; height: 18px; text-align: center;">357.68 MH/s</td>
    <td style="width: 33.3333%; height: 18px;">347.31 MH/s</td>
    </tr>
    </tbody>
    </table>
    """
    odin = """
    <table style="border-collapse: collapse; width: 100%;" border="1">
    <tbody>
    <tr>
    <td style="width: 33.3333%;">Loki</td>
    <td style="width: 33.3333%;">&nbsp;</td>
    <td style="width: 33.3333%;">1 minute ago</td>
    </tr>
    <tr>
    <td style="width: 33.3333%;">current</td>
    <td style="width: 33.3333%; text-align: center;">average</td>
    <td style="width: 33.3333%;">reported</td>
    </tr>
    <tr>
    <td style="width: 33.3333%;">342.88 MH/s</td>
    <td style="width: 33.3333%; text-align: center;">357.68 MH/s</td>
    <td style="width: 33.3333%;">347.31 MH/s</td>
    </tr>
    </tbody>
    </table>
    """
    body = """
    <html>
      <head>
        <meta content="bmp"/>
        <meta content="Lanscape"/>
      </head>
      <center>$table</center>
      <hr />
      <center>$time</center>
    </html>
    """
    options = {
        'width': DEVICE_HEIGHT,
        'height': DEVICE_WIDTH,
        'disable-smart-width': '',
        'encoding': 'UTF-8'
    }
    t = Template(body)
    imgkit.from_string(t.substitute(table=wallets, time=datetime.now().strftime('%I:%M %p')), 'pic/out.bmp', options=options)
    with Image.open('pic/out.bmp').convert(Liveimage.mode) as image:
        bmpToDisplay(image);
    print('[{}]  done html test'.format(datetime.now().strftime('%I:%M:%S %p')))
    UPDATESTARTED = 0
    

def handleBtnPress(btn):
    pinNum = btn.pin.number
    print('[{0}] Pin {1} received'.format(datetime.now().strftime('%I:%M:%S %p'), pinNum))

    if pinNum == 5:
        htmlTest()
        #stringToDisplayCenter('Button 1')
    elif pinNum == 6:
        stringToDisplayCenter('Button 2')
    elif pinNum == 13:
        stringToDisplayCenter('Button 3')
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
#        logging.basicConfig(level=logging.DEBUG)

        print("Initializing ePaper Display")

        global epd
        epd = epd2in7.EPD()
        epd.Init_4Gray()
        
        loading()

        # tell the button what to do when pressed
        btn1.when_pressed = handleBtnPress
        #handleBtnPress(5)
        btn2.when_pressed = handleBtnPress
        #handleBtnPress(6)
        btn3.when_pressed = handleBtnPress
        #handleBtnPress(13)
        btn4.when_pressed = handleBtnPress
        #handleBtnPress(19)

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

#        Limage = Image.new('L', (epd.height, epd.width), 0)  # 0 = black, 255 = white: clear the frame
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
