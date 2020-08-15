#!/usr/bin/env python3
###################################################
##
##  oled1090.py
##  Dump1090 data on Oled micro display
##
###################################################

from math import sin, cos, sqrt, atan2, radians
from datetime import datetime
import time
import urllib.request
import json

from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306, sh1106
from luma.core.render import canvas
from PIL import Image, ImageDraw, ImageFont

# path to dump1090 data
url = "http://127.0.0.1/dump1090-fa/data/aircraft.json"

# replace your coordinates in brackets
lat2 = radians(41.910900)
lon2 = radians(12.481800)

# approximate radius of earth in km
R = 6373.0

# terrestrial miles conversion factor
# conv_fac = 0.621371

# nautical miles conversion factor
conv_fac = 0.539957

# proximity range in km
proximity = 50

# substitute spi(device=0, port=0) below if using that interface
serial = i2c(port=1, address=0x3C)

# substitute ssd1331(...) or sh1106(...) below if using that device
device = ssd1306(serial)

# other bitmap fonts you can try
# from www.dafont.com
#
# font=ImageFont.truetype('/home/pi/oled1090/fonts/Volter__28Goldfish_29.ttf', 9)
# font=ImageFont.truetype('/home/pi/oled1090/fonts/Squarewave.ttf', 16)
# font=ImageFont.truetype('/home/pi/oled1090/fonts/RetroGaming.ttf', 11)
# font=ImageFont.truetype('/home/pi/oled1090/fonts/PokemonClassic.ttf', 8)
# font=ImageFont.truetype('/home/pi/oled1090/fonts/pixelade.ttf', 13)
# font=ImageFont.truetype('/home/pi/oled1090/fonts/new-gen.ttf', 9)
# font=ImageFont.truetype('/home/pi/oled1090/fonts/CodersCrux.ttf', 16)
# font=ImageFont.truetype('/home/pi/oled1090/fonts/Minecraftia-Regular.ttf', 8)
font=ImageFont.truetype('/home/pi/oled1090/fonts/PixelOperator.ttf', 16)

# wait a while for dump1090 to start
time.sleep(30)

top = 0
offset = 24
width = device.width
record = 0

while True:
    # wait and retry if dump1090 is inactive
    while True:
        try:
            data = urllib.request.urlopen(url).read()
            break
        except urllib.error.HTTPError:
            time.sleep(30)
            continue
    data = json.loads(data)
    no_of_aircrafts = len(data['aircraft'])
    proxlist = []
    ind = 0
    line1 = "proximity: " + str(proximity) + "Km "
    line2 = "scanning..."
    for iter in range(no_of_aircrafts):
        if "lat" in data['aircraft'][iter]:
            # calculate distance
            lat1 = radians(data['aircraft'][iter]['lat'])
            lon1 = radians(data['aircraft'][iter]['lon'])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance = R * c
            # calculate miles
            miles = distance * conv_fac
            # if below proximity limit, put in list
            if distance < proximity:
                list = []
                list.append(distance)
                list.append(miles)
                list.append(iter)
                proxlist.append(list)
            # store farthest
            if distance > record:
                record = distance
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                if "flight" in data['aircraft'][iter]:
                    plane = data['aircraft'][iter]['flight']
                else:
                    plane = data['aircraft'][iter]['hex']
                if "alt_baro" in data['aircraft'][iter]:
                    altitude = str(data['aircraft'][iter]['alt_baro'])
                else:
                    altitude = "..."
                line3 = plane + " " + altitude + "Ft"
                line4 = str('%0.1fKm / %0.1fMi' %(distance,miles))
                line5 = dt_string
    # if list is not empty, choose the closer one
    if len(proxlist) > 0:
        proxlist.sort()
        ind = proxlist[0][2]
        if "flight" in data['aircraft'][ind]:
            plane = data['aircraft'][ind]['flight']
        else:
            plane = data['aircraft'][ind]['hex']
        if "alt_baro" in data['aircraft'][ind]:
            altitude = str(data['aircraft'][ind]['alt_baro'])
        else:
            altitude = "..."
        if altitude == "ground":
            line1 = plane + " " + altitude
        else:
            line1 = plane + " " + altitude + "Ft"
        line2 = str('%0.1fKm / %0.1fMi' %(proxlist[0][0],proxlist[0][1]))
    # print to display
    with canvas(device) as draw:
        w, h = draw.textsize(line1)
        draw.text(((width - w) / 2, top), line1, fill="white")
        w, h = draw.textsize(line2)
        draw.text(((width - w) / 2, top+10), line2, fill="white")
        draw.line((0, top+22, width, top+22), fill="white")
        w, h = draw.textsize(line3, font=font)
        draw.text(((width - w) / 2, offset), line3, font=font, fill="white")
        w, h = draw.textsize(line4, font=font)
        draw.text(((width - w) / 2, offset+12), line4, font=font, fill="white")
        w, h = draw.textsize(line5, font=font)
        draw.text(((width - w) / 2, offset+24), line5, font=font, fill="white")
    # wait few seconds
    time.sleep(5)
