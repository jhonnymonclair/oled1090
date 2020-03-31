# oled1090.py
Python script to display ADS-B data on Oled SSD1306
###
Oled1090.py is a Python script based on <b>LUMA Oled Library</b>, a nice piece of software that allows to write and draw
on SSD1306 and other Oled display models. For more info, read https://luma-oled.readthedocs.io/en/latest/
###
<b>SSD1306</b> is a 0,96 inch model, there are blue, white, yellow and yellow/blue versions available on the market,
it comes in two resolutions, 128x32 or 128x64 pixels, and two different kinds of interface, I2C or SPI.
On average the display uses about 20mA current, operating voltage from 3V to 5V.
You can find it on Amazon or Ebay for few dollars.
  
One of them was laying in my drawer, a left over of a previous project, so I thought to have some fun
with it and check if I could find some awesome purpose, that is how Oled1090 gets out.

Oled1090 reads Dump1090 data at intervals, if it finds an aircraft trespassing a preset proximity range then
sends info on upper part of display for as long as the aircraft flights in the area. At same time, it keeps trace of the
farthest received aircraft on the lower part of display.

Tipically the program is installed on the same Raspberry running Dump1090 but nothing prevents you from install
it on a different one, just take care to set the correct url in program according to that.   

Note: Oled1090 processes ADS-B data (no MLAT) and only for aicrafts transmitting identity and position (lat,lon)
because it relies just on the Aicraft.Json locally produced by Dump1090, there isn't any else involved database.

The following step-by-step guide has been written on the base of a Raspbian Buster Lite installation.
Different version of Raspbian may or may not satisfy all required dependencies.
If it fails, then something is missing.
To correct it, "sudo apt-get install" whatever dependency.

Wiring
-------

- Raspberry pin 1 > Display VCC 3v
- Raspberry pin 3 > Display SDA
- Raspberry pin 5 > Display SCL
- Raspberry pin 9 or pin 14 > Display GND


Enable I2C interface
-------

```
sudo raspi-config
```
- Use the down arrow to select 5 Interfacing Options
- Arrow down to I2C
- Select yes when it asks you to enable I2C
- Also select yes if it asks about automatically loading the kernel module
- Use the right arrow to select the <Finish> button
- Select yes when it asks to reboot.


Detecting device memory address
-------
(most of times the default address is 3C, so you can skip this step and eventually inspect later if doesn't work)

- install i2c-tools:
```
sudo apt-get install -y i2c-tools
i2cdetect -y 1
```
the detected address must match the address of code line in program:
```
serial = i2c(port=1, address=0x3C)
```


Install LUMA Oled Library
-------

```
sudo apt-get update
sudo apt-get install python3-pil
sudo apt-get install python3-pip
sudo -H pip3 install --upgrade luma.oled
```


Install the program
-------

- copy the repository: 
```
git clone https://github.com/jhonnymonclair/oled1090.git
cd oled1090
```
- enable system to start the program at boot:
```
sudo cp oled1090.service /lib/systemd/system
sudo systemctl enable oled1090.service
```


configuring the program
-------

- edit the program:
```
nano oled1090.py
```
- set the correct Url to dump1090 Aircraft.json:

example for a dump1090-mutability running on the same machine
 ```
 http://127.0.0.1/dump1090-mutability/data/aircraft.json
 ```
example for a dump1090-fa running on a machine on the same subnet
```
http://192.168.1.100/dump1090-fa/data/aircraft.json
```
- replace coordinates in brackets with yours
```
lat2 = radians(MyLatitude)
lon2 = radians(MyLongitude)
```
- set a proximity range in Km and replace the value
```
proximity = 20
```
- save the changes (Ctrl-X) 
- reboot

