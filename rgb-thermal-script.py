# This work is licensed under the MIT license.
# Copyright (c) 2013-2023 OpenMV LLC. All rights reserved.
# https://github.com/openmv/openmv/blob/master/LICENSE
#
# Thermal Overlay Demo
#
# This example shows off how to overlay a heatmap onto your OpenMV Cam's
# live video output from the main camera.

import sensor
import image
import time
import fir
import pyb
from pyb import RTC
import machine

rtc = RTC()

# or image.BILINEAR or 0 (nearest neighbor)
drawing_hint = image.BICUBIC | image.CENTER | image.SCALE_ASPECT_KEEP

ALT_OVERLAY = False  # Set to True to allocate a second ir image.

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.WQXGA2)
sensor.skip_frames(time=2000)

# Initialize the thermal sensor


# Allocate another frame buffer for smoother video.
extra_fb = sensor.alloc_extra_fb(sensor.width(), sensor.height(), sensor.RGB565)

# FPS clock
clock = time.clock()


def year(datetime):
    return str(datetime[0])
def month(datetime):
    return str('%02d' % datetime[1])
def day(datetime):
    return str('%02d' % datetime[2])
def hour(datetime):
    return str('%02d' % datetime[4])
def minute(datetime):
    return str('%02d' % datetime[5])
def second(datetime):
    return str('%02d' % datetime[6])
def timestamp(datetime):
    date_string = ''.join([year(datetime), month(datetime), day(datetime)])
    time_string = ''.join([hour(datetime), minute(datetime), second(datetime)])
    return "T".join([date_string, time_string])


while True:
    clock.tick()
    fir.init()

    time.sleep_ms(3000)

    # Capture an image
    img = sensor.snapshot()

    # Capture FIR data
    #   ta: Ambient temperature
    #   ir: Object temperatures (IR array)
    #   to_min: Minimum object temperature
    #   to_max: Maximum object temperature
    try:
        ta, ir, to_min, to_max = fir.read_ir()
    except OSError:
        continue

    #img = sensor.snapshot()
    print("save rgb")

    # Save the RGB image
    timestamp = timestamp(rtc.datetime())
    print(timestamp)
    img.save("rgb_" f"{timestamp}.jpg")


    with open("thermal_" f"{timestamp}.bin", "wb") as bin_file:
        for value in ir:
            value = value * 100
            bin_file.write(int(value).to_bytes(2, 'little'))


    fir.deinit()
    img.flush()

    rtc.wakeup(10000)

    machine.deepsleep()

    # Print FPS.
    #print(clock.fps())
    #print(time.localtime())
