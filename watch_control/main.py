from datetime import datetime
import time
from rpi_ws281x import Adafruit_NeoPixel, Color
from watch_control.segments import num_to_segments, light_seconds_indicator
from PiAnalog import PiAnalog
from watch_control.colors import rainbow3, rainbow, red
import threading
import yaml
import json
import os
import builtins

debug = False

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


strip.setBrightness(100)
strip.show()

brightness = "auto"

f = open("config.yml")
file = f.read()
config = yaml.safe_load(file)
brightness = config['brightness']

sensor = PiAnalog()
sensor.C = config['analog'][0]
sensor.R1 = config['analog'][1]
sensor.a_pin = 24
# for x in range(0, LED_COUNT):
#    strip.setPixelColor(x, Color(255, 0, 0))
color = None

if config['theme'] == "rainbow_snake":
    color = rainbow
elif config['theme'] == "rainbow":
    color = rainbow3
elif config['theme'] == "custom":
    color = red
    colors = config["colors"]
    leds = [[126,151],[104,126],[99,104],[77,99],[52,74],[47,52],[25,47],[0,22]]
    for index in range(8):
        for led in range(leds[index][0], leds[index][1]):
            color[led] = [int(colors[index][0]), int(colors[index][1]), int(colors[index][2])]



def tprint(*objs, **kwargs):
    my_prefix = "[WatchControl]"
    builtins.print(my_prefix, *objs, **kwargs)

class WatchControl(threading.Thread):
    def __init__(self, queueWC2WS, queueWS2WC, debugLocal):
        self.queueWS2WC = queueWS2WC
        self.queueWC2WS = queueWC2WS
        global debug
        debug = debugLocal
        super().__init__()
        self.daemon = True

    def run(self):
        print("[WatchControl] Starting!")
        threading.Thread(target=backlight_update).start()
        self.main()

    def main(self):
        global color
        light_seconds_indicator(True, color, strip)
        num_to_segments(8, 1, color, strip)
        num_to_segments(8, 2, color, strip)
        num_to_segments(8, 3, color, strip)
        num_to_segments(8, 4, color, strip)
        num_to_segments(8, 5, color, strip)
        num_to_segments(8, 6, color, strip)
        strip.show()
        time.sleep(5)

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
            
            if len(self.queueWS2WC) != 0:
                msg = self.queueWS2WC[0][0:3]
                data = self.queueWS2WC[0][4:]
                
                if msg == "scb":
                    global brightness
                    brightness = data
                    self.queueWS2WC.pop(0)
                    with open("./config.yml", 'w') as f:
                        config['brightness'] = brightness
                        f.write(yaml.safe_dump(config))
                
                if msg == 'gcb':
                    self.queueWS2WC.pop(0)
                    self.queueWC2WS.append(f"gcb {brightness}")
                
                if msg == 'gcc':
                    self.queueWS2WC.pop(0)
                    self.queueWC2WS.append(f"gcc {json.dumps(color)}")

                if msg == 'std':
                    self.queueWS2WC.pop(0)
                    tprint(f"Shutting down")
                    for x in range(0, LED_COUNT):
                        strip.setPixelColor(x, Color(0, 0, 0))
                    strip.show()
                    os.system("systemctl poweroff")
                    break

                if msg == 'rst':
                    self.queueWS2WC.pop(0)
                    tprint(f"Rebooting")
                    for x in range(0, LED_COUNT):
                        strip.setPixelColor(x, Color(0, 0, 0))
                    strip.show()
                    os.system("systemctl reboot")
                    break

                if msg == "sct":
                    tprint(f"Setting color mode to {data}")
                    self.queueWS2WC.pop(0)
                    if data == "rainbow":
                        color = rainbow3
                        with open("./config.yml", 'w') as f:
                            config['theme'] = "rainbow"
                            f.write(yaml.safe_dump(config))
                    if data == "rainbow_snake":
                        color = rainbow
                        with open("./config.yml", 'w') as f:
                            config['theme'] = "rainbow_snake"
                            f.write(yaml.safe_dump(config))
                    if data == "custom":
                        color = red
                        colors = config["colors"]
                        leds = [[126,151],[104,126],[99,104],[77,99],[52,74],[47,52],[25,47],[0,22]]
                        for index in range(8):
                            for led in range(leds[index][0], leds[index][1]):
                                color[led] = [int(colors[index][0]), int(colors[index][1]), int(colors[index][2])]

                        with open("./config.yml", 'w') as f:
                            config['theme'] = "custom"
                            f.write(yaml.safe_dump(config))
                
                if msg == "scc":
                    self.queueWS2WC.pop(0)
                    with open("./config.yml", 'w') as f:
                        config['colors'] = json.loads(data)
                        tprint("Setting colors")
                        f.write(yaml.safe_dump(config))
                        
                        colors = config["colors"]
                        leds = [[126,151],[104,126],[99,104],[77,99],[52,74],[47,52],[25,47],[0,22]]
                        for index in range(8):
                            for led in range(leds[index][0], leds[index][1]):
                                color[led] = [int(colors[index][0]), int(colors[index][1]), int(colors[index][2])]
                                    
                if msg == "gct":
                    self.queueWS2WC.pop(0)
                    tprint(f"Returning current theme {config['theme']}")
                    self.queueWC2WS.append(f"gct {config['theme']}")
                
                if msg == "gtc":
                    self.queueWS2WC.pop(0)
                    tprint(f"Returning current theme colors {config['colors']}")
                    self.queueWC2WS.append(f"gtc {json.dumps(config['colors'])}")
            time.sleep(0.02)
        

def backlight_update():
    lastjas = 0
    while True:
        if brightness == "auto":
            if debug:
                print(f"Sensor: {sensor.read_resistance()*config['analog'][2]}")

            jas = 20000 - (sensor.read_resistance()*config['analog'][2])
            jas = jas / 200
            if jas < 1:
                jas = 1
            if jas > 255:
                jas = 255
            #jas = (jas + lastjas)/2
            if debug:
                print(f"Jas: {jas}")

            strip.setBrightness(int(jas))
            strip.show()
            lastjas = jas
            time.sleep(0.05)
        else:
            strip.setBrightness(int(brightness))
            strip.show()
            time.sleep(0.1)

def int_to_str(i):
    if i < 10:
        return f"0{i}"
    else:
        return str(i)



