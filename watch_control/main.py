from datetime import datetime
import time
from rpi_ws281x import Adafruit_NeoPixel
from segments import num_to_segments, light_seconds_indicator
from PiAnalog import PiAnalog
from colors import rainbow3
import asyncio
loop = asyncio.get_event_loop()

# LED strip configuration:
LED_COUNT = 300  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

sensor = PiAnalog()
sensor.C = 0.1
sensor.R1 = 330
sensor.a_pin = 24
# for x in range(0, LED_COUNT):
#    strip.setPixelColor(x, Color(255, 0, 0))
color = rainbow3

strip.setBrightness(100)
strip.show()

light_seconds_indicator(True, color, strip)
num_to_segments(8, 1, color, strip)
num_to_segments(8, 2, color, strip)
num_to_segments(8, 3, color, strip)
num_to_segments(8, 4, color, strip)
num_to_segments(8, 5, color, strip)
num_to_segments(8, 6, color, strip)
strip.show()
time.sleep(5)


async def main():
    lastnow = None
    sekundovnik = False
    while True:
        now = datetime.now()
        if (now.microsecond / 1000) > 500:
            if sekundovnik is not False:
                sekundovnik = False
                light_seconds_indicator(sekundovnik, color, strip)
                strip.show()
        else:
            if sekundovnik is not True:
                sekundovnik = True
                light_seconds_indicator(sekundovnik, color, strip)
                strip.show()

        if lastnow != now.second:
            print(jas)
            hodina = str(int_to_str(now.hour))
            num_to_segments(int(hodina[0]), 6, color, strip)
            num_to_segments(int(hodina[1]), 5, color, strip)

            minuta = str(int_to_str(now.minute))
            num_to_segments(int(minuta[0]), 4, color, strip)
            num_to_segments(int(minuta[1]), 3, color, strip)

            sekunda = str(int_to_str(now.second))
            num_to_segments(int(sekunda[0]), 2, color, strip)
            num_to_segments(int(sekunda[1]), 1, color, strip)
            strip.show()
            lastnow = now.second
        

async def backlight_update():
    lastjas = 0
    while True:
        jas = 20000 - sensor.read_resistance()
        jas = jas / 200
        if jas < 1:
            jas = 1
        if jas > 255:
            jas = 255
        jas = (jas + lastjas)/2
        strip.setBrightness(int(jas))
        strip.show()
        lastjas = jas
        await asyncio.sleep(0.02)
        
loop.create_task(backlight_update())
loop.create_task(main())

def int_to_str(i):
    if i < 10:
        return f"0{i}"
    else:
        return str(i)


import threading


class WatchControl(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        print("[WatchControl] Starting!")
        main()

loop.run_forever()
