import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Raspberry Pi pin configuration:
RST = 24
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()
def clear():
    disp.clear()
    disp.display()
def print(line1,line2,line3) :
    
    # Make sure to create image with mode '1' for 1-bit color.
    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # First define some constants to allow easy resizing of shapes.
    padding = 2
    shape_width = 20
    top = padding
    bottom = height-padding

    # Move left to right keeping track of the current x position for drawing shapes.
    x = padding

    # Load default font.
    font = ImageFont.load_default()
    # abc = 'abcd'
    # line1 = "  Status  : "+abc
    # line2 = "  Status  : "+abc
    # line3 = "  Status  : "+abc
    # led.draw_text2(x-axis, y-axis, whatyouwanttoprint, size) < Understand?

    # Write two lines of text.
    draw.text((x, top),    line1, font=font, fill=255)
    draw.text((x, top+10), line2, font=font, fill=255)
    draw.text((x, top+20), line3, font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.display()