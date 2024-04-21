import time
import board
import digitalio

from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# Define the Reset Pin
oled_reset = digitalio.DigitalInOut(board.D4)

# Display Parameters
OLED_WIDTH = 128
OLED_HEIGHT = 64

# Use for I2C.
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, addr=0x3C, reset=oled_reset)

# Clear display.
oled.fill(0)
oled.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new('1', (OLED_WIDTH, OLED_HEIGHT))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, OLED_WIDTH,OLED_HEIGHT), outline=0, fill=0)

FONT_SIZE = 6

font = ImageFont.truetype('/home/username/oled-terminal-pyte/tiny.ttf', FONT_SIZE)

CHARS_HEIGHT = 10
CHARS_WIDTH = 32


def update_screen(lines, cursor_x, cursor_y):
    draw.rectangle((0, 0, OLED_WIDTH, OLED_HEIGHT), outline=0, fill=0)
    for line_num in range(len(lines)):
        line = lines[line_num]
        if cursor_y == line_num:
            before_cursor = line[:cursor_x]
            cursor_char = line[cursor_x]
            after_cursor = line[cursor_x + 1:]
            draw.text((0, line_num * (FONT_SIZE)), before_cursor, font=font, fill=255)
            (left, top, right, bottom) = draw.textbbox((font.getsize(before_cursor)[0], line_num * (FONT_SIZE)), cursor_char, font=font)
            draw.rectangle((left, top, right-1, bottom), fill=255)
            draw.text((font.getsize(before_cursor)[0], line_num * (FONT_SIZE)), cursor_char, font=font, fill=0)
            draw.text((font.getsize(before_cursor)[0] + font.getsize(cursor_char)[0], line_num * (FONT_SIZE)), after_cursor, font=font, fill=255)
        else:
            draw.text((0, line_num * (FONT_SIZE)), line, font=font, fill=255)

    oled.image(image)
    oled.show()
    

