segments1 = [[6, 7, 8], [9, 10, 11], [13, 14, 15], [16, 17, 18], [19, 20, 21], [3, 4, 5], [2, 1, 0]]
segments2 = [[38, 39, 40], [41, 42, 43], [25, 26, 27], [28, 29, 30], [31, 32, 33], [35, 36, 37], [44, 45, 46]]
seconds = [47, 48, 50, 51, 99, 100, 102, 103]
num_segments = [[1, 1, 1, 1, 1, 1, 0],
                [0, 1, 1, 0, 0, 0, 0],
                [1, 1, 0, 1, 1, 0, 1],
                [1, 1, 1, 1, 0, 0, 1],
                [0, 1, 1, 0, 0, 1, 1],
                [1, 0, 1, 1, 0, 1, 1],
                [1, 0, 1, 1, 1, 1, 1],
                [1, 1, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 0, 1, 1]]

from rpi_ws281x import Color
import time


def num_to_segments(i, index, color, strip):
    """
    :param strip: Led pásek

    :param color: barva ve formátu (red, green, blue)
    :type color: tuple

    :param index: číslo displeje 1 - 6
    :type index: int

    :param i: číslo
    :type i: int

    """
    segments = num_segments[i]
    if (index % 2) == 1:
        for a in range(7):
            if segments[a]:
                for led in segments1[a]:
                    led += (52 * ((index - 1) / 2))
                    led = int(led)
                    strip.setPixelColor(led, Color(color[led][0], color[led][1], color[led][2]))
            else:
                for led in segments1[a]:
                    led += (52 * ((index - 1) / 2))
                    led = int(led)
                    strip.setPixelColor(led, Color(0, 0, 0))
    else:
        for a in range(len(segments1)):
            if segments[a]:
                for led in segments2[a]:
                    led += (52 * ((index - 2) / 2))
                    led = int(led)
                    # print(led)
                    strip.setPixelColor(led, Color(color[led][0], color[led][1], color[led][2]))
            else:
                for led in segments2[a]:
                    led += (52 * ((index - 2) / 2))
                    led = int(led)
                    # print(led)
                    strip.setPixelColor(led, Color(0, 0, 0))


def light_seconds_indicator(status, color, strip):
    for led in seconds:
        if status:
            strip.setPixelColor(led, Color(color[led][0], color[led][1], color[led][2]))
        else:
            strip.setPixelColor(led, Color(0, 0, 0))
