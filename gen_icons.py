import os
from PIL import Image, ImageDraw, ImageFont

def create_start_icon():
    img = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Green rounded square background
    draw.rounded_rectangle((32, 32, 480, 480), radius=100, fill=(46, 204, 113))
    # White Play triangle
    draw.polygon([(200, 160), (200, 352), (360, 256)], fill=(255, 255, 255))
    img.save('/Users/frankvanlaarhoven/Desktop/dataminerAI/start_icon.png')

def create_stop_icon():
    img = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Red rounded square background
    draw.rounded_rectangle((32, 32, 480, 480), radius=100, fill=(231, 76, 60))
    # White Stop square
    draw.rectangle((180, 180, 332, 332), fill=(255, 255, 255))
    img.save('/Users/frankvanlaarhoven/Desktop/dataminerAI/stop_icon.png')

if __name__ == '__main__':
    create_start_icon()
    create_stop_icon()
